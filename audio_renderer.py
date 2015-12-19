import pyaudio, math, itertools, struct, random

#global settings
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

#internal globals
renders = 0

#waves:
def sineWave(p):
		return math.sin(p*math.pi*2)#slow, names, ech. it hurts
def squareWave(p):
		return 1. if (p%1) > 0.5 else -1.
def sawtoothWave(p):
		return (p%1)*2. - 1.
def triangleWave(p):
		p = (p%1)*4
		if p <= 1:
			return p
		elif p >= 3:
			return p-4
		else:
			return 2-p
def dafuqWave(p):#a happy little accident
		p = (p%1)*4
		if p <= 1:
			return p
		elif p >= 3:
			return p-2
		else:
			return 1-p
#modifiers:
def AddAttack2Wave(wave, length=1.0):#length in kinda seconds untill the velocity is halved
	l = 440.0 * length
	def NewWave(p):
		return wave(p)/(1. + p/l)
	return NewWave
def AddCrush2Wave(wave, levels=100):#length in kinda seconds untill the velocity is halved
	def NewWave(p):
		return float(int(wave(p)*levels))/levels
	return NewWave
#perc
def highhatBeat(p):#short percussion
	#return (random.random()*2-1)/(1+p/10)
	return (random.random()*2-1) * max(1-p/30, 0)
def snareBeat(p):
	return min(max((random.random()*2-1) * max(2-p/24, 0), -1), 1)
def drumBeat(p):
	return triangleWave(math.sqrt(1.8*p))*1.2

	
#generator
class generator():
	frequency = float(RATE)
	channels = 2
	
	instruments = [sineWave for _ in xrange(16)]#15 channels instead?
	
	def __init__(self):
		self.notes = [set() for _ in xrange(16)]
		self.note = []#[i] = [channel, note, velocity, start pos, instrument, frequency]
		self.pos = 0#position
	
	#input
	def set_note(self, channel, note, velocity, modify=False):
		if note not in self.notes[channel]:
			self.note.append([channel, note, float(velocity)/3, self.pos, self.instruments[channel], self.get_freq(note)])
			self.notes[channel].add(note)
		else:
			for i, n in enumerate(self.note):
				if n[0] == channel and n[1] == note:
					self.note[i][2] = float(velocity)/3
					if not modify: self.note[i][3] = self.pos
					return
	def stop_note(self, channel, note):
		for i, n in enumerate(self.note):
			if n[0] == channel and n[1] == note:
				del self.note[i]
				self.notes[channel].remove(note)
				return
	
	def get_frames(self, chunk):#render frames
		out = []
		
		#speedup the name lookup a little
		chn = self.channels
		f = self.frequency
		notes = tuple(self.note)
		
		if len(notes):
			for i in map(float, xrange(self.pos, self.pos+chunk)):
				frame = sum(w((i-p)/f * freq) * v for c, n, v, p, w, freq in notes)
				
				if -1 <= frame <= 1:
					for _ in xrange(chn):
						out.append(frame)
				else:
					for _ in xrange(chn):
						out.append(math.copysign(1, frame))
					#out.append(frame)
		else:
			out = [0.]*chunk*chn
		self.pos += chunk
		
		return self.pack(out)
	
	#change this for other tunings:
	def get_freq(self, note):#tune for c4 = 60 and A = 440Hz
		return 440.*math.pow(2, float(note-58)/12.)
	
	#internal:
	#todo: determine the fastest of the two: (maybe even implement it in numpy instead?)
	def pack(self, frames):#this handles bit-depth aswell. "frame" is a float between -1 and 1
		p = struct.pack
		n = int
		return "".join((p("h", n(i*0x7FFF)) for i in frames))
	def pack2(self, frames):
		l = len(frames)
		scaled = map(mul, frames, [0x7FFF]*l)
		inted = map(int, scaled)
		return struct.pack("h"*l, *inted)

			
def play(generator):
	def callback(in_data, frame_count, time_info, status_flags):
			global renders
			renders += 1
			return (generator.get_frames(frame_count), pyaudio.paContinue)
	
	pa = pyaudio.PyAudio()
	stream = pa.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					output=True,
					frames_per_buffer=CHUNK,
					stream_callback=callback)
	return stream
def init(genClass):
	gen = genClass()
	play(gen)
	
	return gen

#cause why not?
def get_rendercount_since_last_time():#horribly long name
	global renders
	ret = renders
	renders = 0
	return ret

