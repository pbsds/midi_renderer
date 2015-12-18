import pyaudio, math, itertools, struct

#global settings
CHUNK = 256
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

#internal globals
renders = 0

class generatorBase():
	frequency = 44100.
	channels = 2
	velocity_max = 128.#the scale/coeficient
	def __init__(self):
		self.notes = []#[i] = [note id, velocity]
		self.pos = 0#position
	
	#input
	def set_note(self, id, velocity):
		if id not in map(self._map_i0, self.notes):
			self.notes.append([id, float(velocity)/(self.velocity_max*3)])
		else:
			for i, note in enumerate(self.notes):
				if note[0] == id:
					self.notes[i][1] = float(velocity)/(self.velocity_max*3)
					break
	def stop_note(self, id):
		for i, e in enumerate(self.notes):
				if e[0] == id:
					del self.notes[i]
					break
	
	def get_frames(self, chunk):#render frames
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
	
	#To be replaced by children:
	def tone_generator(self, p):#a period is from 0.0 to 1.0. p is not run trough modulo 1 first
		return 0#placeholder
	def get_freq(self, note):#tune for c4 = 60 and A = 440Hz
		return 440.*math.pow(2, float(note-60)/12.)
	
	#internal:
	def _map_i0(self, i):
		return i[0]
	#todo: determine the fastest of the two: (maybe even implement it in numpy instead?)
	def pack(self, frames):#this handles bit-depth aswell. "frame" is a float between -1 and 1
		h = "h"
		p = struct.pack
		return "".join((p(h, int(i*0x7FFF)) for i in frames))
	def pack2(self, frames):
		l = len(frames)
		scaled = map(mul, frames, [0x7FFF]*l)
		inted = map(int, scaled)
		return struct.pack("h"*len(frames), *inted)

class sineGenerator(generatorBase):
	def tone_generator(self, p):
		return math.sin(p*math.pi*2)#slow, names, ech. it hurts
class squareGenerator(generatorBase):
	def tone_generator(self, p):
		return 1. if (p%1) > 0.5 else -1.
class jigGenerator(generatorBase):#is this the right name? derp
	def tone_generator(self, p):
		return (p%1)*2. - 1.
class sawbladeGenerator(generatorBase):#is this the right name? derp
	def tone_generator(self, p):
		p = (p%1)*4
		if p <= 1:
			return p
		elif p >= 3:
			return p-4
		else:
			return 2-p
class dafuqGenerator(generatorBase):#is this the right name? derp
	def tone_generator(self, p):
		p = (p%1)*4
		if p <= 1:
			return p
		elif p >= 3:
			return p-2
		else:
			return 1-p

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

