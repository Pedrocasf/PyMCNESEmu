include "main_memory.pyx"
from threading import Thread


class CPU(Thread):
    accumulator = 0x00
    x = 0x00
    y = 0x00
    stack_pointer = 0x01FD
    program_counter = 0
    cycle_count = 0
    processor_status = 0b00100100

    # misc functions

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
            self.program_counter -= (~(Memory.memory[self.program_counter + 1]) & 0b01111111) - 1
        else:
            self.program_counter += ((Memory.memory[self.program_counter + 1]) + 2)



   # index modes

    def immediate(self):
        self.program_counter += 2
        return self.program_counter - 1

    def zero_page(self):
        self.program_counter += 2
        return Memory.memory[self.program_counter - 1]

    def zero_page_x(self):
        self.program_counter += 2
        return (Memory.memory[self.program_counter - 1] + self.x) & 0x0FF

    def zero_page_y(self):
        self.program_counter += 2
        return (Memory.memory[self.program_counter - 1] + self.y) & 0x0FF

    def absolute(self):
        self.program_counter += 3
        address = ((Memory.memory[self.program_counter - 1] << 8) | Memory.memory[self.program_counter - 2])
        return address & 0xFFFF

    def absolute_x(self):
        self.program_counter += 3
        address = ((Memory.memory[self.program_counter - 1] << 8) | Memory.memory[self.program_counter - 2]) + self.x
        return address & 0xFFFF

    def absolute_y(self):
        self.program_counter += 3
        address = ((Memory.memory[self.program_counter - 1] << 8) | Memory.memory[self.program_counter - 2]) + self.y
        return address & 0xFFFF

    def indirect(self):
        self.program_counter += 3
        lsb = (Memory.memory[self.program_counter - 1] << 8) | Memory.memory[self.program_counter - 2]
        if (lsb & 0x0FF) == 0xFF:
            address = (Memory.memory[lsb -0xFF] << 8) | Memory.memory[lsb]
        else:
            address = (Memory.memory[lsb + 1] << 8) | Memory.memory[lsb]
        return address & 0xFFFF

    def indexed_indirect(self):
        self.program_counter += 2
        lsb = (Memory.memory[self.program_counter - 1] + self.x) & 0x0FF
        if lsb == 0xff:
            address = (Memory.memory[lsb - 0xff] << 8) | Memory.memory[lsb]
        else:
            address = (Memory.memory[lsb + 1] << 8) | Memory.memory[lsb]
        return address & 0xFFFF

    def indirect_indexed(self):
        self.program_counter += 2
        lsb = Memory.memory[self.program_counter - 1] & 0xFF
        if lsb == 0xFF:
            address = ((Memory.memory[lsb - 0xff] << 8) | Memory.memory[lsb]) + self.y
        else:
            address = ((Memory.memory[lsb + 1] << 8) | Memory.memory[lsb]) + self.y
        return address & 0xFFFF

    #documented opcodes

    def ADC(self, address):
        if (self.accumulator + Memory.memory[address]) & 0b10000000 == 0b10000000 and (self.accumulator & 0b10000000) == 0b00000000 and (Memory.memory[address] & 0b10000000) == 0b00000000:
            self.processor_status = self.processor_status | 0b01000000
        else:
            self.processor_status = self.processor_status & 0b10111111
        self.accumulator = self.accumulator + Memory.memory[address] + (self.processor_status & 0b00000001)
        if self.accumulator > 0xFF:
            self.processor_status = self.processor_status | 0b00000001
        else:
            self.processor_status = self.processor_status & 0b11111110
        self.accumulator = self.accumulator & 0x00FF
        self.value_zero_negative(self.accumulator)

    def AND(self, address):
        self.accumulator = self.accumulator & Memory.memory[address]
        self.value_zero_negative(self.accumulator)

    def ASL(self, address):
        if (Memory.memory[address] & 0b10000000) == 0b10000000:
            self.processor_status = self.processor_status | 0b00000001
        else:
            self.processor_status = self.processor_status & 0b11111110
        Memory.memory[address] = (Memory.memory[address] << 1) & 0x0FF
        self.value_zero_negative(Memory.memory[address])

    def ASLa(self):
        if (self.accumulator & 0b10000000) == 0b10000000:
            self.processor_status = self.processor_status | 0b00000001
        else:
            self.processor_status = self.processor_status & 0b11111110
        self.accumulator = self.accumulator << 1
        if self.accumulator > 0b11111111:
            self.accumulator = 0
        self.value_zero_negative(self.accumulator)
        self.program_counter += 1

    def BCC(self):
        if (self.processor_status & 0b00000001) == 0b00000000:
            self.branch()
        else:
            self.program_counter += 2

    def BCS(self):
        if (self.processor_status & 0b00000001) == 0b00000001:
            self.branch()
        else:
            self.program_counter += 2

    def BEQ(self):
        if (self.processor_status & 0b00000010) == 0b00000010:
            self.branch()
        else:
            self.program_counter += 2

    def BIT(self, address):
        if Memory.memory[address] & 0b01000000 == 0b01000000:
            self.processor_status = self.processor_status | 0b01000000
        else:
            self.processor_status = self.processor_status & 0b10111111
        if Memory.memory[address] & 0b10000000 == 0b10000000:
            self.processor_status = self.processor_status | 0b10000000
        else:
            self.processor_status = self.processor_status & 0b01111111
        if self.accumulator & Memory.memory[address] == 0:
            self.processor_status = self.processor_status | 0b00000010
        else:
            self.processor_status = self.processor_status & 0b11111101



    def BMI(self):
        if (self.processor_status & 0b10000000) == 0b10000000:
            self.branch()
        else:
            self.program_counter += 2


    def BNE(self):
        if (self.processor_status & 0b00000010) == 0b00000000:
            self.branch()
        else:
            self.program_counter += 2


    def BPL(self):
        if (self.processor_status & 0b10000000) == 0b00000000:
            self.branch()
        else:
            self.program_counter += 2

    def BRK(self):
        self.program_counter = ((Memory.memory[0XFFFF] << 8) | Memory.memory[0XFFFE])
        self.processor_status = self.processor_status | 0b00110100

    def BVC(self):
        if (self.processor_status & 0b01000000) == 0b00000000:
            self.branch()
        else:
            self.program_counter += 2

    def BVS(self):
        if (self.processor_status & 0b01000000) == 0b01000000:
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


    def CMP(self, address):
        if self.accumulator >= Memory.memory[address]:
            self.processor_status = self.processor_status | 0b00000001
        else:
            self.processor_status = self.processor_status & 0b11111110
        if self.accumulator == Memory.memory[address]:
            self.processor_status = self.processor_status | 0b00000010
        else:
            self.processor_status = self.processor_status & 0b11111101
        if (self.accumulator - Memory.memory[address]) & 0b10000000 == 0b10000000:
            self.processor_status = self.processor_status | 0b10000000
        else:
            self.processor_status = self.processor_status & 0b01111111


    def CPX(self, address):
        if self.x >= Memory.memory[address]:
            self.processor_status = self.processor_status | 0b00000001
        else:
            self.processor_status = self.processor_status & 0b11111110
        if self.x == Memory.memory[address]:
            self.processor_status = self.processor_status | 0b00000010
        else:
            self.processor_status = self.processor_status & 0b11111101
        if (self.x - Memory.memory[address]) & 0b10000000 == 0b10000000:
            self.processor_status = self.processor_status | 0b10000000
        else:
            self.processor_status = self.processor_status & 0b01111111


    def CPY(self, address):
        if self.y >= Memory.memory[address]:
            self.processor_status = self.processor_status | 0b00000001
        else:
            self.processor_status = self.processor_status & 0b11111110
        if self.y == Memory.memory[address]:
            self.processor_status = self.processor_status | 0b00000010
        else:
            self.processor_status = self.processor_status & 0b11111101
        if (self.y - Memory.memory[address]) & 0b10000000 == 0b10000000:
            self.processor_status = self.processor_status | 0b10000000
        else:
            self.processor_status = self.processor_status & 0b01111111


    def DEC(self, address):
        if Memory.memory[address]== 0:
            Memory.memory[address] = ~Memory.memory[address] & 0b011111111
        else:
            Memory.memory[address] -= 1
        self.value_zero_negative(Memory.memory[address])

    def DEX(self):
        if self.x == 0:
            self.x = ~self.x & 0b011111111
        else:
            self.x -= 1
        self.value_zero_negative(self.x)
        self.program_counter += 1

    def DEY(self):
        if self.y == 0:
            self.y = ~self.y & 0b011111111
        else:
            self.y -= 1
        self.value_zero_negative(self.y)
        self.program_counter += 1

    def EOR(self, address):
        self.accumulator = self.accumulator ^ Memory.memory[address]
        self.value_zero_negative(self.accumulator)

    def INC(self, address):
        Memory.memory[address] = (Memory.memory[address] + 1) & 0x0FF
        self.value_zero_negative(Memory.memory[address])

    def INX(self):
        self.x = (self.x + 1) & 0x0FF
        self.value_zero_negative(self.x)
        self.program_counter += 1

    def INY(self):
        self.y = (self.y + 1) & 0x0FF
        self.value_zero_negative(self.y)
        self.program_counter += 1

    def JMP(self, address):
        self.program_counter = address

    def JSR(self):
        sub_routine = self.program_counter + 2
        Memory.memory[self.stack_pointer] = (sub_routine & 0xFF00) >> 8
        Memory.memory[self.stack_pointer - 1] = (sub_routine & 0x00FF)
        self.stack_pointer -= 2
        self.program_counter = self.absolute()

    def LDA(self, address):
        self.accumulator = Memory.memory[address]
        self.value_zero_negative(self.accumulator)

    def LDX(self, address):
        self.x = Memory.memory[address]
        self.value_zero_negative(self.x)

    def LDY(self, address):
        self.y = Memory.memory[address]
        self.value_zero_negative(self.y)

    def LSR(self, address):
        if (Memory.memory[address] & 0b00000001) == 0b00000001:
            self.processor_status = self.processor_status | 0b00000001
        else:
            self.processor_status = self.processor_status & 0b11111110
        Memory.memory[address] = Memory.memory[address] >> 1
        self.value_zero_negative(Memory.memory[address])

    def LSRa(self):
        if (self.accumulator & 0b00000001) == 0b00000001:
            self.processor_status = self.processor_status | 0b00000001
        else:
            self.processor_status = self.processor_status & 0b11111110
        self.accumulator = self.accumulator >> 1
        self.value_zero_negative(self.accumulator)
        self.program_counter += 1

    def NOP(self, *args):
        if len(args) == 0:
            self.program_counter += 1

    def ORA(self, address):
        self.accumulator = self.accumulator | Memory.memory[address]
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
        if Memory.memory[address] & 0b10000000 == 0b10000000:
            self.processor_status = self.processor_status | 0b100000000
        else:
            self.processor_status = self.processor_status & 0b011111111
        Memory.memory[address] = ((Memory.memory[address] << 1) | (self.processor_status & 0b100000000) >> 8) & 0x00FF
        if self.processor_status & 0b100000000 == 0b100000000:
            self.processor_status = (self.processor_status | ((self.processor_status & 0b100000000) >> 8) & 0x00FF)
        else:
            self.processor_status = self.processor_status & (self.processor_status & 0b011111110)
        self.value_zero_negative(Memory.memory[address])

    def ROLa(self):
        if self.accumulator & 0b10000000 == 0b10000000:
            self.processor_status = self.processor_status | 0b100000000
        else:
            self.processor_status = self.processor_status & 0b011111111
        self.accumulator = ((self.accumulator << 1) | (self.processor_status & 0b100000000) >> 8) & 0x00FF
        if self.processor_status & 0b100000000 == 0b100000000:
            self.processor_status = (self.processor_status | ((self.processor_status & 0b100000000) >> 8) & 0x00FF)
        else:
            self.processor_status = self.processor_status & (self.processor_status & 0b011111110)
        self.value_zero_negative(self.accumulator)
        self.program_counter += 1

    def ROR(self, address):
        value = (Memory.memory[address] | ((self.processor_status & 0b00000001) << 8))
        if (value & 0b1) == 0b1:
            self.processor_status = self.processor_status | 0b1
        else:
            self.processor_status = self.processor_status & 0b11111110
        Memory.memory[address] = (value >> 1)
        self.value_zero_negative(Memory.memory[address])

    def RORa(self):
        self.accumulator = self.accumulator | ((self.processor_status & 0b00000001) << 8)
        if (self.accumulator & 0b1) == 0b1:
            self.processor_status = self.processor_status | 0b1
        else:
            self.processor_status = self.processor_status & 0b11111110
        self.accumulator = self.accumulator >> 1
        self.value_zero_negative(self.accumulator)
        self.program_counter += 1

    def RTI(self):
        self.stack_pointer += 1
        self.processor_status = Memory.memory[self.stack_pointer] | 0b00100000
        self.stack_pointer += 2
        self.program_counter += 1

    def RTS(self):
        self.stack_pointer += 2
        self.program_counter = ((Memory.memory[self.stack_pointer] << 8) | Memory.memory[self.stack_pointer - 1]) + 1

    def SBC(self, address):
        if (self.accumulator - Memory.memory[address]) - (1 - (self.processor_status & 0b00000001)) & 0b10000000 == 0b00000000 and self.accumulator & 0b10000000 == 0b10000000 and ~Memory.memory[address] & 0b10000000 == 0b10000000:
            self.processor_status = self.processor_status | 0b01000000
        elif ~(self.accumulator - Memory.memory[address]) & 0b10000000 == 0b10000000 and (~self.accumulator & 0b10000000 == 0b00000000 and ~Memory.memory[address] & 0b10000000 == 0b00000000):
            self.processor_status = self.processor_status | 0b01000000
        else:
            self.processor_status = self.processor_status & 0b10111111
        self.accumulator = self.accumulator - Memory.memory[address] - (1 - (self.processor_status & 0b00000001))
        if self.accumulator & 0b10000000 == 0b10000000:
            self.processor_status = self.processor_status & 0b11111110
        else:
            self.processor_status = self.processor_status | 0b00000001
        self.accumulator = self.accumulator & 0x00FF
        self.value_zero_negative(self.accumulator)

    def SEC(self):
        self.processor_status = self.processor_status | 0b00000001
        self.program_counter += 1

    def SED(self):
        self.processor_status = self.processor_status | 0b00001000
        self.program_counter += 1

    def SEI(self):
        self.processor_status = self.processor_status | 0b00000100
        self.program_counter += 1

    def STA(self, address):
        if self.accumulator < 0:
            self.accumulator *= -1
        Memory.memory[address] = self.accumulator
        
    def STP(self):
        pass

    def STX(self, address):
        if self.x < 0:
            self.x *= -1
        Memory.memory[address] = self.x

    def STY(self, address):
        if self.y < 0:
            self.y *= -1
        Memory.memory[address] = self.y

    def TAX(self):
        self.x = self.accumulator
        self.value_zero_negative(self.x)
        self.program_counter += 1

    def TAY(self):
        self.y = self.accumulator
        self.value_zero_negative(self.y)
        self.program_counter += 1

    def TSX(self):
        self.x = self.stack_pointer & 0x0FF
        self.value_zero_negative(self.x)
        self.program_counter += 1

    def TXA(self):
        self.accumulator = self.x
        self.value_zero_negative(self.accumulator)
        self.program_counter += 1

    def TXS(self):
        self.stack_pointer = self.x + 0x100
        self.program_counter +=1

    def TYA(self):
        self.accumulator = self.y
        self.value_zero_negative(self.accumulator)
        self.program_counter += 1

            #undocumented opcodes

    def ANC(self, address):
        pass

    def RLA(self, address):
        pass

    def SLO(self, address):
        pass

    def SRE(self, address):
        pass

    def __init__(self):

        self.opcode_table = {0x00:lambda:self.BRK(),0x01:lambda:self.ORA(self.indexed_indirect()),0x02:lambda:self.STP(),0x03:lambda:self.SLO(self.indexed_indirect()),0x04:lambda:self.NOP(self.zero_page()),0x05:lambda:self.ORA(self.zero_page()),0x06:lambda:self.ASL(self.zero_page()),0x07:lambda:self.SLO(self.zero_page()),0x08:lambda:self.PHP(),
                             0x09:lambda:self.ORA(self.immediate()),0x0A:lambda:self.ASLa(),0x0B:lambda:self.ANC(self.immediate()),0x0C:lambda:self.NOP(self.absolute()),0x0D:lambda:self.ORA(self.absolute()),0x0E:lambda:self.ASL(self.absolute()),0x0F:lambda:self.SLO(self.absolute()),0x10:lambda:self.BPL(),0x11:lambda:self.ORA(self.indirect_indexed()),
                             0x12:lambda:self.STP,0x13:lambda:self.SLO(self.indirect_indexed()),0x14:lambda:self.NOP(self.zero_page_x()),0x15:lambda:self.ORA(self.zero_page_x()),0x16:lambda:self.ASL(self.zero_page_x()),0x17:lambda:self.SLO(self.zero_page_x()),0x18:lambda:self.CLC(),0x19:lambda:self.ORA(self.absolute_y()),0x1A:lambda:self.NOP(),
                             0x1B:lambda:self.SLO(self.absolute_y()),0x1C:lambda:self.NOP,0x1D:lambda:self.ORA(self.absolute_x()),0x1E:lambda:self.ASL(self.absolute_x()),0x1F:lambda:self.SLO(self.absolute_x()),0x20:lambda:self.JSR(),0x21:lambda:self.AND(self.indexed_indirect()),0x22:lambda:self.STP,0x23:lambda:self.RLA(self.indexed_indirect()),
                             0x24:lambda:self.BIT(self.zero_page()),0x25:lambda:self.AND(self.zero_page()),0x26:lambda:self.ROL(self.zero_page()),0x27:lambda:self.RLA(self.zero_page()),0x28:lambda:self.PLP(),0x29:lambda:self.AND(self.immediate()),0x2A:lambda:self.ROLa(),0x2B:lambda:self.ANC(self.immediate()),0x2C:lambda:self.BIT(self.absolute()),
                             0x2D:lambda:self.AND(self.absolute()),0x2E:lambda:self.ROL(self.absolute()),0x2F:lambda:self.RLA(self.absolute()),0x30:lambda:self.BMI(),0x31:lambda:self.AND(self.indirect_indexed()),0x32:lambda:self.STP,0x33:lambda:self.RLA(self.indirect_indexed()),0x34:lambda:self.NOP(self.zero_page_x()),
                             0x35:lambda:self.AND(self.zero_page_x()),0x36:lambda:self.ROL(self.zero_page_x()),0x37:lambda:self.RLA(self.zero_page_x()),0x38:lambda:self.SEC(),0x39:lambda:self.AND(self.absolute_y()),0x3A:lambda:self.NOP,0x3B:lambda:self.RLA(self.absolute_y),0x3C:lambda:self.NOP,0x3D:lambda:self.AND(self.absolute_x()),
                             0x3E:lambda:self.ROL(self.absolute_x()),0x3F:lambda:self.RLA(self.absolute_x()),0x40:lambda:self.RTI(),0x41:lambda:self.EOR(self.indexed_indirect()),0x42:lambda:self.STP,0x43:lambda:self.SRE(self.indexed_indirect()),0x44:lambda:self.NOP(self.zero_page()),0x45:lambda:self.EOR(self.zero_page()),
                             0x46:lambda:self.LSR(self.zero_page()),0x47:lambda:self.STP,0x48:lambda:self.PHA(),0x49:lambda:self.EOR(self.immediate()),0x4A:lambda:self.LSRa(),0x4B:lambda:self.STP,0x4C:lambda:self.JMP(self.absolute()),0x4D:lambda:self.EOR(self.absolute()),0x4E:lambda:self.LSR(self.absolute()),0x4F:lambda:self.STP,0x50:lambda:self.BVC(),
                             0x51:lambda:self.EOR(self.indirect_indexed()),0x52:lambda:self.STP,0x53:lambda:self.STP,0x54:lambda:self.STP,0x55:lambda:self.EOR(self.zero_page_x()),0x56:lambda:self.LSR(self.zero_page_x()),0x57:lambda:self.STP,0x58:lambda:self.STP,0x59:lambda:self.EOR(self.absolute_y()),0x5A:lambda:self.STP,0x5B:lambda:self.STP,
                             0x5C:lambda:self.STP,0x5D:lambda:self.EOR(self.absolute_x()),0x5E:lambda:self.LSR(self.absolute_x()),0x5F:lambda:self.STP,0x60:lambda:self.RTS(),0x61:lambda:self.ADC(self.indexed_indirect()),0x62:lambda:self.STP,0x63:lambda:self.STP,0x64:lambda:self.NOP(self.zero_page()),0x65:lambda:self.ADC(self.zero_page()),
                             0x66:lambda:self.ROR(self.zero_page()),0x67:lambda:self.STP,0x68:lambda:self.PLA(),0x69:lambda:self.ADC(self.immediate()),0x6A:lambda:self.RORa(),0x6B:lambda:self.STP,0x6C:lambda:self.JMP(self.indirect()),0x6D:lambda:self.ADC(self.absolute()),0x6E:lambda:self.ROR(self.absolute()),0x6F:lambda:self.STP,0x70:lambda:self.BVS(),
                             0x71:lambda:self.ADC(self.indirect_indexed()),0x72:lambda:self.STP,0x73:lambda:self.STP,0x74:lambda:self.STP,0x75:lambda:self.ADC(self.zero_page_x()),0x76:lambda:self.ROR(self.zero_page_x()),0x77:lambda:self.STP,0x78:lambda:self.SEI(),0x79:lambda:self.ADC(self.absolute_y()),0x7A:lambda:self.STP,0x7B:lambda:self.STP,
                             0x7C:lambda:self.STP,0x7D:lambda:self.ADC(self.absolute_x()),0x7E:lambda:self.ROR(self.absolute_x()),0x7F:lambda:self.STP,0x80:lambda:self.STP,0x81:lambda:self.STA(self.indexed_indirect()),0x82:lambda:self.STP,0x83:lambda:self.STP,0x84:lambda:self.STY(self.zero_page()),0x85:lambda:self.STA(self.zero_page()),
                             0x86:lambda:self.STX(self.zero_page()),0x87:lambda:self.STP,0x88:lambda:self.DEY(),0x89:lambda:self.STP,0x8A:lambda:self.TXA(),0x8B:lambda:self.STP,0x8C:lambda:self.STY(self.absolute()),0x8D:lambda:self.STA(self.absolute()),0x8E:lambda:self.STX(self.absolute()),0x8F:lambda:self.STP,0x90:lambda:self.BCC(),
                             0x91:lambda:self.STA(self.indirect_indexed()),0x92:lambda:self.STP,0x93:lambda:self.STP,0x94:lambda:self.STY(self.zero_page_x()),0x95:lambda:self.STA(self.zero_page_x()),0x96:lambda:self.STX(self.zero_page_y()),0x97:lambda:self.STP,0x98:lambda:self.TYA(),0x99:lambda:self.STA(self.absolute_y()),0x9A:lambda:self.TXS(),
                             0x9B:lambda:self.STP,0x9C:lambda:self.STP,0x9D:lambda:self.STA(self.absolute_x()),0x9E:lambda:self.STP,0x9F:lambda:self.STP,0xA0:lambda:self.LDY(self.immediate()),0xA1:lambda:self.LDA(self.indexed_indirect()),0xA2:lambda:self.LDX(self.immediate()),0xA3:lambda:self.STP,0xA4:lambda:self.LDY(self.zero_page()),
                             0xA5:lambda:self.LDA(self.zero_page()),0xA6:lambda:self.LDX(self.zero_page()),0xA7:lambda:self.STP,0xA8:lambda:self.TAY(),0xA9:lambda:self.LDA(self.immediate()),0xAA:lambda:self.TAX(),0xAB:lambda:self.STP,0xAC:lambda:self.LDY(self.absolute()),0xAD:lambda:self.LDA(self.absolute()),0xAE:lambda:self.LDX(self.absolute()),
                             0xAF:lambda:self.STP,0xB0:lambda:self.BCS(),0xB1:lambda:self.LDA(self.indirect_indexed()),0xB2:lambda:self.STP,0xB3:lambda:self.STP,0xB4:lambda:self.LDY(self.zero_page_x()),0xB5:lambda:self.LDA(self.zero_page_x()),0xB6:lambda:self.LDX(self.zero_page_y()),0xB7:lambda:self.STP,0xB8:lambda:self.CLV(),
                             0xB9:lambda:self.LDA(self.absolute_y()),0xBA:lambda:self.TSX(),0xBB:lambda:self.STP,0xBC:lambda:self.LDY(self.absolute_x()),0xBD:lambda:self.LDA(self.absolute_x()),0xBE:lambda:self.LDX(self.absolute_y()),0xBF:lambda:self.STP,0xC0:lambda:self.CPY(self.immediate()),0xC1:lambda:self.CMP(self.indexed_indirect()),
                             0xC2:lambda:self.STP,0xC3:lambda:self.STP,0xC4:lambda:self.CPY(self.zero_page()),0xC5:lambda:self.CMP(self.zero_page()),0xC6:lambda:self.DEC(self.zero_page()),0xC7:lambda:self.STP,0xC8:lambda:self.INY(),0xC9:lambda:self.CMP(self.immediate()),0xCA:lambda:self.DEX(),0xCB:lambda:self.STP,0xCC:lambda:self.CPY(self.absolute()),
                             0xCD:lambda:self.CMP(self.absolute()),0xCE:lambda:self.DEC(self.absolute()),0xCF:lambda:self.STP,0xD0:lambda:self.BNE(),0xD1:lambda:self.CMP(self.indirect_indexed()),0xD2:lambda:self.STP(),0xD3:lambda:self.STP,0xD4:lambda:self.STP,0xD5:lambda:self.CMP(self.zero_page_x()),0xD6:lambda:self.DEC(self.zero_page_x()),
                             0xD7:lambda:self.STP,0xD8:lambda:self.CLD(),0xD9:lambda:self.CMP(self.absolute_y()),0xDA:lambda:self.STP,0xDB:lambda:self.STP,0xDC:lambda:self.STP,0xDD:lambda:self.CMP(self.absolute_x()),0xDE:lambda:self.DEC(self.absolute_x()),0xDF:lambda:self.STP,0xE0:lambda:self.CPX(self.immediate()),
                             0xE1:lambda:self.SBC(self.indexed_indirect()),0xE2:lambda:self.STP,0xE3:lambda:self.STP,0xE4:lambda:self.CPX(self.zero_page()),0xE5:lambda:self.SBC(self.zero_page()),0xE6:lambda:self.INC(self.zero_page()),0xE7:lambda:self.STP,0xE8:lambda:self.INX(),0xE9:lambda:self.SBC( self.immediate()),0xEA:lambda:self.NOP(),
                             0xEB:lambda:self.STP,0xEC:lambda:self.CPX(self.absolute()),0xED:lambda:self.SBC(self.absolute()),0xEE:lambda:self.INC(self.absolute()),0xEF:lambda:self.STP,0xF0:lambda:self.BEQ(),0xF1:lambda:self.SBC(self.indirect_indexed()),0xF2:lambda:self.STP,0xF3:lambda:self.STP,0xF4:lambda:self.STP,0xF5:lambda:self.SBC(self.zero_page_x())
                            ,0xF6:lambda:self.INC(self.zero_page_x()),0xF7:lambda:self.STP,0xF8:lambda:self.SED(),0xF9:lambda:self.SBC(self.absolute_y()),0xFA:lambda:self.STP,0xFB:lambda:self.STP,0xFC:lambda:self.STP,0xFD:lambda:self.SBC(self.absolute_x()),0xFE:lambda:self.INC(self.absolute_x()),0xFF:lambda:self.STP}
