import asyncio
import socket
from messages import build_version_message, build_verack_message, parse_message, build_getaddr_message

class PeerDB:
    """Prosta baza peerów"""
    def __init__(self):
        self.peers = {}  # {ip: port}

    def add_peer(self, ip, port):
        self.peers[ip] = port

    def list_peers(self):
        return [(ip, port) for ip, port in self.peers.items()]

peer_db = PeerDB()

# Funkcja: rozwiązywanie DNS
def dns_seed_lookup(seed_host):
    """Zwraca listę IPv4 z domeny seed"""
    try:
        infos = socket.getaddrinfo(seed_host, 8333, socket.AF_INET, socket.SOCK_STREAM)
        ips = [info[4][0] for info in infos]
        return list(set(ips))
    except Exception as e:
        print("Błąd DNS lookup:", e)
        return []

# Funkcja: getaddr od pojedynczego peer
async def getaddr_from_peer(ip, port=8333, timeout=10):
    try:
        reader, writer = await asyncio.open_connection(ip, port)
        # Wysyłamy handshake: version + verack
        writer.write(build_version_message(addr_recv_ip=ip, addr_recv_port=port))
        await writer.drain()

        buf = b""
        got_verack = False
        got_version = False
        deadline = asyncio.get_event_loop().time() + timeout

        # Reader loop: handshake
        while asyncio.get_event_loop().time() < deadline and (not got_verack or not got_version):
            data = await reader.read(4096)
            if not data:
                break
            buf += data
            while True:
                cmd, payload, buf = parse_message(buf)
                if cmd is None:
                    break
                if cmd == "version":
                    writer.write(build_verack_message())
                    await writer.drain()
                    got_version = True
                elif cmd == "verack":
                    got_verack = True

        if not (got_version and got_verack):
            print(f"Handshake failed with {ip}")
            writer.close()
            await writer.wait_closed()
            return []

        # Wysyłamy getaddr
        writer.write(build_getaddr_message())
        await writer.drain()

        addr_list = []
        deadline2 = asyncio.get_event_loop().time() + timeout
        buf2 = b""
        while asyncio.get_event_loop().time() < deadline2:
            data = await reader.read(4096)
            if not data:
                break
            buf2 += data
            while True:
                cmd, payload, buf2 = parse_message(buf2)
                if cmd is None:
                    break
                if cmd == "addr":
                    # payload zawiera listę peerów
                    # Prostą metodą odczytujemy IP i porty
                    for i in range(0, len(payload), 30):  # 30 bajtów per addr
                        ip_bytes = payload[i+12:i+28][-4:]  # ostatnie 4 bajty IPv4
                        port_bytes = payload[i+28:i+30]
                        ip_str = ".".join(str(b) for b in ip_bytes)
                        port_int = int.from_bytes(port_bytes, "big")
                        addr_list.append((ip_str, port_int))
                        peer_db.add_peer(ip_str, port_int)
        writer.close()
        await writer.wait_closed()
        return addr_list
    except Exception as e:
        print(f"Błąd przy peerze {ip}: {e}")
        return []

# Funkcja: odkrywanie peerów
async def discover_peers(seed_host):
    ips = dns_seed_lookup(seed_host)
    print(f"DNS seed {seed_host} → {ips}")
    tasks = [getaddr_from_peer(ip) for ip in ips]
    results = await asyncio.gather(*tasks)
    # Flatten
    all_peers = [p for sublist in results for p in sublist]
    print(f"Znaleziono {len(all_peers)} peerów:")
    for ip, port in all_peers:
        print(f"{ip}:{port}")
    return all_peers

# Przykładowe uruchomienie
if __name__ == "__main__":
    seed = "seed.bitcoin.sipa.be"
    asyncio.run(discover_peers(seed))
