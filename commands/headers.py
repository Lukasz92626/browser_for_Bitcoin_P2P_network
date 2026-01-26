import logging

from constants import BYTE_IN_CHARS

class Headers:
    def __init__(self):
        self.logger = logging.getLogger('bitcoin')
        self.last_block_hash = None

    def unpack_block_headers(self, data):
        varint = str(data)[:2]
        self.logger.info("varint: " + str(varint) + "\n")
        block_headers_amount = 1 * BYTE_IN_CHARS
        if varint == "fd":
            block_headers_amount = 3 * BYTE_IN_CHARS
        elif varint == "fe":
            block_headers_amount = 5 * BYTE_IN_CHARS
        elif varint == "ff":
            block_headers_amount = 9 * BYTE_IN_CHARS
        else:
            block_headers_amount = 1 * BYTE_IN_CHARS
        block_headers_list = str(data)[block_headers_amount:]

        block_headers = []
        for i in range(0, len(block_headers_list), 81 * BYTE_IN_CHARS):
            header_81 = block_headers_list[i:i + 81 * BYTE_IN_CHARS]
            header_80 = header_81[:80 * BYTE_IN_CHARS]  # ostatni bajt zawsze 0 odcinamy
            block_headers.append(header_80)
        self.last_block_hash = block_headers[-1]
        print(self.last_block_hash + "\n")