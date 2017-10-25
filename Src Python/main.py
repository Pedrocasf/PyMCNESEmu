import sys
from numba import jit
from threading import Thread
from memory import Memory
from central_processing_unit import CPU
from picture_processing_unit import PPU
from audio_processing_unit import APU
mem = Memory()


def initialize():
    with open(sys.argv[1], mode="rb") as f:
        data = f.read()
    mapper = ((data[0x6] & 0b11110000) >> 4) | (data[0x7] & 0b11110000)
    mem.load_data(data, mapper, 0x4000)
initialize()
cpu = CPU()
ppu = PPU()
apu = APU()
cpu.program_counter = ((mem.memory[0xFFFD] << 8) + mem.memory[0xFFFC])




def PPU_cycle():
    while True:
        ppu.PPUCTRL = mem.memory[0x2000]
        ppu.PPUMASK = mem.memory[0x2001]
        ppu.PPUSTATUS = mem.memory[0x2002]
        ppu.OAMADDR = mem.memory[0x2003]
        ppu.OAMDATA = mem.memory[0x2004]
        ppu.PPUSCROLL = mem.memory[0x2005]
        ppu.PPUADDR = mem.memory[0x2006]
        ppu.PPUDATA = mem.memory[0x2007]
        ppu.OAMDMA = mem.memory[0x4014]


def APU_cycle():
    pass


def cycle():
    for i in range(8991):
        cpu.opcode_table[mem.memory[cpu.program_counter]]()


t_cpu = Thread(target=cycle)
t_ppu = Thread(target=PPU_cycle)
t_apu = Thread(target=APU_cycle)
t_ppu.setDaemon(True)
t_apu.setDaemon(True)
t_cpu.start()
t_ppu.start()
t_apu.start()
ppu.V_blank()
print(mem.memory[0x210], mem.memory[3])