import sched, time, sys
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
print(hex(cpu.program_counter))
s = sched.scheduler(time.time, time.sleep)
ppu.decode()

def cycle():
    for i in range(14815):
        cpu.opcode_table[mem.memory[cpu.program_counter]]()
        print("%s" % hex(cpu.program_counter)[2:].upper().zfill(4) + " %s" % (hex(Memory.memory[cpu.program_counter])[2:].upper()).zfill(2) + " A: %s" % (hex(cpu.accumulator)[2:].upper()).zfill(2) + " X: %s" % (hex(cpu.x)[2:].upper()).zfill(2) + " Y: %s" % (hex(cpu.y)[2:].upper()).zfill(2) + " P: %s " % hex(cpu.processor_status)[2:].upper() + "SP: %s " % hex((cpu.stack_pointer - 0x100))[2:].upper().zfill(2) + " P(bin):%s" % (bin(cpu.processor_status)[2:]).zfill(8) + " CYC: 0")
        ppu.OAMDMA_old = ppu.OAMDMA
        ppu.PPUCTRL = mem.memory[0x2000]
        ppu.PPUMASK = mem.memory[0x2001]
        ppu.PPUSTATUS = mem.memory[0x2002]
        ppu.OAMADDR = mem.memory[0x2003]
        ppu.OAMDATA = mem.memory[0x2004]
        ppu.PPUSCROLL = mem.memory[0x2005]
        ppu.PPUADDR = mem.memory[0x2006]
        ppu.PPUDATA = mem.memory[0x2007]
        ppu.OAMDMA = mem.memory[0x4014]
        if ppu.OAMDMA != ppu.OAMDMA_old:
            ppu.DMA()
        if cpu.program_counter == 0xC0ED:
            exit()
    print(ppu.PPUSTATUS)
    ppu.render_frame()
    cpu.NMI()
    s.enter((1/60), 1, cycle, ())

s.enter((1/60), 1, cycle, ())
s.run()
print(mem.memory[0x210], mem.memory[3])