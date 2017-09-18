import sys
import logging
from main_memory import Memory
from central_processing_unit import CPU
from picture_processing_unit import PPU
from audio_processing_unit import APU
mem = Memory()
logging.basicConfig(level=logging.DEBUG)


def initialize():
    with open(sys.argv[1], mode="rb") as f:
        data = f.read()
        memory_banks = data[4] * 0x4000
    mem.load_data(data, 0xC000, memory_banks)


initialize()
cpu = CPU()
ppu = PPU()
apu = APU()


def cycle():
    if cpu.cycle_count >= 340:
        cpu.cycle_count = 1
    logging.debug("Program Counter: %s" %hex(cpu.program_counter) + " Operation:%s" %
                  cpu.opcode_table[mem.memory[cpu.program_counter]].__name__ + " A:%s" % hex(cpu.accumulator)
                    + " X:%s" % hex(cpu.x) + " Y:%s" % hex(cpu.y) + " SP:%s" % hex(cpu.stack_pointer) + " CYC:%s" % cpu.cycle_count +
                   " Processor Status:%s" % bin(cpu.processor_status))
    cpu.opcode_table[mem.memory[cpu.program_counter]]()
    for ppuc in range(0,2):
        ppu.cycle()
    apu.cycle()

for i in range(0, 8991):
    cycle()
print(mem.memory[0x2])
print(mem.memory[0x3])
