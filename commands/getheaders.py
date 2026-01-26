from utils import int_to_byte_str, str_to_hex, count_payload, checksum_f, reverse_hex, append_zeros_right

genesis_hash_hex = reverse_hex("000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f")

p_ver = int_to_byte_str(70014, 4)
hash_count = "01"
block_locator_hashes = genesis_hash_hex
hash_stop = append_zeros_right("00", 32)

payload = p_ver + hash_count + block_locator_hashes + hash_stop

# message header
m_bytes = 'f9beb4d9'  # magic bytes
c = "getheaders"
command = str_to_hex(c, 12)
size = count_payload(payload, 4)
checksum = checksum_f(payload)

def get_msg_fields():
    return [command, size, checksum, payload]

header = m_bytes + command + size + checksum

getheaders_message = header + payload

if __name__ == '__main__':
    h = '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'
    res = reverse_hex(h)
    # print(bytes.fromhex(getheaders_message))
    print(p_ver)
