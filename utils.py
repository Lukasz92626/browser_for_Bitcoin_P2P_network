import hashlib
from datetime import datetime
import numpy as np

# pads the hex string with trailing zeros up to a specified length, taking the existing digits into account
def append_zeros_right(hex_str, length):
    return str.ljust(hex_str, length*2, "0")

def del_0x(hex_str):
    return hex_str.replace("0x", "")

def del_x00(hex_str):
    return hex_str.replace("\x00", "")

# def del_b_and_apos(hex_str): # deletes b'' from bytes string

# reverse hex number and returns string
def reverse_hex(hex_str):
    b = del_0x(hex_str)[::-1]
    if len(b) % 2 == 1:
        b += '0'
    list2d = hex_string_to_2d_list(b)
    np_arr = np.array(list2d)
    list2d = np_arr.flatten()
    return "".join(list2d)

def hex_string_to_2d_list(b) -> list[list[int]]:
    len_b = int(len(b) / 2)
    list2d = [[0] * 2 for i in range(len_b)]
    m = 0
    n = 1
    for i in range(len(b)):
        list2d[m][n] = b[i]
        if i % 2 == 1:
            m += 1
            n = 1
        else:
            n -= 1
    return list2d

def del_colons(IPv6: str):
    return IPv6.replace(':', '')

def checksum_f(hex_str: str): # f - oznacza ze to funkcja, dla odroznienia od checksum
    data = bytes.fromhex(hex_str)
    hash1 = hashlib.sha256(data).digest()
    hash2 = hashlib.sha256(hash1).hexdigest()
    return hash2[:8]

# metoda oblicza rozmiar payload
def count_payload(hex_str, length):
    return append_zeros_right(reverse_hex(hex(int(len(hex_str) / 2))), length)

# metoda zamieniajaca napis hex, na int
def hex_str_to_int(hex_str):
    return int(reverse_hex(hex_str), 16)

# metoda zamieniajaca ciag bajtow na napis, ciag hex
# uzywana dla: payload
def bytes_to_hex_str(bytes_chain):
    return bytes_chain.hex()

# metoda zamieniajaca napis hex na ciag bajtow
# parametry( napis: hex, dlugosc ciagu bajtow: int)
# uzywana dla: size
def hex_str_to_bytes(hex_str, length, is_big_endian=False):
    if is_big_endian:
        return append_zeros_right(hex_str, length)
    else:
        return append_zeros_right(reverse_hex(hex_str), length)

# metoda zamieniajaca ciag bajtow na int
# uzywana dla: size
def bytes_to_int(bytes_chain, is_big_endian):
    if is_big_endian:
        return int.from_bytes(bytes_chain, 'big')
    else:
        return int.from_bytes(bytes_chain, 'little')

# metoda zamieniajaca ciag bajtow na napis
# uzywana dla: command
def bytes_to_str(bytes_chain):
    return del_x00(bytes_chain.decode('utf-8'))

# metoda zamieniajaca napis na ciag hex
# parametry( napis: str, dlugosc ciagu : int)
# uzywana dla: command
def str_to_hex(s, length):
    return append_zeros_right(s.encode("utf-8").hex(), length)

# metoda zamieniajaca int na string bajtow little-endian
# parametry( numer: int, dlugosc ciagu bajtow: int)
def int_to_byte_str(number, length):
    return append_zeros_right(reverse_hex(hex(number)), length)

# metoda zamieniajaca int na ciag bajtow o danej dlugosci
# uzywana dla: size

if __name__ == '__main__':
    h = '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'
    res = reverse_hex(h)

