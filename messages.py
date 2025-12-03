import time
import struct
import hashlib
import os

#  Utilsy

def sha256d(b: bytes) -> bytes:
    """Double SHA256."""
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()

def varint(n: int) -> bytes:
    """Bitcoin varint serializer."""
    if n < 0xfd:
        return struct.pack("B", n)
    elif n <= 0xffff:
        return b'\xfd' + struct.pack("<H", n)
    elif n <= 0xffffffff:
        return b'\xfe' + struct.pack("<I", n)
    else:
        return b'\xff' + struct.pack("<Q", n)

def ipv6_from_ipv4(ip: str) -> bytes:
    """Bitcoin stores IPv4 as IPv6-mapped."""
    parts = ip.split('.')
    return b"\x00" * 10 + b"\xff\xff" + bytes([int(x) for x in parts])

#  Nagłówek Bitcoin

def bitcoin_message(command: str, payload: bytes, testnet=False) -> bytes:
    """
    Buduje pełny nagłówek wiadomości Bitcoin P2P.
    mainnet magic: F9 BE B4 D9
    testnet magic: 0B 11 09 07
    """
    magic = 0xD9B4BEF9 if not testnet else 0x0B110907
    magic_bytes = struct.pack("<I", magic)

    command_bytes = command.encode("ascii") + b"\x00" * (12 - len(command))
    payload_len = struct.pack("<I", len(payload))
    checksum = sha256d(payload)[:4]

    return magic_bytes + command_bytes + payload_len + checksum + payload

#  Serializacja adresów (version message)

def serialize_netaddr(services: int, ip: str, port: int) -> bytes:
    """
    NetAddr structure w Bitcoin:
      8 bytes services
      16 bytes IPv6
      2 bytes port (big endian!!)
    """
    return (
        struct.pack("<Q", services) +
        ipv6_from_ipv4(ip) +
        struct.pack(">H", port)
    )

#  Wiadomości Bitcoin

def build_version_message(
    addr_recv_ip="127.0.0.1",
    addr_recv_port=8333,
    addr_from_ip="0.0.0.0",
    addr_from_port=8333,
    services=0,
    relay=True,
    start_height=0,
    user_agent=b"/BitLab:0.1/"
):
    """
    Pełny version message zgodnie z Bitcoin protocol.
    """
    version = 70015
    timestamp = int(time.time())
    nonce = struct.unpack("<Q", os.urandom(8))[0]

    payload = b""
    payload += struct.pack("<i", version)
    payload += struct.pack("<Q", services)
    payload += struct.pack("<q", timestamp)

    # addr_recv
    payload += serialize_netaddr(services, addr_recv_ip, addr_recv_port)

    # addr_from
    payload += serialize_netaddr(services, addr_from_ip, addr_from_port)

    # nonce
    payload += struct.pack("<Q", nonce)

    # user agent (varstr)
    payload += varint(len(user_agent)) + user_agent

    # start height
    payload += struct.pack("<i", start_height)

    # relay flag
    payload += struct.pack("B", 1 if relay else 0)

    return bitcoin_message("version", payload)


def build_verack_message():
    """Very small, empty payload."""
    return bitcoin_message("verack", b"")


def build_getaddr_message():
    """getaddr ma pusty payload."""
    return bitcoin_message("getaddr", b"")


#  Inventory / GetData

INV_TYPE = {
    "tx": 1,
    "block": 2,
    "filtered_block": 3,
    "cmpct_block": 4,
}

def build_inv_message(kind: str, obj_hash_hex: str):
    typ = INV_TYPE.get(kind, 1)
    obj_hash = bytes.fromhex(obj_hash_hex)[::-1]  # Bitcoin uses LE hash order

    payload = b""
    payload += varint(1)  # jedno ogłoszenie
    payload += struct.pack("<I", typ)
    payload += obj_hash

    return bitcoin_message("inv", payload)


def build_getdata_message(kind: str, obj_hash_hex: str):
    typ = INV_TYPE.get(kind, 1)
    obj_hash = bytes.fromhex(obj_hash_hex)[::-1]

    payload = b""
    payload += varint(1)
    payload += struct.pack("<I", typ)
    payload += obj_hash

    return bitcoin_message("getdata", payload)

#  Ping / Pong

def build_ping_message():
    nonce = struct.unpack("<Q", os.urandom(8))[0]
    payload = struct.pack("<Q", nonce)
    return bitcoin_message("ping", payload)

def build_pong_message(nonce: int):
    payload = struct.pack("<Q", nonce)
    return bitcoin_message("pong", payload)

def parse_message(stream_bytes: bytes, testnet=False):
    """
    Próbuje wyciągnąć jedną pełną wiadomość z bufora stream_bytes.
    Zwraca: (cmd, payload, remaining_bytes)
    Jeśli nie ma pełnej wiadomości, zwraca (None, None, stream_bytes).
    """
    HEADER_LEN = 24
    if len(stream_bytes) < HEADER_LEN:
        return None, None, stream_bytes

    magic_expected = 0x0B110907 if testnet else 0xD9B4BEF9
    magic = int.from_bytes(stream_bytes[0:4], "little")
    if magic != magic_expected:
        raise ValueError(f"Wrong magic: {hex(magic)}")

    command_raw = stream_bytes[4:16]
    command = command_raw.split(b"\x00", 1)[0].decode("ascii")

    payload_len = int.from_bytes(stream_bytes[16:20], "little")
    checksum = stream_bytes[20:24]

    total_len = HEADER_LEN + payload_len
    if len(stream_bytes) < total_len:
        return None, None, stream_bytes

    payload = stream_bytes[24:24 + payload_len]

    from hashlib import sha256
    import hashlib
    from messages import sha256d

    if sha256d(payload)[:4] != checksum:
        raise ValueError("Checksum mismatch")

    remaining = stream_bytes[total_len:]
    return command, payload, remaining

#  ALERT / MESSAGE / REJECT

def build_message_message(text: str):
    """
    Wyślij prosty komunikat diagnostyczny (typ message)
    Payload = UTF-8 string
    """
    payload = text.encode("utf-8")
    return bitcoin_message("message", payload)


def build_alert_message(text: str):
    """
    Historyczna alert message. Payload może być dowolnym tekstem.
    W oryginale alert miał podpisy kryptograficzne, ale do BitLaba nie trzeba.
    """
    payload = text.encode("utf-8")
    return bitcoin_message("alert", payload)


def build_reject_message(command: str, reason: str, code: int = 0x10):
    """
    reject message:
        varstr command
        code (1 bajt)
        varstr reason
    """

    cmd_bytes = command.encode("ascii")
    reason_bytes = reason.encode("utf-8")

    payload = b""
    payload += varint(len(cmd_bytes)) + cmd_bytes
    payload += bytes([code])
    payload += varint(len(reason_bytes)) + reason_bytes

    return bitcoin_message("reject", payload)

#  BLOCKCHAIN / HEADERS / TX

def build_tx_message(raw_tx_hex: str):
    """
    TX message zawiera raw transaction (w formacie Bitcoin)
    Zakładamy, że user podaje hex-transakcji
    """
    payload = bytes.fromhex(raw_tx_hex)
    return bitcoin_message("tx", payload)


def build_block_message(raw_block_hex: str):
    """
    Block message — pełny blok w hex
    """
    payload = bytes.fromhex(raw_block_hex)
    return bitcoin_message("block", payload)


def build_getblocks_message(locator_hashes: list[str], stop_hash: str = "00"*32):
    """
    getblocks:
      version (4b)
      varint count of locator hashes
      32B locator hashes (LE)
      stop hash (LE)
    """
    payload = struct.pack("<I", 70015)
    payload += varint(len(locator_hashes))

    for h in locator_hashes:
        payload += bytes.fromhex(h)[::-1]

    payload += bytes.fromhex(stop_hash)[::-1]
    return bitcoin_message("getblocks", payload)


def build_getheaders_message(locator_hashes: list[str], stop_hash: str = "00"*32):
    payload = struct.pack("<I", 70015)
    payload += varint(len(locator_hashes))

    for h in locator_hashes:
        payload += bytes.fromhex(h)[::-1]

    payload += bytes.fromhex(stop_hash)[::-1]
    return bitcoin_message("getheaders", payload)


def build_headers_message(headers: list[bytes]):
    """
    headers message: lista nagłówków bloków
    tutaj payload = varint + list of 80B headers + tx count (always 0)
    """
    payload = varint(len(headers))
    for h in headers:
        payload += h + b"\x00"  # 0 transakcji
    return bitcoin_message("headers", payload)
