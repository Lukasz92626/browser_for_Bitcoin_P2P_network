import asyncio
from typing import Dict, Tuple
from messages import build_version_message, build_getaddr_message, build_inv_message, build_getdata_message
from messages import build_version_message, build_verack_message, parse_message
from messages import build_ping_message, build_pong_message
from messages import build_alert_message, build_message_message, build_reject_message
from messages import build_tx_message, build_block_message
from messages import build_getblocks_message, build_getheaders_message


class Peer:
    def __init__(self, host: str, port: int, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.host = host
        self.port = port
        self.reader = reader
        self.writer = writer

class P2PManager:
    def __init__(self):
        self.peers: Dict[Tuple[str,int], Peer] = {}

    async def _open(self, host: str, port: int) -> Peer:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            peer = Peer(host, port, reader, writer)
            self.peers[(host,port)] = peer
            print(f"Połączono z {host}:{port}")
            # uruchom task do czytania wiadomości od tego peera
            asyncio.create_task(self._reader_loop(peer))
            return peer
        except Exception as e:
            print(f"Błąd połączenia z {host}:{port}: {e}")
            return None

    def connect(self, host: str, port: int):
        return self._open(host, port)

    async def _reader_loop(self, peer: Peer):
        try:
            buf = b""
            while True:
                data = await peer.reader.read(4096)
                if not data:
                    print(f"Rozłączono: {peer.host}:{peer.port}")
                    del self.peers[(peer.host, peer.port)]
                    break

                buf += data

                while True:
                    try:
                        cmd, payload, buf = parse_message(buf)
                    except Exception as e:
                        print("Błąd parsowania:", e)
                        break

                    if cmd is None:
                        break

                    print(f"[{peer.host}:{peer.port}] → {cmd}")

                    if cmd == "ping":
                        # payload = 8-bajtowy nonce w little endian
                        nonce = int.from_bytes(payload, "little")
                        pong = build_pong_message(nonce)
                        peer.writer.write(pong)
                        await peer.writer.drain()
                        print("↪ wysłano pong")

                    elif cmd == "pong":
                        print("↪ otrzymano pong")

        except Exception as e:
            print("Błąd w reader_loop:", e)

    def print_peers(self):
        if not self.peers:
            print("Brak połączeń.")
            return
        print("Lista połączonych peerów:")
        for (h,p) in self.peers.keys():
            print(f" - {h}:{p}")

    async def _send_to_all(self, payload: bytes):
        if not self.peers:
            print("Brak peerów do wysłania.")
            return
        for peer in list(self.peers.values()):
            try:
                peer.writer.write(payload)
                await peer.writer.drain()
                print(f"Wysłano {len(payload)} bajtów do {peer.host}:{peer.port}")
            except Exception as e:
                print("Błąd wysyłania:", e)

    def send_version(self):
        msg = build_version_message()
        return self._send_to_all(msg)

    def send_getaddr(self):
        msg = build_getaddr_message()
        return self._send_to_all(msg)

    def send_inv(self, kind: str, h: str):
        msg = build_inv_message(kind, h)
        return self._send_to_all(msg)

    def send_getdata(self, kind: str, h: str):
        msg = build_getdata_message(kind, h)
        return self._send_to_all(msg)

    def send_ping(self):
        msg = build_ping_message()
        return self._send_to_all(msg)

    def send_alert(self, text: str):
        msg = build_alert_message(text)
        return self._send_to_all(msg)

    def send_message(self, text: str):
        msg = build_message_message(text)
        return self._send_to_all(msg)

    def send_reject(self, cmd: str, reason: str):
        msg = build_reject_message(cmd, reason)
        return self._send_to_all(msg)

    def send_tx(self, raw_tx_hex: str):
        return self._send_to_all(build_tx_message(raw_tx_hex))

    def send_block(self, raw_block_hex: str):
        return self._send_to_all(build_block_message(raw_block_hex))

    def send_getblocks(self, locator_hashes: list[str]):
        return self._send_to_all(build_getblocks_message(locator_hashes))

    def send_getheaders(self, locator_hashes: list[str]):
        return self._send_to_all(build_getheaders_message(locator_hashes))


async def handshake(host, port, timeout=10):
    reader, writer = await asyncio.open_connection(host, port)
    # wyślij version
    writer.write(build_version_message(addr_recv_ip=host, addr_recv_port=port))
    await writer.drain()

    buf = b""
    deadline = asyncio.get_event_loop().time() + timeout
    got_verack = False
    got_version = False

    while asyncio.get_event_loop().time() < deadline and (not got_verack or not got_version):
        data = await reader.read(4096)
        if not data:
            break
        buf += data
        while True:
            cmd, payload, buf = parse_message(buf)
            if cmd is None:
                break
            print("Otrzymano:", cmd)
            if cmd == "version":
                writer.write(build_verack_message())
                await writer.drain()
                got_version = True
            elif cmd == "verack":
                got_verack = True

    return got_version and got_verack
