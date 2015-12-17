#!python2
import math, struct, time, itertools
from operator import mul

import mido
mido.set_backend('mido.backends.pygame')
keyboard = mido.get_input_names()[0]

import pyaudio
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

class generatorBase():
	frequency = 44100.
	channels = 2
	velocity_max = 128.#the scale/coeficient
	def __init__(self):
		self.notes = []#[i] = [note id, velocity]
		self.pos = 0#position
	
	#input
	def set_note(self, id, velocity):
		if id not in map(self._map_id, self.notes):
			self.notes.append([id, float(velocity)/(self.velocity_max*2)])
		else:
			for i, e in enumerate(self.notes):
				if e[0] == id:
					self.notes[i][1] = float(velocity)/(self.velocity_max*2)
					break
	def stop_note(self, id):
		for i, e in enumerate(self.notes):
				if e[0] == id:
					del self.notes[i]
					break
	
	#def generator:
	def get_frames(self, chunk):
		out = []
		
		#speedup the name lookup a little
		chn = self.channels
		f = self.frequency
		notes = tuple(self.notes)
		
		if len(notes):
			for i in map(float, xrange(self.pos, self.pos+chunk)):# / self.channels):
				period = i/f
				frame = sum(self.tone_generator(period * self.get_freq(n)) * v for n, v in notes)
				for _ in xrange(chn):
					out.append(frame if -1 <= frame <= 1 else frame/abs(frame))
					#out.append(frame)
		else:
			out = [0.]*chunk*chn
		self.pos += chunk
		
		return self.pack(out)
	
	#2 be replaced by children:
	def tone_generator(self, p):#a period is from 0.0 to 1.0. p is not run trough modulo 1 first
		return 0#placeholder
	def get_freq(self, note):#tune for c4 = 60 and A = 440Hz
		return 440.*math.pow(2, float(note-60)/12.)
	
	#private:
	def _map_id(self, i):
		return i[0]
	def pack(self, frames):#this handles bit-depth aswell. "frame" is a float between -1 and 1
		h = "h"
		p = struct.pack
		return "".join((p(h, int(i*0x7FFF)) for i in frames))
		#return struct.pack("H", int((frame+1)*0x7FFF))
	def pack_bak(self, frames):
		l = len(frames)
		scaled = map(mul, frames, [0x7FFF]*l)
		inted = map(int, scaled)
		return struct.pack("h"*len(frames), *inted)
		#return struct.pack("H", int((frame+1)*0x7FFF))
	

class sineGenerator(generatorBase):
	def tone_generator(self, p):
		return math.sin(p*math.pi*2)#slow, names, ech. it hurts

class squareGenerator(generatorBase):
	def tone_generator(self, p):
		return 1. if (p%1) > 0.5 else -1.

class jigGenerator(generatorBase):#is this the right name? derp
	def tone_generator(self, p):
		return (p%1)*2. - 1.

#todo: sawblade and more fun stuff

def main(generator):
	gen = generator()
	renders = []#since its mutable
	last10 = []
	
	def callback(in_data, frame_count, time_info, status_flags):
		renders.append(None)
		#print 1,
		return (gen.get_frames(frame_count), pyaudio.paContinue)
	pa = pyaudio.PyAudio()
	stream =pa.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					output=True,
					frames_per_buffer=CHUNK,
					stream_callback=callback)
	
	last_clock = -1
	with mido.open_input(keyboard) as f:
		for i in f: 
			if i.type == "clock":
				h = time.time()-last_clock
				last_clock = time.time()
				if h > 0:
					h = round(1./h, 2)
				else:
					h = None
				
				last10.append(len(renders))
				del renders[:]
				if len(last10)>10: del last10[0]
				
				print "\nclock @", h, "Hz.  Render @", h*sum(last10)/10, "/", round(float(RATE)/CHUNK, 2), "Hz ",
				
				
			elif i.type == "note_on":
				if i.velocity == 0:
					gen.stop_note(i.note)
				else:
					gen.set_note(i.note, i.velocity)
				print "note (%i, %i)" % (i.note, i.velocity),


if __name__ == "__main__":
	#main(jigGenerator)
	main(squareGenerator)
	#main(sineGenerator)








