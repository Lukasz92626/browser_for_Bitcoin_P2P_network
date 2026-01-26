import socket
import logging
import socket

from commands.addr import Addr
from commands.getblocks import getblocks_message
from commands.getheaders import getheaders_message, get_msg_fields
from commands.headers import Headers
from commands.inv import Inv
from commands.verack import verack_header
from commands.version import get_version
from mode import Mode
from utils import checksum_f, bytes_to_int, bytes_to_str, \
    bytes_to_hex_str, str_to_hex, count_payload
from commands.addr_utils import is_sensible_addr, print_addr



class Communication:
    def __init__(self, NODE, MODE = Mode.IDLE):
        self.node = NODE
        self.logger = logging.getLogger('bitcoin')
        self.MODE = MODE
        self.addr = Addr()
        self.inv = Inv()
        self.headers = Headers()

    def get_mode(self):
        return self.MODE

    def set_mode(self, MODE):
        self.MODE = MODE

    def set_node(self, NODE):
        self.node = NODE

    def disconnect(self, client):
        client.close()
        print("Connection closed...: ")

    def connect(self) -> socket.socket:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.node.host_v4, self.node.port))
        print("Connection established: ")
        return client

    def connect_until_success(self, max_tries=20, timeout=3):
        for _ in range(max_tries):
            node = self.addr.draw()
            if node is None or node.host_v4 is None or node.host_v6 is None:
                continue

            self.node = node
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(timeout)

            try:
                client.connect((self.node.host_v4, self.node.port))
                print(f"Connected to {self.node}")
                client.settimeout(10)

                return client
            except OSError as e:
                print(f"Failed to connect to {self.node}: {e}")
                client.close()

        return None

    def send_version(self, client) -> None:
        version = bytes.fromhex(get_version(self.node))
        client.send(version)
        print("Version sent: ")
        self.logger.debug("+++++++++++++++++++++++++++++++++++++++++ Send version +++++++++++++++++++++++++++++++++++++++++\n")
        print(version)

    def read_version(self, client) -> None:
        try:
            magic_bytes = client.recv(4)
            command = client.recv(12)
            size = client.recv(4)
            checksum = client.recv(4)

            size_dec = bytes_to_int(size, False)
            payload = client.recv(size_dec)

            self.logger.debug("======================================= Read version =============================================\n")
            self.logger.debug("magic_bytes: " + str(magic_bytes.hex()) + "\n")
            self.logger.debug("command: " + bytes_to_str(command) + "\n")
            self.logger.debug("size: " + str(size_dec) + "\n")
            self.logger.debug("checksum: " + bytes_to_hex_str(checksum) + "\n")
            self.logger.debug("payload: " + bytes_to_hex_str(payload) + "\n")
        except socket.timeout:
            print("Node nie odpowiedział w czasie 10 sekund.")

    def read_verack(self, client) -> None:
        magic_bytes = client.recv(4)
        command = client.recv(12)
        size = client.recv(4)
        checksum = client.recv(4)

        self.logger.debug("======================================= Read verack =============================================\n")
        self.logger.debug("magic_bytes: " + str(magic_bytes.hex()) + "\n")
        self.logger.debug("command: " + bytes_to_str(command) + "\n")
        self.logger.debug("size: " + str(bytes_to_int(size, False)) + "\n")
        self.logger.debug("checksum: " + bytes_to_hex_str(checksum) + "\n")
        # payload = client.recv(size_dec)
        # print(str(payload))

    def send_verack(self, client) -> None:
        verack = bytes.fromhex(verack_header)
        client.send(verack)
        self.logger.debug("======================================= Send verack =============================================\n")
        self.logger.debug("verack: " + str(verack) + "\n")

    def read_in_loop(self, client) -> None:
        magic_bytes = 'f9beb4d9'
        while self.MODE is not Mode.EXIT:
            buffer = ''
            while True:
                byte = client.recv(1)
                if byte == b'\x00':
                    print("Read null byte from the socket.")
                    return
                buffer += byte.hex()

                if len(buffer) == 8: # 8 hex chars == 4 bytes
                    if buffer == 'f9beb4d9':
                        command = client.recv(12)
                        size = client.recv(4)
                        checksum = client.recv(4)

                        command_dec = bytes_to_str(command)
                        size_dec = bytes_to_int(size, False)
                        payload = client.recv(size_dec)
                        payload_hex = bytes_to_hex_str(payload)

                        self.logger.debug("======================================= any command =============================================\n")
                        self.logger.debug("command: " + command_dec + "\n")
                        self.logger.debug("size: " + str(size_dec) + "\n")
                        self.logger.debug("checksum: " + bytes_to_hex_str(checksum) + "\n")
                        self.logger.debug("payload: " + payload_hex + "\n")

                        if command_dec == "ping":
                            self.logger.info("Ping command received.")
                            command = "pong"

                            command_hex = str_to_hex(command, 12)
                            size = count_payload(payload_hex, 4)
                            checksum = checksum_f(payload_hex)
                            self.logger.info(command_hex + "\n")
                            message = magic_bytes + command_hex + size + checksum + payload_hex

                            client.send(bytes.fromhex(message))
                            self.logger.info("Answering with command pong.")

                        if self.MODE is Mode.GETADDR:
                            self.MODE = Mode.IDLE
                            command = 'getaddr'

                            command_hex = str_to_hex(command, 12)
                            size = count_payload(payload_hex, 4)
                            checksum = checksum_f(payload.hex())
                            message = magic_bytes + command_hex + size + checksum + payload_hex

                            client.send(bytes.fromhex(message))
                            self.logger.debug("+++++++++++++++++++++++++++++++++++++++++ getaddr +++++++++++++++++++++++++++++++++++++++++\n")
                            self.logger.info("getaddr: asking for information about known active peers.")

                        if command_dec == "addr":
                            self.MODE = Mode.IDLE
                            a_list = self.addr.unpack_addresses(payload_hex)
                            self.addr.save(a_list)

                            #for addr in a_list:
                            #    print(addr)

                            printed = set()

                            for addr in a_list:
                                if not is_sensible_addr(addr):
                                    continue

                                key = (addr.ip, addr.port)
                                if key in printed:
                                    continue

                                printed.add(key)
                                print_addr(addr)



                        if command_dec == "inv":
                            command = "inv"

                            command_hex = str_to_hex(command, 12)
                            size = count_payload(payload_hex, 4)
                            checksum = checksum_f(payload_hex)

                            self.inv.unpack_transactions(payload_hex)

                            self.logger.debug("======================================= inv =============================================\n")
                            self.logger.debug("command: " + command + "\n")
                            self.logger.debug("size: " + str(size) + "\n")
                            self.logger.debug("checksum: " + str(checksum) + "\n")
                            self.logger.debug("payload: " + payload_hex + "\n")
                            # command = "getdata"
                            # command_hex = str_to_hex(command, 12)
                            # inv_vector_list = self.inv.unpack_transactions(payload_hex)
                            # if not inv_vector_list:
                            #     print("Brak transakcji w inv_vector_list")
                            #     continue
                            # while True:
                            #     inv_vector = random.choice(inv_vector_list)
                            #     if inv_vector.name == "MSG_TX":
                            #         payload_hex = "01" + inv_vector.hash
                            #         break
                            # size = count_payload(payload_hex, 4)
                            # checksum = checksum_f(payload_hex)
                            #
                            # self.logger.debug("======================================= getdata =============================================\n")
                            # self.logger.debug("command: " + command + "\n")
                            # self.logger.debug("size: " + str(size) + "\n")
                            # self.logger.debug("checksum: " + str(checksum) + "\n")
                            # self.logger.debug("payload: " + payload_hex + "\n")
                            #
                            # # odpowiedz dowolnym getdata zeby node nie rozlaczal
                            # message = magic_bytes + command_hex + size + checksum + payload_hex
                            # self.logger.debug("spraawdzenie: " + str(bytes.fromhex(message)))
                            # client.send(bytes.fromhex(message))

                        if self.MODE is Mode.GETDATA_TX:
                            self.MODE = Mode.IDLE
                            command = "getdata"
                            command_hex = str_to_hex(command, 12)
                            payload_hex = "01" + self.inv.transaction.hash # jedna transakcja dlatego 01 varint
                            size = count_payload(payload_hex, 4)
                            checksum = checksum_f(payload_hex)

                            self.logger.debug("+++++++++++++++++++++++++++++++++++++++++ getdata tx +++++++++++++++++++++++++++++++++++++++++\n")
                            self.logger.debug("command: " + command + "\n")
                            self.logger.debug("size: " + str(size) + "\n")
                            self.logger.debug("checksum: " + str(checksum) + "\n")
                            self.logger.debug("payload: " + payload_hex + "\n")

                            message = magic_bytes + command_hex + size + checksum + payload_hex
                            client.send(bytes.fromhex(message))

                        if self.MODE is Mode.GETDATA_BLOCK:
                            self.MODE = Mode.IDLE
                            command = "getdata"
                            command_hex = str_to_hex(command, 12)
                            payload_hex = "02" + self.headers.last_block_hash # jeden blok (ostatni) dlatego 02 varint
                            size = count_payload(payload_hex, 4)
                            checksum = checksum_f(payload_hex)

                            self.logger.debug("+++++++++++++++++++++++++++++++++++++++++ getdata block +++++++++++++++++++++++++++++++++++++++++\n")
                            self.logger.debug("command: " + command + "\n")
                            self.logger.debug("size: " + str(size) + "\n")
                            self.logger.debug("checksum: " + str(checksum) + "\n")
                            self.logger.debug("payload: " + payload_hex + "\n")

                            message = magic_bytes + command_hex + size + checksum + payload_hex
                            client.send(bytes.fromhex(message))

                        if self.MODE is Mode.GETHEADERS:
                            self.MODE = Mode.IDLE
                            client.send(bytes.fromhex(getheaders_message))
                            fields = get_msg_fields()

                            self.logger.debug("+++++++++++++++++++++++++++++++++++++++++ getheaders +++++++++++++++++++++++++++++++++++++++++\n")
                            self.logger.debug("command: getheaders\n")
                            self.logger.debug("size: " + str(fields[1]) + "\n")
                            self.logger.debug("checksum: " + str(fields[2]) + "\n")
                            self.logger.debug("payload: " + fields[3] + "\n")

                        if self.MODE is Mode.GETBLOCKS:
                            self.MODE = Mode.IDLE
                            client.send(bytes.fromhex(getblocks_message))
                            fields = get_msg_fields()

                            self.logger.debug("+++++++++++++++++++++++++++++++++++++++++ getblocks +++++++++++++++++++++++++++++++++++++++++\n")
                            self.logger.debug("command: getblocks\n")
                            self.logger.debug("size: " + str(fields[1]) + "\n")
                            self.logger.debug("checksum: " + str(fields[2]) + "\n")
                            self.logger.debug("payload: " + fields[3] + "\n")

                        if command_dec == "headers":
                            command = "headers"

                            command_hex = str_to_hex(command, 12)
                            size = count_payload(payload_hex, 4)
                            checksum = checksum_f(payload_hex)
                            self.headers.unpack_block_headers(payload_hex)

                            self.logger.debug("======================================= headers =======================================\n")
                            self.logger.debug("command: " + command + "\n")
                            self.logger.debug("size: " + str(size) + "\n")
                            self.logger.debug("checksum: " + str(checksum) + "\n")
                            self.logger.debug("payload: " + payload_hex + "\n")
                        break

                    buffer = ''