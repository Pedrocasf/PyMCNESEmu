import threading, time, sys
sys.setrecursionlimit(2147483647)
from memory import Memory
from central_processing_unit import CPU
from picture_processing_unit import PPU
from audio_processing_unit import APU
mem = Memory()


def initialize():
    with open(sys.argv[1], mode="rb") as f:
        data = f.read()
    mapper = ((data[0x6] & 0b11110000) >> 4) | ((data[0x7]) & 0b11110000)
    mem.load_data(data, mapper, 0x4000)
initialize()
cpu = CPU()
ppu = PPU()
apu = APU()
cpu.program_counter = ((mem.memory[0xFFFD] << 8) + mem.memory[0xFFFC])
ppu.decode()
print("%s" % hex(cpu.program_counter)[2:].upper().zfill(4) + " %s" % (hex(Memory.memory[cpu.program_counter])[2:].upper()).zfill(2) + " A: %s" % (hex(cpu.accumulator)[2:].upper()).zfill(2) + " X: %s" % (hex(cpu.x)[2:].upper()).zfill(2) + " Y: %s" % (hex(cpu.y)[2:].upper()).zfill(2) + " P: %s " % hex(cpu.processor_status)[2:].upper() + "SP: %s " % hex((cpu.stack_pointer - 0x100))[2:].upper().zfill(2) + " P(bin):%s" % (bin(cpu.processor_status)[2:]).zfill(8) + " CYC: 0")


def cycle():
    ppu.nmi_alread_happend = False
    while cpu.cycles_left >= 0:
        ppu.OAMDMA_old = ppu.OAMDMA
        cpu.opcode_table[mem.memory[cpu.program_counter]]()
        if ppu.OAMDMA != ppu.OAMDMA_old:
            ppu.DMA()
        if cpu.program_counter == 0xC000:
            exit()
    cpu.cycles_left = 6820
    ppu.enter_VBlank()
    while cpu.cycles_left >= 0:
        if cpu.program_counter == 0xC000:
            exit()
        cpu.opcode_table[mem.memory[cpu.program_counter]]()
        if (ppu.PPUCTRL & 0b10000000) == 0b10000000 and ppu.nmi_to_happen:
            ppu.nmi_to_happen = False
            cpu.NMI()
    ppu.render_frame()
    threading.Timer((1 / 60), cycle).start()

cycle()
