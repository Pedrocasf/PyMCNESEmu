class Memory:
    memory = bytearray(0x10000)

    def __init__(self):
        for i in range(len(self.memory)):
            self.memory[i] = 0

    def load_data(self, data, offset, banks, offset_data):
        for i in range(0, bank):
            self.memory[i + offset] = data[i + offset_data]

    def write_to_address(self, data, address ):
        self.memory[address] = data