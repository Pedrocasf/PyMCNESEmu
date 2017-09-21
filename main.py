import sys
import logging
from main_memory import Memory
from central_processing_unit import CPU
from picture_processing_unit import PPU
from audio_processing_unit import APU
mem = Memory()
logging.basicConfig(level=logging.DEBUG)


def initialize():
    with open("nestest.nes", mode="rb") as f:
        data = f.read()
        memory_banks = data[4] * 0x4000
    mem.load_data(data, 0xC000, memory_banks, 0x10)


initialize()
cpu = CPU()
ppu = PPU()
apu = APU()


def cycle():
    print(" %s" % hex(cpu.program_counter)[2:].upper() + " %s" % cpu.opcode_table[mem.memory[cpu.program_counter]].__name__ + " A:%s" % (hex(cpu.accumulator)[2:].upper()).zfill(2) + " X:%s" % (hex(cpu.x)[2:].upper()).zfill(2) + " Y:%s" % (hex(cpu.y)[2:].upper()).zfill(2) + " P:%s" % hex(cpu.processor_status)[2:].upper()  + " P(bin):%s" % (bin(cpu.processor_status)[2:]).zfill(8) + " CYC: 0")
    cpu.opcode_table[mem.memory[cpu.program_counter]]()
    for ppuc in range(0,2):
        ppu.cycle()
    apu.cycle()

for i in range(0, 8991):
    cycle()
    if cpu.opcode_table[mem.memory[cpu.program_counter]].__name__ == "BRK":
        break