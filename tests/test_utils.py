from messages import varint, sha256d
import hashlib

def test_varint_small():
    assert varint(10) == b'\x0a'

def test_varint_16bit():
    assert varint(0xfd)[:1] == b'\xfd'

def test_sha256d():
    d = sha256d(b"hello")
    # porównamy z dwukrotnym hashlib.sha256
    h = hashlib.sha256(hashlib.sha256(b"hello").digest()).digest()
    assert d == h
