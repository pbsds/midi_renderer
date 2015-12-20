import pyaudio, math, itertools, struct, random, time

#global settings
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

#waves:
def sineWave(p, freq):
		return math.sin(p*math.pi*2)#slow, names, ech. it hurts
def squareWave(p, freq):
		return 1. if (p%1) > 0.5 else -1.
def sawtoothWave(p, freq):
		return (p%1)*2. - 1.
def triangleWave(p, freq):
		p = (p%1)*4
		if p <= 1:
			return p
		elif p >= 3:
			return p-4
		else:
			return 2-p
def dafuqWave(p, freq):#a happy little accident
		p = (p%1)*4
		if p <= 1:
			return p
		elif p >= 3:
			return p-2
		else:
			return 1-p
#modifiers:
def AddAttack2Wave(wave, length=0.5, perSecond=False):#length is number of seconds untill the velocity is halved for A4. for all if perSecond is true
	if not perSecond:
		def NewWave(p, freq):
			return wave(p, freq)/(1. + p/(length*440.))
	else:
		def NewWave(p, freq):
			return wave(p, freq)/(1. + p/(length*freq))
	return NewWave
def AddCrush2Wave(wave, levels=8):
	def NewWave(p, freq):
		return float(int(wave(p, freq)*levels))/levels
	return NewWave
def AddPitchWobbles2Wave(wave, speed=7, strength=.25, perSecond=False):#wobbles speed times per second for a A4, and scales with frequency. if perSeconds is true then all notes wobbles the same
	if not perSecond:
		speed *= 2*math.pi/440
		def NewWave(p, freq):
			return wave(p + math.sin(p*speed)*strength, freq)
	else:
		r = RATE
		speed *= 2*math.pi
		def NewWave(p, freq):
			return wave(p + math.sin(p/freq*speed)*strength, freq)
	return NewWave
def AddVibrato2Wave(wave, speed=15., low=0.0):#speed = times a second
	speed *= 2*math.pi
	def NewWave(p, freq):
		return wave(p, freq) * ((math.cos(p*speed/freq) + 1)/2.*(1.-low) + low)
	return NewWave
def ChangeWaveOctave(wave, change=0):#change is number of octaves
	speed = 2.**change
	def NewWave(p, freq):
		return wave(p*speed, freq*speed)
	return NewWave
def CombineWaves(wave1, wave2, v1, v2):
	def NewWave(p, freq):
		return wave1(p, freq)*v1 + wave2(p, freq)*v2
	return NewWave
#perc
def highhatBeat(p, freq):#short percussion
	#return (random.random()*2-1)/(1+p/10)
	return (random.random()*2-1) * max(1-p/30, 0)
def snareBeat(p, freq):
	return min(max((random.random()*2-1) * max(2-p/24, 0), -1), 1)
def drumBeat(p, freq):
	return triangleWave(math.sqrt(3.6*p), freq)*1.2

#soundfonts:
def MakeProgramTable():
	none = lambda x, y: 0.
	#none = squareWave
	out = [none for i in range(128)]
	
	piano = AddAttack2Wave(squareWave, length=0.3)#todo: fix this
	for i in xrange(0,8): out[i] = piano
	
	harpsichord = AddAttack2Wave(sawtoothWave, length=0.2)
	harpsichord = AddCrush2Wave(harpsichord, levels=8)
	out[6] = harpsichord
	
	ChromaticPercussion = AddAttack2Wave(squareWave, length=0.01, perSecond=True)
	ChromaticPercussion = ChangeWaveOctave(ChromaticPercussion, change=+1)
	for i in xrange(8,16): out[i] = ChromaticPercussion
	
	organ = AddAttack2Wave(sineWave, length=1.5)
	organ = AddPitchWobbles2Wave(organ, speed=3.2, strength=0.25)
	for i in xrange(16,24): out[i] = organ
	
	guitar = AddAttack2Wave(sawtoothWave, length=0.4)#heavy, doesn't sound good
	guitarp1 = AddPitchWobbles2Wave(guitar, speed=3, strength=0.25)
	guitarp2 = AddVibrato2Wave(guitar, speed=6, low=0.2)
	guitar = CombineWaves(guitarp1, guitarp2, 0.6, 0.5)
	for i in xrange(24, 32): out[i] = guitar
	
	overdrive = triangleWave#WIP
	for i in xrange(29, 31): out[i] = guitar
	
	out[0] = overdrive
	return out

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
			self.note.append([channel, note, float(velocity)/4, self.pos, self.instruments[channel], self.get_freq(note)])
			self.notes[channel].add(note)
		else:
			for i, n in enumerate(self.note):
				if n[0] == channel and n[1] == note:
					self.note[i][2] = float(velocity)/4
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
				frame = sum(w((i-p)/f * freq, freq) * v for c, n, v, p, w, freq in notes)
				
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

#player for pyaudio:
renders = []
def play(generator):
	def callback(in_data, frame_count, time_info, status_flags):
			#global renders
			epoch = time.time()
			out = generator.get_frames(frame_count)
			renders.append(time.time()-epoch)#mutable
			return (out, pyaudio.paContinue)
	
	pa = pyaudio.PyAudio()
	stream = pa.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					output=True,
					frames_per_buffer=CHUNK,
					stream_callback=callback)
	return stream
#def init(genClass):
#	gen = genClass()
#	play(gen)
#	
#	return gen
def get_rendercount_since_last_time():#horribly long name
	global renders
	ret = (len(renders), sum(renders))
	del renders[:]
	return ret

