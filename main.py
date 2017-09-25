import sys
from main_memory import Memory
from central_processing_unit import CPU
from picture_processing_unit import PPU
from audio_processing_unit import APU
mem = Memory()


def initialize():
    with open(sys.argv[1], mode="rb") as f:
        data = f.read()
        memory_banks = data[4] * 0x4000
    mem.load_data(data, 0xC000, memory_banks, 0x10)


initialize()
cpu = CPU()
ppu = PPU()
apu = APU()


def cycle():
    cpu.opcode_table[mem.memory[cpu.program_counter]]()
    print("%s" % hex(cpu.program_counter)[2:].upper().zfill(4) + " %s" % cpu.opcode_table[mem.memory[cpu.program_counter]].__name__ + " A: %s" % (hex(cpu.accumulator)[2:].upper()).zfill(2) + " X: %s" % (hex(cpu.x)[2:].upper()).zfill(2) + " Y: %s" % (hex(cpu.y)[2:].upper()).zfill(2) + " P: %s " % hex(cpu.processor_status)[2:].upper()  + "SP: %s " %hex((cpu.stack_pointer - 0x100))[2:].upper().zfill(2) +" P(bin):%s" % (bin(cpu.processor_status)[2:]).zfill(8) + " CYC: 0")
    for ppuc in range(0,2):
        ppu.cycle()
    apu.cycle()

print(" %s" % hex(cpu.program_counter)[2:].upper().zfill(4) + " %s" % cpu.opcode_table[mem.memory[cpu.program_counter]].__name__ + " A: %s" % (hex(cpu.accumulator)[2:].upper()).zfill(2) + " X: %s" % (hex(cpu.x)[2:].upper()).zfill(2) + " Y: %s" % (hex(cpu.y)[2:].upper()).zfill(2) + " P: %s " % hex(cpu.processor_status)[2:].upper() + "SP: %s " % hex((cpu.stack_pointer - 0x100))[2:].upper().zfill(2) + " P(bin):%s" % (bin(cpu.processor_status)[2:]).zfill(8) + " CYC: 0")

for i in range(9000):
    cycle()
    if cpu.opcode_table[mem.memory[cpu.program_counter]].__name__ == "BRK":
        break
