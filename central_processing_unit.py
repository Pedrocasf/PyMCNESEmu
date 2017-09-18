from main_memory import Memory
import logging


class CPU:
    accumulator = 0x00
    x = 0x00
    y = 0x00
    stack_pointer = 0x01FF
    program_counter = 0xC000
    cycle_count = 0
    processor_status = 0b00000000

    def A_zero_negative(self):
        if self.accumulator == 0:
            self.processor_status = self.processor_status | 0b00000010
        else:
            self.processor_status = self.processor_status & 0b11111101
        self.processor_status = self.processor_status | (self.accumulator & 0b10000000)

    def Y_zero_negative(self):
        if self.y == 0:
            self.processor_status = self.processor_status | 0b00000010
        else:
            self.processor_status = self.processor_status & 0b11111101
        self.processor_status = self.processor_status | (self.y & 0b10000000)

    def X_zero_negative(self):
        if self.x == 0:
            self.processor_status = self.processor_status | 0b00000010
        else:
            self.processor_status = self.processor_status & 0b11111101
        self.processor_status = self.processor_status | (self.x & 0b10000000)

    def M_zero_negative(self):
        if Memory.memory[self.program_counter + 1] == 0:
            self.processor_status = self.processor_status | 0b00000010
        else:
            self.processor_status = self.processor_status & 0b11111101
        self.processor_status = self.processor_status | (Memory.memory[self.program_counter + 1] & 0b10000000)

    def branch(self):
        if Memory.memory[self.program_counter + 1] & 0b10000000 != 0:
            self.program_counter -= (~(Memory.memory[self.program_counter + 1]) & 0b01111111) - 1
        else:
            self.program_counter += ((Memory.memory[self.program_counter + 1]) + 2)
        self.cycle_count += 9

    def not_branch(self):
        self.program_counter += 2
        self.cycle_count += 6

    def compare(self, register: object, address: object) -> object:
        if register >= Memory.memory[address]:
            self.processor_status = self.processor_status | 0b00000001
        if register == Memory.memory[address]:
            self.processor_status = self.processor_status | 0b00000010
        self.processor_status = self.processor_status | ((register - Memory.memory[address]) | 0b10000000)

    def store(self, register, address):
        if register < 0:
            register *= -1
        Memory.memory[address] = register

    def indexed_indirect(self):
        lsb = (Memory.memory[self.program_counter] + self.x) & 0x0FF
        address = Memory.memory[lsb + 1] << 8 | Memory.memory[lsb]
        logging.debug(address)
        return address

    def indirect_indexed(self):
        address = ((Memory.memory[self.program_counter + 1] + 1 << 8) | Memory.memory[self.program_counter + 1]) + self.y
        return address

    def absolute(self):
        address = (Memory.memory[self.program_counter + 2] << 8) | Memory.memory[self.program_counter + 1]
        return address

    def BRK(self):
        self.processor_status = 0
        self.program_counter = ((Memory.memory[0XFFFF] << 8) | Memory.memory[0XFFFE])
        self.processor_status = self.processor_status | 0b00110100
        self.cycle_count += 7

    def ORAdx(self):
        pass

    def STP(self):
        pass

    def SLOdx(self):
        pass

    def NOP(self):
        self.program_counter += 1
        self.cycle_count += 6

    def ORAd(self):
        pass

    def ASLd(self):
        pass

    def SLOd(self):
        pass

    def PHP(self):
        Memory.memory[self.stack_pointer] = self.processor_status | 0b00110100
        self.program_counter += 1

    def ORAi(self):
        self.accumulator = self.accumulator | Memory.memory[self.program_counter + 1]
        self.A_zero_negative()
        self.program_counter += 2

    def ASL(self):
        self.processor_status = 0
        self.processor_status = self.processor_status | (self.accumulator & 0b10000000)
        self.accumulator = self.accumulator << 1
        self.A_zero_negative()
        self.program_counter += 1

    def ANCi(self):
        pass

    def NOPa(self):
        self.program_counter += 1
        self.cycle_count += 6

    def ORAa(self):
        pass

    def ASLa(self):
        pass

    def SLOa(self):
        pass

    def BPLd(self):
        if self.processor_status & 0b10000000 == 0b000000000:
            self.branch()
        else:
            self.not_branch()

    def ORAdy(self):
        pass

    def SLOdy(self):
        pass

    def NOPdx(self):
        self.program_counter += 1
        self.cycle_count += 6

    def ORAidx(self):
        self.accumulator = (self.accumulator | self.indexed_indirect()) & 0x00FF
        self.program_counter += 2

    def ASLdx(self):
        pass

    def CLC(self):
        self.processor_status = 0
        self.processor_status = self.processor_status & 0b11111110
        self.program_counter += 1
        self.cycle_count += 6

    def ORAay(self):
        pass

    def SLOay(self):
        pass

    def NOPax(self):
        self.program_counter += 1
        self.cycle_count += 6

    def ORAax(self):
        pass

    def ASLax(self):
        self.processor_status = 0
        address = (Memory.memory[self.program_counter + 2] << 8 | Memory.memory[self.program_counter + 1]) + self.x
        self.processor_status = self.processor_status | (address & 0b10000000)
        self.accumulator = address << 1
        self.A_zero_negative()
        self.program_counter += 3

    def SLOax(self):
        pass

    def JSRa(self):
        Memory.memory[self.stack_pointer] = (self.program_counter & 0xFF00) >> 8
        Memory.memory[self.stack_pointer - 1] = (self.program_counter & 0x00FF)
        self.stack_pointer -= 2
        self.program_counter = self.absolute()
        self.cycle_count += 18

    def ANDdx(self):
        pass

    def RLAdx(self):
        pass

    def BITd(self):
        self.processor_status = 0
        self.processor_status = self.processor_status | (
        Memory.memory[Memory.memory[self.program_counter + 1]] & 0b01000000)
        self.processor_status = self.processor_status | (
        Memory.memory[Memory.memory[self.program_counter + 1]] & 0b10000000)
        self.program_counter += 2
        self.cycle_count += 9

    def ANDd(self):
        pass

    def ROLd(self):
        pass

    def RLAd(self):
        pass

    def PLP(self):
        self.processor_status = 0
        self.processor_status = Memory.memory[self.stack_pointer]
        self.program_counter += 1

    def ANDi(self):
        self.processor_status = 0
        self.accumulator = self.accumulator & Memory.memory[self.program_counter + 1]
        self.A_zero_negative()
        self.program_counter += 2

    def ROL(self):
        self.processor_status = 0
        self.processor_status = self.processor_status | (self.accumulator & 0b10000000)
        self.accumulator = (self.accumulator << 1) & (self.processor_status & 0b00000001)
        self.A_zero_negative()
        self.program_counter += 2

    def BITa(self):
        self.processor_status = 0
        v = self.accumulator & self.absolute()
        self.processor_status = self.processor_status | (v & 0b01000000)
        self.processor_status = self.processor_status | (v & 0b10000000)
        self.program_counter += 2

    def ANDa(self):
        self.processor_status = 0
        self.accumulator = self.accumulator & Memory.memory[self.program_counter + 1]
        self.A_zero_negative()
        self.program_counter += 2

    def ROLa(self):
        self.processor_status = 0
        self.processor_status = self.processor_status | (Memory.memory[self.program_counter + 1] & 0b1000000)
        Memory.memory[self.program_counter + 1] = (Memory.memory[self.program_counter + 1] << 1) & 0b1000000
        self.M_zero_negative()
        self.program_counter += 2

    def RLAa(self):
        pass

    def BMId(self):
        if self.processor_status & 0b10000000 != 0:
            self.branch()
        else:
            self.not_branch()

    def ANDdy(self):
        pass

    def RLAdy(self):
        pass

    def ROLdx(self):
        pass

    def SEC(self):
        self.processor_status = 0
        self.processor_status = self.processor_status | 0b00000001
        self.program_counter += 1
        self.cycle_count += 6

    def ANDay(self):
        pass

    def RLAay(self):
        pass

    def ANDax(self):
        pass

    def ROLax(self):
        pass

    def RLAax(self):
        pass

    def RTI(self):
        self.program_counter += 1

    def EORdx(self):
        pass

    def SREdx(self):
        pass

    def NOPd(self):
        self.program_counter += 1
        self.cycle_count += 6

    def EORd(self):
        pass

    def LSRd(self):
        pass

    def SREd(self):
        pass

    def PHA(self):
        Memory.memory[self.stack_pointer] = self.accumulator
        self.program_counter += 1

    def LSRdx(self):
        pass

    def EORi(self):
        self.processor_status = 0
        self.accumulator = self.accumulator ^ Memory.memory[self.program_counter + 1]
        self.A_zero_negative()
        self.program_counter += 2

    def LSR(self):
        self.processor_status = 0
        self.processor_status = self.processor_status | (self.accumulator & 0b00000001)
        self.accumulator = self.accumulator >> 1
        self.A_zero_negative()
        self.program_counter += 1

    def ALRi(self):
        pass

    def JMPa(self):
        self.program_counter = self.absolute()
        self.cycle_count += 9

    def EORa(self):
        pass

    def LSRa(self):
        pass

    def SREa(self):
        pass

    def BVCd(self):
        if self.processor_status & 0b01000000 == 0:
            self.branch()
        else:
            self.not_branch()

    def EORdy(self):
        pass

    def SREdy(self):
        pass

    def CLI(self):
        pass

    def EORay(self):
        pass

    def SREay(self):
        pass

    def EORax(self):
        pass

    def LSRax(self):
        pass

    def SREax(self):
        pass

    def RTS(self):
        self.stack_pointer += 2
        self.program_counter = ((Memory.memory[self.stack_pointer] << 8) | Memory.memory[self.stack_pointer - 1]) + 3

    def ADCdx(self):
        pass

    def RRAdx(self):
        pass

    def ADCd(self):
        pass

    def RORd(self):
        pass

    def RRAd(self):
        pass

    def PLA(self):
        self.processor_status = 0
        self.accumulator = Memory.memory[self.stack_pointer]
        self.A_zero_negative()
        self.program_counter += 1

    def ADCi(self):
        self.processor_status = 0
        self.accumulator += Memory.memory[self.program_counter + 1]
        if self.accumulator >= 0xFF:
            self.accumulator = self.accumulator >> 1
            self.processor_status = self.processor_status | 0b00000001
        self.A_zero_negative()
        self.program_counter += 2

    def ROR(self):
        self.processor_status = 0
        self.processor_status = self.processor_status | (self.accumulator & 0b10000000)
        self.accumulator = self.accumulator & ((self.processor_status & 0b00000001) << 8)
        self.accumulator = self.accumulator >> 1
        self.A_zero_negative()
        self.program_counter += 1

    def ARRi(self):
        pass

    def JMPIa(self):
        pass

    def ADCa(self):
        pass

    def RORa(self):
        pass

    def RRAa(self):
        pass

    def BVSd(self):
        if self.processor_status & 0b01000000 != 0:
            self.branch()
        else:
            self.not_branch()

    def ADCdy(self):
        pass

    def RRAdy(self):
        pass

    def RORdx(self):
        pass

    def SEI(self):
        self.processor_status = self.processor_status | 0b000001000
        self.program_counter += 1

    def ADCay(self):
        pass

    def RRAay(self):
        pass

    def ADCax(self):
        pass

    def RORax(self):
        pass

    def RRAax(self):
        pass

    def NOPi(self):
        self.program_counter += 1
        self.cycle_count += 6

    def STAdx(self):
        self.store(self.accumulator, Memory.memory[self.program_counter + 1] + self.x)
        self.program_counter += 2

    def SAXdx(self):
        pass

    def STYd(self):
        self.store(self.y, Memory.memory[self.program_counter + 1])
        self.program_counter += 2

    def STAd(self):
        self.store(self.accumulator, Memory.memory[self.program_counter + 1])
        self.program_counter += 2
        self.cycle_count += 9

    def STXd(self):
        self.store(self.x, self.program_counter + 1)
        self.program_counter += 2
        self.cycle_count += 9

    def SAXd(self):
        pass

    def DEY(self):
        self.processor_status = 0
        self.y -= 1
        self.Y_zero_negative()
        self.program_counter += 1

    def TXA(self):
        self.processor_status = 0
        self.accumulator = self.x
        self.A_zero_negative()
        self.program_counter += 1

    def XAAi(self):
        pass

    def STYa(self):
        pass

    def STAa(self):
        Memory.memory[self.absolute()] = self.accumulator
        self.program_counter += 3

    def STXa(self):
        self.store(self.x, self.absolute())
        self.program_counter += 3

    def SAXa(self):
        pass

    def BCCd(self):
        if self.processor_status & 0b00000001 == 0:
            self.branch()
        else:
            self.not_branch()

    def STAdy(self):
        address = self.indexed_indirect()
        self.store(self.y, address)
        self.program_counter += 2

    def AHXdy(self):
        pass

    def STYdx(self):
        pass

    def STXdy(self):
        pass

    def SAXdy(self):
        pass

    def TYA(self):
        self.accumulator = self.y
        self.A_zero_negative()
        self.program_counter += 1

    def STAay(self):
        pass

    def TXS(self):
        self.stack_pointer = self.x + 0x100
        self.program_counter += 1

    def TASay(self):
        pass

    def SHYax(self):
        pass

    def STAax(self):
        pass

    def SHXay(self):
        pass

    def AHXay(self):
        pass

    def LDYi(self):
        self.y = Memory.memory[self.program_counter + 1]
        self.Y_zero_negative()
        self.program_counter += 2

    def LDAdx(self):
        self.accumulator = Memory.memory[(Memory.memory[self.program_counter + 1] + self.x) & 0x0FF]
        self.A_zero_negative()
        self.program_counter += 2

    def LDXi(self):
        self.x = Memory.memory[self.program_counter + 1]
        self.X_zero_negative()
        self.program_counter += 2
        self.cycle_count += 6

    def LAXdx(self):
        pass

    def LDYd(self):
        pass

    def LDAd(self):
        self.accumulator = Memory.memory[self.program_counter + 1]
        self.A_zero_negative()
        self.program_counter += 2

    def LDXd(self):
        self.x = Memory.memory[Memory.memory[self.program_counter + 1]]
        self.X_zero_negative()
        self.program_counter += 2

    def LAXd(self):
        pass

    def TAY(self):
        self.y = self.accumulator
        self.Y_zero_negative()
        self.program_counter += 1

    def LDAi(self):
        self.accumulator = Memory.memory[self.program_counter + 1]
        self.A_zero_negative()
        self.program_counter += 2
        self.cycle_count += 6

    def TAX(self):
        self.x = self.accumulator
        self.X_zero_negative()
        self.program_counter += 2

    def LAXi(self):
        pass

    def LDYa(self):
        pass

    def LDAa(self):
        self.accumulator = Memory.memory[self.absolute()]
        self.A_zero_negative()
        self.program_counter += 3

    def LDXa(self):
        self.x = Memory.memory[self.absolute()]
        self.X_zero_negative()
        self.program_counter += 3

    def LAXa(self):
        pass

    def BCSd(self):
        if self.processor_status & 0b1 != 0:
            self.branch()
        else:
            self.not_branch()

    def LDAdy(self):
        pass

    def LAXdy(self):
        pass

    def LDYdx(self):
        pass

    def LDXdy(self):
        pass

    def CLV(self):
        self.processor_status = self.processor_status and 0b10111111
        self.program_counter += 1

    def LDAay(self):
        pass

    def TSX(self):
        self.x = self.stack_pointer - 0x100
        self.X_zero_negative()
        self.program_counter += 1

    def LASay(self):
        pass

    def LDYax(self):
        pass

    def LDAax(self):
        pass

    def LDXay(self):
        pass

    def LAXay(self):
        pass

    def CPYi(self):
        self.compare(self.y, self.program_counter + 1)
        self.program_counter += 2

    def CMPdx(self):
        pass

    def DCPdx(self):
        pass

    def CPYd(self):
        pass

    def CMPd(self):
        self.compare(self.accumulator, Memory.memory[self.program_counter + 1])
        self.program_counter += 2

    def DECd(self):
        pass

    def DCPd(self):
        pass

    def INY(self):
        self.y += 1
        self.Y_zero_negative()
        self.program_counter += 1

    def CMPi(self):
        if self.accumulator >= Memory.memory[self.program_counter + 1]:
            self.processor_status = self.processor_status | 0b00000001
        if self.accumulator == Memory.memory[self.program_counter + 1]:
            self.processor_status = self.processor_status | 0b00000010
        self.processor_status = self.processor_status | (
        (self.accumulator - Memory.memory[Memory.memory[self.program_counter + 1]]) | 0b10000000)
        self.program_counter += 2

    def DEX(self):
        self.processor_status = 0
        self.x -= 1
        self.X_zero_negative()
        self.program_counter += 1

    def AXSi(self):
        pass

    def CPYa(self):
        pass

    def CMPa(self):
        pass

    def DECa(self):
        pass

    def DCPa(self):
        pass

    def BNEd(self):
        if (self.processor_status & 0b00000010) != 0:
            self.branch()
        else:
            self.not_branch()

    def CMPdy(self):
        pass

    def DCPdy(self):
        pass

    def DECdx(self):
        pass

    def CLD(self):
        self.processor_status = self.processor_status & 0b11000111
        self.program_counter += 2

    def CMPay(self):
        pass

    def DCPay(self):
        pass

    def CMPax(self):
        pass

    def DECax(self):
        pass

    def DCPax(self):
        pass

    def CPXi(self):
        if self.x >= Memory.memory[self.program_counter + 1]:
            self.processor_status = self.processor_status | 0b00000001
        if self.x == Memory.memory[self.program_counter + 1]:
            self.processor_status = self.processor_status | 0b00000010
        self.processor_status = self.processor_status | (
        (self.x - Memory.memory[Memory.memory[self.program_counter + 1]]) | 0b10000000)
        self.program_counter += 2

    def SBCdx(self):
        pass

    def ISCdx(self):
        pass

    def CPXd(self):
        self.compare(self.x, Memory.memory[Memory.memory[self.program_counter + 1]])
        self.program_counter += 2

    def SBCd(self):
        pass

    def INCd(self):
        Memory.memory[Memory.memory[self.program_counter + 1]] += 1
        self.program_counter += 2

    def ISCd(self):
        pass

    def INX(self):
        self.x += 1
        self.X_zero_negative()
        self.program_counter += 1

    def SBCi(self):
        self.accumulator -= Memory.memory[self.program_counter + 1]
        if self.accumulator < 0:
            self.processor_status = self.processor_status | 0b00000010
        self.A_zero_negative()
        self.program_counter += 2

    def CPXa(self):
        pass

    def SBCa(self):
        pass

    def INCa(self):
        pass

    def ISCa(self):
        pass

    def BEQd(self):
        if self.processor_status & 0b00000010 == 0b10:
            self.branch()
        else:
            self.not_branch()

    def SBCdy(self):
        pass

    def ISCdy(self):
        pass

    def INCdx(self):
        pass

    def SED(self):
        self.processor_status = self.processor_status | 0b00001000
        self.program_counter += 1

    def SBCay(self):
        pass

    def ISCay(self):
        pass

    def SBCax(self):
        pass

    def INCax(self):
        pass

    def ISCax(self):
        pass

    def ANDidx(self):
        pass

    def EORidx(self):
        pass

    def ADCidx(self):
        pass

    def STAidx(self):
        self.store(self.accumulator, self.indexed_indirect())
        self.program_counter += 2

    def LDAidx(self):
        self.accumulator = Memory.memory[self.indexed_indirect()]
        self.A_zero_negative()
        self.program_counter += 2

    def CMPidx(self):
        pass

    def SBCidx(self):
        pass

    def SLOidx(self):
        pass

    def RLAidx(self):
        pass

    def SREidx(self):
        pass

    def RRAidx(self):
        pass

    def DCPidx(self):
        pass

    def ISCidx(self):
        pass

    def __init__(self):
        self.opcode_table = {0x00: self.BRK, 0x01: self.ORAidx, 0x02: self.STP, 0x03: self.SLOidx, 0x04: self.NOP,
                             0x05: self.ORAd, 0x06: self.ASLd, 0x07: self.SLOd, 0x08: self.PHP, 0x09: self.ORAi,
                             0x0A: self.ASL, 0x0B: self.ANCi, 0x0C: self.NOPa, 0x0D: self.ORAa, 0x0E: self.ASLa,
                             0x0F: self.SLOa,
                             0x10: self.BPLd, 0x11: self.ORAdy, 0x12: self.STP, 0x13: self.SLOdy, 0x14: self.NOPdx,
                             0x15: self.ORAdx, 0x16: self.ASLdx, 0x17: self.SLOdx, 0x18: self.CLC, 0x19: self.ORAay,
                             0x1A: self.NOP, 0x1B: self.SLOay, 0x1C: self.NOPax, 0x1D: self.ORAax, 0x1E: self.ASLax,
                             0x1F: self.SLOax,
                             0x20: self.JSRa, 0x21: self.ANDidx, 0x22: self.STP, 0x23: self.RLAidx, 0x24: self.BITd,
                             0x25: self.ANDd, 0x26: self.ROLd, 0x27: self.RLAd, 0x28: self.PLP, 0x29: self.ANDi,
                             0x2A: self.ROL, 0x2B: self.ANCi, 0x2C: self.BITa, 0x2D: self.ANDa, 0x2E: self.ROLa,
                             0x2F: self.RLAa,
                             0x30: self.BMId, 0x31: self.ANDdy, 0x32: self.STP, 0x33: self.RLAdy, 0x34: self.NOPdx,
                             0x35: self.ANDdx, 0x36: self.ROLdx, 0x37: self.RLAdx, 0x38: self.SEC, 0x39: self.ANDay,
                             0x3A: self.NOP, 0x3B: self.RLAay, 0x3C: self.NOPax, 0x3D: self.ANDax, 0x3E: self.ROLax,
                             0x3F: self.RLAax,
                             0x40: self.RTI, 0x41: self.EORidx, 0x42: self.STP, 0x43: self.SREidx, 0x44: self.NOPd,
                             0x45: self.EORd, 0x46: self.LSRd, 0x47: self.SREd, 0x48: self.PHA, 0x49: self.EORi,
                             0x4A: self.LSR, 0x4B: self.ALRi, 0x4C: self.JMPa, 0x4D: self.EORa, 0x4E: self.LSRa,
                             0x4F: self.SREa,
                             0x50: self.BVCd, 0x51: self.EORdy, 0x52: self.STP, 0x53: self.SREdy, 0x54: self.NOPdx,
                             0x55: self.EORdx, 0x56: self.LSRdx, 0x57: self.SREdx, 0x58: self.CLI, 0x59: self.EORay,
                             0x5A: self.NOP, 0x5B: self.SREay, 0x5C: self.NOPax, 0x5D: self.EORax, 0x5E: self.LSRax,
                             0x5F: self.SREax,
                             0x60: self.RTS, 0x61: self.ADCidx, 0x62: self.STP, 0x63: self.RRAidx, 0x64: self.NOPd,
                             0x65: self.ADCd, 0x66: self.RORd, 0x67: self.RRAd, 0x68: self.PLA, 0x69: self.ADCi,
                             0x6A: self.ROR, 0x6B: self.ARRi, 0x6C: self.JMPIa, 0x6D: self.ADCa, 0x6E: self.RORa,
                             0x6F: self.RRAa,
                             0x70: self.BVSd, 0x71: self.ADCdy, 0x72: self.STP, 0x73: self.RRAdy, 0x74: self.NOPdx,
                             0x75: self.ADCdx, 0x76: self.RORdx, 0x77: self.RRAdx, 0x78: self.SEI, 0x79: self.ADCay,
                             0x7A: self.NOP, 0x7B: self.RRAay, 0x7C: self.NOPax, 0x7D: self.ADCax, 0x7E: self.RORax,
                             0x7F: self.RRAax,
                             0x80: self.NOPi, 0x81: self.STAidx, 0x82: self.NOPi, 0x83: self.SAXdx, 0x84: self.STYd,
                             0x85: self.STAd, 0x86: self.STXd, 0x87: self.SAXd, 0x88: self.DEY, 0x89: self.NOPi,
                             0x8A: self.TXA, 0x8B: self.XAAi, 0x8C: self.STYa, 0x8D: self.STAa, 0x8E: self.STXa,
                             0x8F: self.SAXa,
                             0x90: self.BCCd, 0x91: self.STAdy, 0x92: self.STP, 0x93: self.AHXdy, 0x94: self.STYdx,
                             0x95: self.STAdx, 0x96: self.STXdy, 0x97: self.SAXdy, 0x98: self.TYA, 0x99: self.STAay,
                             0x9A: self.TXS, 0x9B: self.TASay, 0x9C: self.SHYax, 0x9D: self.STAax, 0x9E: self.SHXay,
                             0x9F: self.AHXay,
                             0xA0: self.LDYi, 0xA1: self.LDAidx, 0xA2: self.LDXi, 0xA3: self.LAXdx, 0xA4: self.LDYd,
                             0xA5: self.LDAd, 0xA6: self.LDXd, 0xA7: self.LAXd, 0xA8: self.TAY, 0xA9: self.LDAi,
                             0xAA: self.TAX, 0xAB: self.LAXi, 0xAC: self.LDYa, 0xAD: self.LDAa, 0xAE: self.LDXa,
                             0xAF: self.LAXa,
                             0xB0: self.BCSd, 0xB1: self.LDAdy, 0xB2: self.STP, 0xB3: self.LAXdy, 0xB4: self.LDYdx,
                             0xB5: self.LDAdx, 0xB6: self.LDXdy, 0xB7: self.LAXdy, 0xB8: self.CLV, 0xB9: self.LDAay,
                             0xBA: self.TSX, 0xBB: self.LASay, 0xBC: self.LDYax, 0xBD: self.LDAax, 0xBE: self.LDXay,
                             0xBF: self.LAXay,
                             0xC0: self.CPYi, 0xC1: self.CMPidx, 0xC2: self.NOPi, 0xC3: self.DCPidx, 0xC4: self.CPYd,
                             0xC5: self.CMPd, 0xC6: self.DECd, 0xC7: self.DCPd, 0xC8: self.INY, 0xC9: self.CMPi,
                             0xCA: self.DEX, 0xCB: self.AXSi, 0xCC: self.CPYa, 0xCD: self.CMPa, 0xCE: self.DECa,
                             0xCF: self.DCPa,
                             0xD0: self.BNEd, 0xD1: self.CMPdy, 0xD2: self.STP, 0xD3: self.DCPdy, 0xD4: self.NOPdx,
                             0xD5: self.CMPdx, 0xD6: self.DECdx, 0xD7: self.DCPdx, 0xD8: self.CLD, 0xD9: self.CMPay,
                             0xDA: self.NOP, 0xDB: self.DCPay, 0xDC: self.NOPax, 0xDD: self.CMPax, 0xDE: self.DECax,
                             0xDF: self.DCPax,
                             0xE0: self.CPXi, 0xE1: self.SBCidx, 0xE2: self.NOPi, 0xE3: self.ISCidx, 0xE4: self.CPXd,
                             0xE5: self.SBCd, 0xE6: self.INCd, 0xE7: self.ISCd, 0xE8: self.INX, 0xE9: self.SBCi,
                             0xEA: self.NOP, 0xEB: self.SBCi, 0xEC: self.CPXa, 0xED: self.SBCa, 0xEE: self.INCa,
                             0xEF: self.ISCa,
                             0xF0: self.BEQd, 0xF1: self.SBCdy, 0xF2: self.STP, 0xF3: self.ISCdy, 0xF4: self.NOPdx,
                             0xF5: self.SBCdx, 0xF6: self.INCdx, 0xF7: self.ISCdx, 0xF8: self.SED, 0xF9: self.SBCay,
                             0xFA: self.NOP, 0xFB: self.ISCay, 0xFC: self.NOPax, 0xFD: self.SBCax, 0xFE: self.INCax,
                             0xFF: self.ISCax}
