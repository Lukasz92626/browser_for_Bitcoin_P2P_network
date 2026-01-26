from constants import BYTE_IN_CHARS
import logging

class InvVector:
    def __init__(self, data):
        inv_vector_tuple = self.unpack(data)
        self.name = inv_vector_tuple[0]
        self.hash = inv_vector_tuple[1]

    def __str__(self):
        return "name: " + self.name + " inv_vector: " + str(self.hash) + "\n"

    def unpack(self, data):
        uint32_t = str(data)[:4*BYTE_IN_CHARS]
        if uint32_t == "00000000":
            name = "ERROR"
            return [name, data]
        elif uint32_t == "01000000":
            name = "MSG_TX"
            return [name, data]
        elif uint32_t == "02000000":
            name = "MSG_BLOCK"
            return [name, data]
        elif uint32_t == "03000000":
            name = "MSG_FILTERED_BLOCK"
            return [name, data]
        elif uint32_t == "04000000":
            name = "MSG_CMPCT_BLOCK"
            return [name, data]
        elif uint32_t == "01000040":
            name = "MSG_WITNESS_TX"
            return [name, data]
        elif uint32_t == "02000040":
            name = "MSG_WITNESS_BLOCK"
            return [name, data]
        elif uint32_t == "03000040":
            name = "MSG_FILTERED_WITNESS_BLOCK"
            return [name, data]
        print("something went wrong! inv.py:36")
        return None


class Inv:
    def __init__(self):
        self.logger = logging.getLogger('bitcoin')
        self.transaction: InvVector | None = None

    def unpack_transactions(self, data):
        varint = str(data)[:2]
        self.logger.info("varint: " + str(varint) + "\n")
        inv_vectors_amount = 1 * BYTE_IN_CHARS
        if varint == "fd":
            inv_vectors_amount = 3 * BYTE_IN_CHARS
        elif varint == "fe":
            inv_vectors_amount = 5 * BYTE_IN_CHARS
        elif varint == "ff":
            inv_vectors_amount = 9 * BYTE_IN_CHARS
        else:
            inv_vectors_amount = 1 * BYTE_IN_CHARS
        inv_vectors_list = str(data)[inv_vectors_amount:]
        inv_vectors = [inv_vectors_list[i:i + 36 * BYTE_IN_CHARS] for i in range(0, len(inv_vectors_list), 36 * BYTE_IN_CHARS)]
        inv_vector_list = []
        for inv_vector in inv_vectors:
            inv_vector_list.append(InvVector(inv_vector))
        for inv_vector in inv_vector_list:
            if inv_vector.name == "MSG_TX":
                self.transaction = inv_vector
                break
        return inv_vector_list
