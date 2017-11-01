import numpy as np
import pygame, itertools, sched, time
from memory import Memory
from Singleton import Singleton
np.set_printoptions(threshold=np.nan)

class PPU(metaclass= Singleton):
    palletes = [(0x66, 0x66, 0x66), (0x00, 0x2a, 0x88), (0x14, 0x12, 0xa7), (0x3b, 0x00, 0xa4),
    (0x5c, 0x00, 0x7e), (0x6e, 0x00, 0x40), (0x6c, 0x06, 0x00), (0x56, 0x1d, 0x00),
    (0x33, 0x35, 0x00), (0x0b, 0x48, 0x00), (0x00, 0x52, 0x00), (0x00, 0x4f, 0x08),
    (0x00, 0x40, 0x4d), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00),
    (0xad, 0xad, 0xad), (0x15, 0x5f, 0xd9), (0x42, 0x40, 0xff), (0x75, 0x27, 0xfe),
    (0xa0, 0x1a, 0xcc), (0xb7, 0x1e, 0x7b), (0xb5, 0x31, 0x20), (0x99, 0x4e, 0x00),
    (0x6b, 0x6d, 0x00), (0x38, 0x87, 0x00), (0x0c, 0x93, 0x00), (0x00, 0x8f, 0x32),
    (0x00, 0x7c, 0x8d), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00),
    (0xff, 0xfe, 0xff), (0x64, 0xb0, 0xff), (0x92, 0x90, 0xff), (0xc6, 0x76, 0xff),
    (0xf3, 0x6a, 0xff), (0xfe, 0x6e, 0xcc), (0xfe, 0x81, 0x70), (0xea, 0x9e, 0x22),
    (0xbc, 0xbe, 0x00), (0x88, 0xd8, 0x00), (0x5c, 0xe4, 0x30), (0x45, 0xe0, 0x82),
    (0x48, 0xcd, 0xde), (0x4f, 0x4f, 0x4f), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00),
    (0xff, 0xfe, 0xff), (0xc0, 0xdf, 0xff), (0xd3, 0xd2, 0xff), (0xe8, 0xc8, 0xff),
    (0xfb, 0xc2, 0xff), (0xfe, 0xc4, 0xea), (0xfe, 0xcc, 0xc5), (0xf7, 0xd8, 0xa5),
    (0xe4, 0xe5, 0x94), (0xcf, 0xef, 0x96), (0xbd, 0xf4, 0xab), (0xb3, 0xf3, 0xcc),
    (0xb5, 0xeb, 0xf2), (0xb8, 0xb8, 0xb8), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00)]

    def __init__(self):
        self.pattern_table_screen = pygame.display.set_mode((1024, 480))
        self.final_screen = pygame.display.set_mode((1024, 960))
        self.pattern_table_left = np.zeros((16, 8, 16, 8))
        self.pattern_table_right = np.zeros((16, 8, 16, 8))
        self.PPUCTRL = Memory.memory[0x2000]
        self.PPUMASK = Memory.memory[0x2001]
        self.PPUSTATUS = Memory.memory[0x2002]
        self.OAMADDR = Memory.memory[0x2003]
        self.OAMDATA = Memory.memory[0x2004]
        self.PPUSCROLL = Memory.memory[0x2005]
        self.PPUADDR = Memory.memory[0x2006]
        self.PPUDATA = Memory.memory[0x2007]
        self.OAMDMA = Memory.memory[0x4014]
        self.address = 0x2000
        self.bit = "low"

    def read(self, address):
        if 0x1FFF < address < 0x2008 or 0x3FFF < address < 0x4018:
            if address == 0x2000:
                Memory.memory[address] = self.PPUCTRL
            elif address == 0x2001:
                Memory.memory[address] = self.PPUMASK
            elif address == 0x2002:
                Memory.memory[address] = self.PPUSTATUS
            elif address == 0x2003:
                Memory.memory[address] = self.OAMADDR
            elif address == 0x2004:
                Memory.memory[address] = self.OAMDATA
            elif address == 0x2005:
                Memory.memory[address] = self.PPUSCROLL
            elif address == 0x2006:
                Memory.memory[address] = self.PPUADDR
            elif address == 0x2007:
                Memory.memory[address] = self.PPUDATA

    def write(self, address, result):
        if 0x1FFF < address < 0x2008 or 0x3FFF < address < 0x4018:
            if address == 0x2000:
                self.PPUCTRL = result
            elif address == 0x2001:
                self.PPUMASK = result
            elif address == 0x2002:
                pass
            elif address == 0x2003:
                self.OAMADDR = result
            elif address == 0x2004:
                self.OAMDATA = result
            elif address == 0x2005:
                self.PPUSCROLL = result
            elif address == 0x2006:
                if self.bit == "low":
                    self.PPUADDR = result
                    self.address = self.PPUADDR
                    self.bit = "high"
                elif self.bit == "high":
                    self.address = self.PPUADDR << 8
                    self.bit = "low"
            elif address == 0x2007:
                self.PPUDATA = result
                Memory.ppu_memory[self.address] = self.PPUDATA
                self.address += (((self.PPUCTRL & 0b00000100) >> 2) * 31) + 1
        else:
            Memory.memory[address] = result

    def ppu_write(self):
        Memory.ppu_memory[self.address] = self.PPUDATA
        self.address += (((self.PPUCTRL & 0b00000100) >> 2) * 31) + 1

    def DMA(self):
        self.OAMDMA_old = self.OAMDMA
        for i in range(0xFF):
            Memory.object_attribute_memory[i] = Memory.memory[(self.OAMDMA << 8) + i]
        print(Memory.object_attribute_memory)

    def decode(self):
        for w, x, y, z in itertools.product(*map(range, (16, 8, 16, 8))):
            self.pattern_table_left[w, x, y, z] = (((int(Memory.ppu_memory[x + (16 * y) + (w * 256)]) << z) & 0b000000010000000) >> 7) + (((int(Memory.ppu_memory[(x + 8) + (y * 16) + (w * 256)]) << z) & 0b0000000010000000) >> 6)
            self.pattern_table_right[w, x, y, z] = (((int(Memory.ppu_memory[0x1000 + x + (16 * y) + (w * 256)]) << z) & 0b0000000010000000) >> 7) + (((int(Memory.ppu_memory[0x1000 + (x + 8) + (y * 16) + (w * 256)]) << z) & 0b0000000010000000) >> 6)
        self.pattern_table_left = np.fliplr(np.rot90(((self.pattern_table_left.astype(int).reshape(128, 8*16)) * 85), 3))
        self.pattern_table_right = np.fliplr(np.rot90(((self.pattern_table_right.astype(int).reshape(128, 8*16)) * 85), 3))

    def render_frame(self):
        base_nametable_address = ((self.PPUCTRL & 0b00000011) * 0x400) + 0x2000
        for i in range(33):
            x = ((Memory.ppu_memory[i+base_nametable_address]) & 0x0F)
            y = ((Memory.ppu_memory[i+base_nametable_address]) & 0xF0)
            if self.PPUCTRL & 0b00010000 == 0b00010000:
                surface = (self.pattern_table_right[x * 8:(x * 8) + 8, y * 8:(y * 8) + 8])
                surface = pygame.pixelcopy.make_surface(surface)
                surface = pygame.transform.scale(surface, (64, 64))
                self.final_screen.blit(surface, (x * 64, y * 64))
            else:
                surface = self.pattern_table_left[x * 8:(x * 8) + 8, y * 8:(y * 8) + 8]
                surface = pygame.pixelcopy.make_surface(surface)
                surface = pygame.transform.scale(surface, (64, 64))
                self.final_screen.blit(surface, (x * 64, y * 64))
        pygame.display.update()
        self.PPUSTATUS &= 0b11011111

    def enter_VBlank(self):
        self.PPUSTATUS = self.PPUSTATUS | 0b10000000

    def sprite_evaluation(self):
        self.PPUSTATUS |= 0b00100000
