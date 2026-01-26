import json
import random
from datetime import datetime

from constants import BYTE_IN_CHARS
import logging
import logging_config
from ipaddress import IPv6Address, ip_address

from node import Node
from utils import bytes_to_int, hex_str_to_int


class Address:
    def __init__(self, data):
        a_tuple = self.unpack(data)
        self.timestamp = a_tuple[0]
        self.services = a_tuple[1]
        self.ip = a_tuple[2]
        self.port = a_tuple[3]

    def __str__(self):
        return ("timestamp: " + str(self.timestamp) + "\nservices: " + str(self.services) +
                "\nip: " + str(self.ip) + "\nport: " + str(self.port) + "\n")

    def unpack(self, data):
        timestamp = data[0:4 * BYTE_IN_CHARS]
        services = data[4 * BYTE_IN_CHARS:12 * BYTE_IN_CHARS]
        ip = data[12 * BYTE_IN_CHARS:28 * BYTE_IN_CHARS]
        port = data[28 * BYTE_IN_CHARS:30 * BYTE_IN_CHARS]

        t = datetime.fromtimestamp(hex_str_to_int(timestamp))
        ip = ip_address(int(ip, 16))
        port = bytes_to_int(bytes.fromhex(port), True)
        return [t, services, ip, port]

    def to_dict(self):
        return {
            'timestamp': str(self.timestamp),
            'services': self.services,
            'ip': str(self.ip),
            'port': self.port
        }

class Addr:
    def __init__(self):
        self.logger = logging.getLogger('bitcoin')

    def unpack_addresses(self, data):
        varint = str(data)[:2]
        self.logger.info("varint: " + str(varint) + "\n")
        address_amount = 1 * BYTE_IN_CHARS
        if varint == "fd":
            address_amount = 3 * BYTE_IN_CHARS
        elif varint == "fe":
            address_amount = 5 * BYTE_IN_CHARS
        elif varint == "ff":
            address_amount = 9 * BYTE_IN_CHARS
        else:
            address_amount = 1 * BYTE_IN_CHARS
        address_list = str(data)[address_amount:]
        addresses = [address_list[i:i + 30 * BYTE_IN_CHARS] for i in range(0, len(address_list), 30 * BYTE_IN_CHARS)]
        a_list = []
        for address in addresses:
            a_list.append(Address(address))
        return sorted(a_list, key=lambda x: x.timestamp, reverse=True)

    def save(self, a_list):
        with open("addresses.json", "w") as f:
            json.dump([a.to_dict() for a in a_list], f, indent=2)

    def draw(self):
        with open("addresses.json", "r") as f:
            addresses = json.load(f)
        addresses_8333 = [a for a in addresses if a["port"] == 8333]
        if not addresses_8333:
            return None

        # chosen = random.choice(addresses_8333[:min(50, len(addresses_8333))])
        chosen = random.choice(addresses_8333)


        return self.dict_to_node(chosen)

    def dict_to_node(self, addr_dict):
        ipv6 = addr_dict["ip"]
        ipv6_obj = IPv6Address(ipv6)

        if ipv6_obj.ipv4_mapped:
            ipv4 = str(ipv6_obj.ipv4_mapped)
        else:
            ipv4 = None

        return Node(
            host_v4=ipv4,
            host_v6=ipv6,
            port=addr_dict["port"]
        )


if __name__ == '__main__':
    s = 'e803123043690904000000000000260040404770590079d466778820402c2'
    addr = Address(s)
    print(str(addr))
