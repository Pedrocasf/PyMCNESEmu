import numpy as np
import pygame, itertools, sched, time
from memory import Memory
from Singleton import Singleton
np.set_printoptions(threshold=np.nan)


class PPU(metaclass=Singleton):
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
        self.final_screen = pygame.display.set_mode((256, 240))
        self.pattern_table_left = np.zeros((16, 8, 16, 8), dtype=np.int32)
        self.pattern_table_right = np.zeros((16, 8, 16, 8), dtype=np.int32)
        self.PPUCTRL = 0
        self.PPUMASK = 0
        self.PPUSTATUS = 0
        self.OAMADDR = 0
        self.OAMDATA = 0 
        self.PPUSCROLL = 0
        self.PPUADDR = 0
        self.PPUDATA = 0
        self.SQ1_VOL = 0
        self.SQ1_SWEEP = 0
        self.SQ1_LO = 0
        self.SQ1_HI = 0
        self.SQ2_VOL = 0
        self.SQ2_SWEEP = 0
        self.SQ2_LO = 0
        self.SQ2_HI = 0
        self.TRI_LINEAR = 0
        self.TRI_LO = 0
        self.TRI_HI = 0
        self.NOISE_VOL = 0
        self.NOISE_LO = 0
        self.NOISE_HI = 0
        self.DMC_FREQ = 0
        self.DMC_RAW = 0
        self.DMC_START = 0
        self.DMC_LEN = 0
        self.OAMDMA = 0
        self.SND_CHN = 0
        self.JOY1 = 0
        self.JOY2 = 0
        self.address = 0x2000
        self.bit = "high"
        self.nmi_to_happen = True
        self.show_tiles = False
        self.clock  = pygame.time.Clock()

    def read(self, address):
        if 0x1FFF < address < 0x4000:
            address = ((address - 0x2000) % 8) + 0x2000
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
        elif 0x3FFF < address < 0x4018:
            if address == 0x4000:
                Memory.memory[address] = self.SQ1_VOL
            elif address == 0x4001:
                Memory.memory[address] = self.SQ1_SWEEP
            elif address == 0x4002:
                Memory.memory[address] = self.SQ1_LO
            elif address == 0x4003:
                Memory.memory[address] = self.SQ1_HI
            elif address == 0x4004:
                Memory.memory[address] = self.SQ2_VOL
            elif address == 0x4005:
                Memory.memory[address] = self.SQ2_SWEEP
            elif address == 0x4006:
                Memory.memory[address] = self.SQ2_LO
            elif address == 0x4007:
                Memory.memory[address] = self.SQ2_HI
            elif address == 0x4008:
                Memory.memory[address] = self.TRI_LINEAR
            elif address == 0x4009:
                Memory.memory[address] = 0
            elif address == 0x400A:
                Memory.memory[address] = self.TRI_LO
            elif address == 0x400B:
                Memory.memory[address] = self.TRI_HI
            elif address == 0x400C:
                Memory.memory[address] = self.NOISE_VOL
            elif address == 0x400D:
                Memory.memory[address] = 0
            elif address == 0x400E:
                Memory.memory[address] = self.NOISE_LO
            elif address == 0x400F:
                Memory.memory[address] = self.NOISE_HI
            elif address == 0x4010:
                Memory.memory[address] = self.DMC_FREQ
            elif address == 0x4011:
                Memory.memory[address] = self.DMC_RAW
            elif address == 0x4012:
                Memory.memory[address] = self.DMC_START
            elif address == 0x4013:
                Memory.memory[address] = self.DMC_LEN
            elif address == 0x4014:
                Memory.memory[address] = self.OAMDMA
            elif address == 0x4015:
                Memory.memory[address] = self.SND_CHN
            elif address == 0x4016:
                Memory.memory[address] = self.JOY1
            elif address == 0x4017:
                Memory.memory[address] = self.JOY2
                

    def write(self, address, result):
        if 0x1FFF < address < 0x4000:
            address = ((address - 0x2000) % 8) + 0x2000
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
                Memory.object_attribute_memory[self.OAMADDR] = self.OAMDATA
            elif address == 0x2005:
                self.PPUSCROLL = result
            elif address == 0x2006:
                self.PPUADDR = result
                if self.bit == "high":
                    self.address = self.PPUADDR << 8
                    self.bit = "low"
                elif self.bit == "low":
                    self.address += self.PPUADDR
                    self.bit = "high"
            elif address == 0x2007:
                self.PPUDATA = result
                Memory.ppu_memory[self.address] = self.PPUDATA
                self.address += (((self.PPUCTRL & 0b00000100) >> 2) * 31) + 1        
        elif 0x3FFF < address < 0x4018:
            if address == 0x4000:
                self.SQ1_VOL = result
            elif address == 0x4001:
                self.SQ1_SWEEP = result
            elif address == 0x4002:
                self.SQ1_LO = result
            elif address == 0x4003:
                self.SQ1_HI = result
            elif address == 0x4004:
                self.SQ2_VOL = result
            elif address == 0x4005:
                self.SQ2_SWEEP = result
            elif address == 0x4006:
                self.SQ2_LO = result
            elif address == 0x4007:
                self.SQ2_HI = result
            elif address == 0x4008:
                self.TRI_LINEAR = result
            elif address == 0x400A:
                self.TRI_LO = result
            elif address == 0x400B:
                self.TRI_HI = result
            elif address == 0x400C:
                self.NOISE_VOL = result
            elif address == 0x400E:
                self.NOISE_LO = result
            elif address == 0x400F:
                self.NOISE_HI = result
            elif address == 0x4010:
                self.DMC_FREQ = result
            elif address == 0x4011:
                self.DMC_RAW = result
            elif address == 0x4012:
                self.DMC_START = result
            elif address == 0x4013:
                self.DMC_LEN = result
            elif address == 0x4014:
                self.OAMDMA = result
                for i in range(0xFF):
                    Memory.object_attribute_memory[i] = Memory.memory[(self.OAMDMA << 8) + i]
            elif address == 0x4015:
                self.SND_CHN = result
            elif address == 0x4016:
                self.JOY1 = result
            elif address == 0x4017:
                self.JOY2 = result
        else:
            Memory.memory[address] = result

    def decode(self):
        for w, x, y, z in itertools.product(*map(range, (16, 8, 16, 8))):
            self.pattern_table_left[w, x, y, z] = (((int(Memory.ppu_memory[x + (16 * y) + (w * 256)]) << z) & 0b000000010000000) >> 7) + (((int(Memory.ppu_memory[(x + 8) + (y * 16) + (w * 256)]) << z) & 0b0000000010000000) >> 6)
            self.pattern_table_right[w, x, y, z] = (((int(Memory.ppu_memory[0x1000 + x + (16 * y) + (w * 256)]) << z) & 0b0000000010000000) >> 7) + (((int(Memory.ppu_memory[0x1000 + (x + 8) + (y * 16) + (w * 256)]) << z) & 0b0000000010000000) >> 6)
        self.pattern_table_left = np.fliplr(np.rot90(((self.pattern_table_left.astype(int).reshape(128, 8*16)) * 85), 3))
        self.pattern_table_right = np.fliplr(np.rot90(((self.pattern_table_right.astype(int).reshape(128, 8*16)) * 85), 3))

    def render_frame(self):
            self.PPUSTATUS = self.PPUSTATUS & 0b011111111
            base_nametable_address = (((self.PPUCTRL & 0b00000011) * 0x400) + 0x2000)
            for i in range(960):
                x = ((Memory.ppu_memory[i+base_nametable_address]) & 0x0F)
                y = ((Memory.ppu_memory[i+base_nametable_address]) & 0xF0) >> 4
                if self.PPUCTRL & 0b00010000 == 0b00010000:
                    surface = self.pattern_table_right[x * 8:(x * 8) + 8, y * 8:(y * 8) + 8]
                    surface = pygame.pixelcopy.make_surface(surface)
                    self.final_screen.blit(surface, ((i%32)*8, (i//32)*8))
                else:
                    surface = self.pattern_table_left[x * 8:(x * 8) + 8, y * 8:(y * 8) + 8]
                    surface = pygame.pixelcopy.make_surface(surface)
                    self.final_screen.blit(surface, ((i%32)*8, (i//32)*8))
            self.PPUSTATUS &= 0b11011111 
            for i in range(64):
                byte_0 = Memory.object_attribute_memory[i*4]
                byte_1 = Memory.object_attribute_memory[(i*4)+1]
                byte_2 = Memory.object_attribute_memory[(i*4)+2]
                byte_3 = Memory.object_attribute_memory[(i*4)+3]
                sprite_x = (byte_1 & 0xFF) >>4
                sprite_y = byte_1 & 0x0FF 
                if self.PPUCTRL & 0b00010000 == 0b00010000:
                    sprite = self.pattern_table_right[sprite_x * 8:(sprite_x * 8) + 8, sprite_y * 8:(sprite_y * 8) + 8]
                    sprite = pygame.pixelcopy.make_surface(sprite)
                    self.final_screen.blit(surface, (byte_3, byte_0))
                else:
                    surface = self.pattern_table_left[sprite_x * 8:(sprite_x * 8) + 8, sprite_y * 8:(sprite_y * 8) + 8]
                    surface = pygame.pixelcopy.make_surface(surface)
                    self.final_screen.blit(surface, (byte_3, byte_0))
            pygame.display.update()

    def enter_VBlank(self):
        self.PPUSTATUS = self.PPUSTATUS | 0b10000000

    def sprite_evaluation(self):
        self.PPUSTATUS |= 0b00100000
	
