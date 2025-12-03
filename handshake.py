import asyncio
import socket
from messages import build_version_message, build_verack_message, parse_message

async def handshake(host, port, timeout=10):

    # 1. Rozwiąż DNS na adres IPv4
    ip = socket.gethostbyname(host)
    print("Połączenie z:", host, "→", ip)

    # 2. Łączymy się po IPv4
    reader, writer = await asyncio.open_connection(ip, port)

    writer.write(build_version_message(addr_recv_ip=ip, addr_recv_port=port))
    await writer.drain()

    buf = b""
    got_verack = False
    got_version = False
    deadline = asyncio.get_event_loop().time() + timeout

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

    writer.close()
    await writer.wait_closed()

    return got_version and got_verack


if __name__ == "__main__":
    ok = asyncio.run(handshake("seed.bitcoin.sipa.be", 8333))
    print("Handshake OK?", ok)
