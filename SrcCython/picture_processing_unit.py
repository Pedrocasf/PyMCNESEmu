import pyglet
import threading
from pyglet.gl import *
from main_memory import Memory


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
        pyglet.app.run()

    def V_blank(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glBegin(GL_TRIANGLES)
        glVertex2f(0, 0)
        glVertex2f(self.window.width, 0)
        glVertex2f(self.window.width, self.window.height)
        threading.Timer((1/60), self.V_blank).start()
        print("V_blank")
