from utils import append_zeros_right, reverse_hex, del_colons, del_0x, str_to_hex

# verack
# message header
m_bytes = 'f9beb4d9' # magic bytes
c = "verack"
command = str_to_hex(c, 12)
size = append_zeros_right(reverse_hex(hex(0)), 4)
checksum = "5DF6E0E2"

verack_header = m_bytes + command + size + checksum

if __name__ == '__main__':
    print(verack_header)