import pyglet , logging
import threading, datetime
from pyglet.gl import *
from memory import Memory
import datetime, threading, time
logging.basicConfig(level=logging.DEBUG)


class PPU:
    window = pyglet.window.Window()
    context = window.context
    config = window.config


    def __init__(self):
        self.PPUCTRL = Memory.memory[0x2000]
        self.PPUMASK = Memory.memory[0x2001]
        self.PPUSTATUS = Memory.memory[0x2002]
        self.OAMADDR = Memory.memory[0x2003]
        self.OAMDATA = Memory.memory[0x2004]
        self.PPUSCROLL = Memory.memory[0x2005]
        self.PPUADDR = Memory.memory[0x2006]
        self.PPUDATA = Memory.memory[0x2007]
        self.OAMDMA = Memory.memory[0x4014]

    
    def V_blank(self):
        threading.Timer((1/60), self.V_blank).start()
        logging.debug("V_blank")
        
