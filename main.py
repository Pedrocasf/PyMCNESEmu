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
        memory_banks = data[4] * 0x3FFF
    mem.load_data(data, 0xC000, memory_banks)

initialize()
cpu = CPU()


def cycle():
    if cpu.cycle_count >= 340:
        cpu.cycle_count = 1
    logging.debug("Program Counter: %s" %hex(cpu.program_counter) + " Operation:%s" % cpu.opcode_table[mem.memory[cpu.program_counter]].__name__ + " A:%s" % cpu.accumulator
            + " X:%s" % cpu.x + " Y:%s" % cpu.y + " SP:%s" % cpu.stack_pointer + " CYC:%s" % cpu.cycle_count + " C:%s" %cpu.carry_flag + " Z:%s" %cpu.zero_flag + " I:%s" %cpu.interrup_disable + " D:%s" %cpu.decimal_mode_flag + " B:%s" %cpu.break_command + " V:%s" %cpu.overflow_flag + " N:%s" %cpu.negative_flag)
    cpu.opcode_table[mem.memory[cpu.program_counter]]()


for i in range(0, 8992):
    cycle()
