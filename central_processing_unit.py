from main_memory import Memory


class CPU:
    accumulator = 0x00
    x = 0x00
    y = 0x00
    stack_pointer = 0x01FD
    program_counter = 0xC000
    cycle_count = 0
    processor_status = 0b00100100

    def value_zero_negative(self, value):
        if value == 0:
            self.processor_status = self.processor_status | 0b00000010
        else:
            self.processor_status = self.processor_status & 0b11111101
        if (value & 0b10000000) == 0b10000000:
            self.processor_status = self.processor_status | 0b10000000
        else:
            self.processor_status = self.processor_status & 0b01111111

    def branch(self):
        if Memory.memory[self.program_counter + 1] & 0b10000000 != 0:
            self.program_counter -= (~(Memory.memory[self.program_counter + 1]) & 0b01111111)
        else:
            self.program_counter += ((Memory.memory[self.program_counter + 1]) + 2)

    def i(self):
        self.program_counter += 2
        return Memory.memory[self.program_counter - 1]

    def d(self):
        self.program_counter +=2
        return Memory.memory[Memory.memory[self.program_counter - 1]]

    def dx(self):
        self.program_counter += 2
        return Memory.memory[Memory.memory[self.program_counter - 1] + self.x]

    def zdy(self):
        self.program_counter += 2
        return Memory.memory[Memory.memory[self.program_counter - 1] + self.y]

    def a(self):
        self.program_counter += 3
        return (Memory.memory[self.program_counter - 1] << 8) | Memory.memory[self.program_counter - 2]

    def ax(self):
        self.program_counter += 3
        return ((Memory.memory[self.program_counter - 1] << 8) | Memory.memory[self.program_counter - 2]) + self.x

    def ay(self):
        self.program_counter += 3
        return ((Memory.memory[self.program_counter - 1] << 8) | Memory.memory[self.program_counter - 2]) + self.y

    def ia(self):
        self.program_counter += 3
        lsb = (Memory.memory[self.program_counter - 1] << 8) | Memory.memory[self.program_counter - 2]
        return (Memory.memory[lsb + 1] << 8 | Memory.memory[lsb])

    def idx(self):
        lsb = (Memory.memory[self.program_counter + 1] + self.x)
        if (lsb + 1) > 0xff:
            address = (Memory.memory[lsb - 0xff] << 8) | Memory.memory[lsb]
        elif lsb > 0xfF:
            address = (Memory.memory[lsb - 0xff] << 8) | Memory.memory[lsb-0xff]
        else:
            address = (Memory.memory[lsb + 1] << 8) | Memory.memory[lsb]
        return address

    def dy(self):
        address = ((Memory.memory[self.program_counter + 1] + 1 << 8) | Memory.memory[self.program_counter + 1]) + self.y
        return address


    def ADC(self, address):
        if (self.accumulator +address) & 0b10000000 == 0b10000000 and (self.accumulator & 0b10000000) == 0b00000000 and (address & 0b10000000) == 0b00000000:
            self.processor_status = self.processor_status | 0b01000000
        else:
            self.processor_status = self.processor_status & 0b10111111
        self.accumulator = self.accumulator + address + (self.processor_status & 0b00000001)
        if self.accumulator > 0xFF:
            self.processor_status = self.processor_status | 0b00000001
        else:
            self.processor_status = self.processor_status & 0b11111110
        self.accumulator = self.accumulator & 0x00FF
        self.value_zero_negative(self.accumulator)

    def AND(self, address):
        self.accumulator = self.accumulator & address
        self.value_zero_negative(self.accumulator)

    def ASl(self, address):
        if (address & 0b10000000) == 0b10000000:
            self.processor_status = self.processor_status | 0b00000001
        else:
            self.processor_status = self.processor_status & 0b11111110
        self.accumulator = address << 1
        if self.accumulator > 0b11111111:
            self.accumulator = 0
        self.value_zero_negative(self.accumulator)

    def BCC(self):
        if self.processor_status & 0b00000001 == 0b00000000:
            self.branch()
        else:
            self.program_counter += 2

    def BCS(self):
        if (self.processor_status & 0b00000001) == 0b00000001:
            self.branch()
        else:
            self.program_counter += 2

    def BEQ(self):
        if self.processor_status & 0b00000010 == 0b00000010:
            self.branch()
        else:
            self.program_counter += 2

    def BIT(self, address):
        if address & 0b01000000 == 0b01000000:
            self.processor_status = self.processor_status | 0b01000000
        else:
            self.processor_status = self.processor_status & 0b10111111
        if address & 0b10000000 == 0b10000000:
            self.processor_status = self.processor_status | 0b10000000
        else:
            self.processor_status = self.processor_status & 0b01111111
        if self.accumulator & address == 0:
            self.processor_status = self.processor_status | 0b00000010
        else:
            self.processor_status = self.processor_status & 0b11111101

    def BMI(self):
        if self.processor_status & 0b10000000 == 0b10000000:
            self.branch()
        else:
            self.program_counter += 2

    def BNE(self):
        if self.processor_status & 0b00000010 == 0b00000000:
            self.branch()
        else:
            self.program_counter += 2

    def BPL(self):
        if self.processor_status & 0b10000000 == 0b00000000:
            self.branch()
        else:
            self.program_counter += 2

    def BRK(self):
        self.program_counter = ((Memory.memory[0XFFFF] << 8) | Memory.memory[0XFFFE])
        self.processor_status = self.processor_status | 0b00110100

    def BVC(self):
        if self.processor_status & 0b01000000 == 0b00000000:
            self.branch()
        else:
            self.program_counter += 2

    def BVS(self):
        if self.processor_status & 0b01000000 == 0b01000000:
            self.branch()
        else:
            self.program_counter += 2

    def CLC(self):
        self.processor_status = self.processor_status & 0b11111110
        self.program_counter += 1

    def CLD(self):
        self.processor_status = self.processor_status & 0b11110111
        self.program_counter += 1

    def CLI(self):
        self.processor_status = self.processor_status & 0b11111011
        self.program_counter += 1

    def CLV(self):
        self.processor_status = self.processor_status & 0b10111111
        self.program_counter += 1

    def CMP(self, register: object, address: object):
        if register >= address:
            self.processor_status = self.processor_status | 0b00000001
        else:
            self.processor_status = self.processor_status & 0b11111110
        if register == address:
            self.processor_status = self.processor_status | 0b00000010
        else:
            self.processor_status = self.processor_status & 0b11111101
        if (register - address) & 0b10000000 == 0b10000000:
            self.processor_status = self.processor_status | 0b10000000
        else:
            self.processor_status = self.processor_status & 0b01111111

    def DEC(self, value):
        if value == 0:
            value = ~value & 0b011111111
        else:
            value -= 1
        self.value_zero_negative(value)
        self.program_counter += 1

    def EOR(self, address):
        self.accumulator = self.accumulator ^ address
        self.value_zero_negative(self.accumulator)
        self.program_counter += 2

    def IN(self, address):
        address += 1
        self.value_zero_negative(address)

    def JMP(self, address):
        self.program_counter = address

    def LD(self, register, address):
        register = address
        self.value_zero_negative(register)

    def LSR(self, value):
        if (value & 0b00000001) == 0b00000001:
            self.processor_status = self.processor_status | 0b00000001
        else:
            self.processor_status = self.processor_status & 0b11111110
        value = value >> 1
        self.value_zero_negative(value)
        self.program_counter += 1

    def NOP(self):
        self.program_counter += 1

    def ORA(self, address):
        self.accumulator = self.accumulator | address
        self.value_zero_negative(self.accumulator)

    def PHA(self):
        Memory.memory[self.stack_pointer] = self.accumulator
        self.stack_pointer -= 1
        self.program_counter += 1

    def PHP(self):
        Memory.memory[self.stack_pointer] = self.processor_status | 0b00110000
        self.stack_pointer -= 1
        self.program_counter += 1

    def PLA(self):
        self.stack_pointer += 1
        self.accumulator = Memory.memory[self.stack_pointer]
        self.value_zero_negative(self.accumulator)
        self.program_counter += 1

    def PLP(self):
        self.stack_pointer += 1
        self.processor_status = (Memory.memory[self.stack_pointer] & 0b11101111) | 0b00100000
        self.program_counter += 1

    def ROL(self, address):
        if address & 0b10000000 == 0b10000000:
            self.processor_status = self.processor_status | 0b100000000
        else:
            self.processor_status = self.processor_status & 0b011111111
        address = ((address << 1) | (self.processor_status & 0b100000000) >> 8) & 0x00FF
        if self.processor_status & 0b100000000 == 0b100000000:
            self.processor_status = (self.processor_status | ((self.processor_status & 0b100000000) >> 8) & 0x00FF)
        else:
            self.processor_status = self.processor_status & (self.processor_status & 0b011111110)
        self.value_zero_negative(address)

    def ROR(self, address):
        address = address | ((self.processor_status & 0b00000001) << 8)
        if (self.accumulator & 0b1) == 0b1:
            self.processor_status = self.processor_status | 0b1
        else:
            self.processor_status = self.processor_status & 0b11111110
        address = address >> 1
        self.value_zero_negative(address)

    def RTI(self):
        self.stack_pointer += 1
        self.processor_status = Memory.memory[self.stack_pointer] | 0b00100000
        self.stack_pointer += 2
        self.program_counter += 1

    def RTS(self):
        self.stack_pointer += 2
        self.program_counter = ((Memory.memory[self.stack_pointer] << 8) | Memory.memory[self.stack_pointer - 1]) + 1

    def SBC(self, address):
        if (self.accumulator - address) - (1 - (self.processor_status & 0b00000001)) & 0b10000000 == 0b00000000 and self.accumulator & 0b10000000 == 0b10000000 and ~address & 0b10000000 == 0b10000000:
            self.processor_status = self.processor_status | 0b01000000
        elif ~(self.accumulator - address) & 0b10000000 == 0b10000000 and (~self.accumulator & 0b10000000 == 0b00000000 and ~address & 0b10000000 == 0b00000000):
            self.processor_status = self.processor_status | 0b01000000
        else:
            self.processor_status = self.processor_status & 0b10111111
        self.accumulator = self.accumulator - address - (1 - (self.processor_status & 0b00000001))
        if self.accumulator & 0b10000000 == 0b10000000:
            self.processor_status = self.processor_status & 0b11111110
        else:
            self.processor_status = self.processor_status | 0b00000001
        self.accumulator = self.accumulator & 0x00FF

    def SEC(self):
        self.processor_status = self.processor_status | 0b00000001
        self.program_counter += 1

    def SED(self):
        self.processor_status = self.processor_status | 0b00001000
        self.program_counter += 1

    def SEI(self):
        self.processor_status = self.processor_status | 0b00000100
        self.program_counter += 1

    def ST(self, register, address):
        if register < 0:
            register *= -1
        address = register

    def T(self, register_source, register_destination):
        register_destination = register_source
        self.value_zero_negative(register_destination)




    def __init__(self):

        self.opcode_table = {0x00:, 0x01:, 0x02:, 0x03:, 0x04:, 0x05:, 0x06:, 0x07:, 0x08:, 0x09:, 0x0A:, 0x0B:, 0x0C:, 0x0D:, 0x0E:, 0x0F:
                            ,0x10:, 0x11:, 0x12:, 0x13:, 0x14:, 0x15:, 0x16:, 0x17:, 0x18:, 0x19:, 0x1A:, 0x1B:, 0x1C:, 0x1D:, 0x1E:, 0x1F:
                            ,0x20:, 0x21:, 0x22:, 0x23:, 0x24:, 0x25:, 0x26:, 0x27:, 0x28:, 0x29:, 0x2A:, 0x2B:, 0x2C:, 0x2D:, 0x2E:, 0x2F:
                            ,0x30:, 0x31:, 0x32:, 0x33:, 0x34:, 0x35:, 0x36:, 0x37:, 0x38:, 0x39:, 0x3A:, 0x3B:, 0x3C:, 0x3D:, 0x3E:, 0x3F:
                            ,0x40:, 0x41:, 0x42:, 0x43:, 0x44:, 0x45:, 0x46:, 0x47:, 0x48:, 0x49:, 0x4A:, 0x4B:, 0x4C:, 0x4D:, 0x4E:, 0x4F:
                            ,0x50:, 0x51:, 0x52:, 0x53:, 0x54:, 0x55:, 0x56:, 0x57:, 0x58:, 0x59:, 0x5A:, 0x5B:, 0x5C:, 0x5D:, 0x5E:, 0x5F:
                            ,0x60:, 0x61:, 0x62:, 0x63:, 0x64:, 0x65:, 0x66:, 0x67:, 0x68:, 0x69:, 0x6A:, 0x6B:, 0x6C:, 0x6D:, 0x6E:, 0x6F:
                            ,0x70:, 0x71:, 0x72:, 0x73:, 0x74:, 0x75:, 0x76:, 0x77:, 0x78:, 0x79:, 0x7A:, 0x7B:, 0x7C:, 0x7D:, 0x7E:, 0x7F:
                            ,0x80:, 0x81:, 0x82:, 0x83:, 0x84:, 0x85:, 0x86:, 0x87:, 0x88:, 0x89:, 0x8A:, 0x8B:, 0x8C:, 0x8D:, 0x8E:, 0x8F:
                            ,0x90:, 0x91:, 0x92:, 0x93:, 0x94:, 0x95:, 0x96:, 0x97:, 0x98:, 0x99:, 0x9A:, 0x9B:, 0x9C:, 0x9D:, 0x9E:, 0x9F:
                            ,0xA0:, 0xA1:, 0xA2:, 0xA3:, 0xA4:, 0xA5:, 0xA6:, 0xA7:, 0xA8:, 0xA9:, 0xAA:, 0xAB:, 0xAC:, 0xAD:, 0xAE:, 0xAF:
                            ,0xB0:, 0xB1:, 0xB2:, 0xB3:, 0xB4:, 0xB5:, 0xB6:, 0xB7:, 0xB8:, 0xB9:, 0xBA:, 0xBB:, 0xBC:, 0xBD:, 0xBE:, 0xBF:
                            ,0xC0:, 0xC1:, 0xC2:, 0xC3:, 0xC4:, 0xC5:, 0xC6:, 0xC7:, 0xC8:, 0xC9:, 0xCA:, 0xCB:, 0xCC:, 0xCD:, 0xCE:, 0xCF:
                            ,0xD0:, 0xD1:, 0xD2:, 0xD3:, 0xD4:, 0xD5:, 0xD6:, 0xD7:, 0xD8:, 0xD9:, 0xDA:, 0xDB:, 0xDC:, 0xDD:, 0xDE:, 0xDF:
                            ,0xE0:, 0xE1:, 0xE2:, 0xE3:, 0xE4:, 0xE5:, 0xE6:, 0xE7:, 0xE8:, 0xE9:, 0xEA:, 0xEB:, 0xEC:, 0xED:, 0xEE:, 0xEF:
                            ,0xF0:, 0xF1:, 0xF2:, 0xF3:, 0xF4:, 0xF5:, 0xF6:, 0xF7:, 0xF8:, 0xF9:, 0xFA:, 0xFB:, 0xFC:, 0xFD:, 0xFE:, 0xFF:}
