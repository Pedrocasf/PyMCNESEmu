import sys, logging
from multiprocessing import Process
from memory import Memory
from central_processing_unit import CPU
from picture_processing_unit import PPU
from audio_processing_unit import APU
mem = Memory()
logging.basicConfig(level=logging.DEBUG)


def initialize():
    with open("nestest.nes", mode="rb") as f:
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
    logging.debug(time.time())
    for i in range(1789773):
        cpu.opcode_table[mem.memory[cpu.program_counter]]()
    logging.debug(time.time())
    sys.exit()
    
if __name__ == '__main__':
    p_cpu = Process(target=cycle)
    p_ppu = Process(target=PPU_cycle)
    p_apu = Process(target=APU_cycle)
    p_cpu.start()
    p_ppu.start()
    p_apu.start()
    p_cpu.join()
    p_ppu.join()
    p_apu.join()
    ppu.V_blank()
