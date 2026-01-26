import time
import constants as cons

from utils import append_zeros_right, reverse_hex, del_colons, del_0x, checksum_f, str_to_hex, int_to_byte_str, \
    count_payload

def get_version(node):
    p_ver = int_to_byte_str(70014, 4)  # protocol version
    serv = int_to_byte_str(0, 8)  # services
    t = int(time.time())
    time_ = int_to_byte_str(t, 8)  # time
    r_serv = int_to_byte_str(0, 8)  # remote services
    remote_ip = del_colons(node.host_v6)  # remote ip
    r_port = del_0x(hex(int(node.port)))  # remote port
    l_serv = int_to_byte_str(0, 8)  # local services
    l_ip = del_colons(cons.local.get("LOCALHOST_V6"))  # local ip
    l_port = del_0x(hex(int(cons.local.get("PORT"))))  # local port
    nonce = int_to_byte_str(0, 8)  # nonce
    compact = "00"  # user agent
    last_block = int_to_byte_str(0, 4)  # remote services

    payload = p_ver + serv + time_ + r_serv + remote_ip + r_port + l_serv + l_ip + l_port + nonce + compact + last_block

    # message header
    m_bytes = 'f9beb4d9'  # magic bytes
    c = "version"
    command = str_to_hex(c, 12)
    size = count_payload(payload, 4)
    checksum = checksum_f(payload)

    header = m_bytes + command + size + checksum

    # combined
    version_message = header + payload
    return version_message

if __name__ == '__main__':
    print(time)
