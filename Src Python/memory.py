from Singleton import Singleton


class Memory(metaclass=Singleton):
    memory = bytearray(0x10000)
    ppu_memory = bytearray(0x10000)
    object_attribute_memory = bytearray(0x100)
      
    def __init__(self):
        for i in range(len(self.memory)):
            self.memory[i] = 0

    def load_data(self, data, mapper, offset):
        if data[0] == 0x4E:
            if mapper == 0:
                if data[0x4] == 0x1:
                    for i in range(0, 0x4000):
                        self.memory[i + 0xC000] = data[i + 0x10]
                    for i in range(0, 0x4000):
                        self.memory[i + 0x8000] = data[i + 0x10]
                    for i in range(0, 0x2000):
                        self.ppu_memory[i] = data[i + 0x4010]
                elif data[0x4] == 0x2:
                    for i in range(0, 0x4000):
                        self.memory[i + 0x8000] = data[i + 0x10]
                    for i in range(0, 0x4000):
                        self.memory[i + 0xc000] = data[i + 0x4000]
                    for i in range(0, 0x2000):
                        self.ppu_memory[i] = data[i + 0x8000]
            else:
                print("mapper not implemented")
        else:
            for i in range(len(data)):
                self.memory[i + offset] = data[i]
