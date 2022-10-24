# © Damien Kazewych 2020
# I *SAW* what you were doing

#    /|   /|   /|   /|   /
#   / |  / |  / |  / |  /  get it? it's a saw wave
#  /  | /  | /  | /  | / 
# /   |/   |/   |/   |/

import multiprocessing
from multiprocessing import Value
from pyo import *

import os

class VoiceProcessor(multiprocessing.Process):
    def __init__(self):
        super(VoiceProcessor, self).__init__()
        self.daemon = True
        self._terminated = False
        self.val = Value('i', -400)
        self.audio_source = Value('i', 0)
        self.current_source = 0
        self.update_flag = Value('b', False)

    def update_ampl(self, val):
        self.val.value = val

    def run(self):
        # All code that should run on a separated
        # core must be created in the run() method.
        #self.server = Server(duplex=1, ichnls=1) #do this on everything else
        #self.server = Server(ichnls=1, sr=22050, buffersize=4096) #do this on pi
        self.server = Server(duplex=1, ichnls=1, nchnls = 2, buffersize=2048)
        #self.server = Server(ichnls=1, buffersize=4096)
        self.server.setInputDevice(2) #2
        self.server.setOutputDevice(0) #1 on mac, 0 on pi
        self.server.boot()


        #a = SfPlayer("../Test1.wav", speed=[1], mul=1)
        sf = SfPlayer("../Test1.wav", speed=[1], mul=0.33)
        sf.stop()
        a = Input(mul=1)
        fil = FreqShift(a, shift=self.val.value, mul=0.8)
        #fil = Biquad(f, freq=2000, q=1, type=0)


        #b = Freeverb(fil, size=[.1,.1], damp=.2, bal=.3)
        #d = Degrade(fil, bitdepth=32, srscale=0.2, mul=0.8)
        #b = Chorus(fil, depth=[1.5,1.6], feedback=0.65, bal=0.8)
        harm = Harmonizer(fil, transpo=-0.33)
        pan = Pan(harm).out()
        #sin = Sine(mul=0.25).out()
        #spec = PeakAmp(a,function=self.update_ampl)
        self.server.start()
        # Keeps the process alive...
        while not self._terminated:
            time.sleep(0.001)
            if self.update_flag.value:
                fil.setShift(self.val.value)
                #fil.setInput(SfPlayer("../Bustin.wav", speed=[1], mul=1))
                self.update_flag.value = False
                if self.audio_source.value != self.current_source:
                    self.current_source = self.audio_source.value
                    if self.audio_source.value == 0:
                        #fil.setInput(Input(mul=0.6))
                        sf.stop()
                        pan.setInput(harm)
                        #fil.setInput(a)
                    else:
                        pan.setInput(sf)
                        #fil.setInput(sf)
                        sf.setOffset(59)
                        sf.play()

        self.server.stop()

    def stop(self):
        self._terminated = True
