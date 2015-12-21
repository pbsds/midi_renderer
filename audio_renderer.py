import pyaudio, math, itertools, struct, random, time, numpy as np

#global settings
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

#waves:
def sineWave(p):
	return math.sin(p*math.pi*2)#slow, names, ech. it hurts
def sine3Wave(p):
		return math.sin(p*math.pi*2)**3#slow, names, ech. it hurts
def sine5Wave(p):
		return math.sin(p*math.pi*2)**5#slow, names, ech. it hurts
def sine7Wave(p):
		return math.sin(p*math.pi*2)**7#slow, names, ech. it hurts
def sine9Wave(p):
		return math.sin(p*math.pi*2)**9#slow, names, ech. it hurts
def squareWave(p):
		return .8 if (p%1) > 0.5 else -.8
def sawtoothWave(p):
	return (p%1)*2. - 1.
def saw3Wave(p):
	return ((p%1)*2. - 1.)**3
def saw5Wave(p):
	return ((p%1)*2. - 1.)**5
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
def AddAttack2Wave(wave, length=0.5):#length is number of seconds untill the velocity is halved for A4
	def NewWave(p):
		return wave(p)/(1. + p/(length*440.))
	return NewWave
def AddCrush2Wave(wave, levels=8):
	def NewWave(p):
		return float(int(wave(p)*levels))/levels
	return NewWave
def AddPitchWobbles2Wave(wave, speed=7, strength=.25, perSecond=False):#wobbles speed times per second for a A4, and scales with frequency. if perSeconds is true then all notes wobbles the same
	speed *= 2*math.pi/440
	def NewWave(p):
		return wave(p + math.sin(p*speed)*strength)
	return NewWave
def AddVibrato2Wave(wave, speed=15., low=0.5):#speed = times a second for A4
	speed *= 2*math.pi
	high = (1-low)/2
	def NewWave(p):
		return wave(p) * ((math.cos(p*speed/440.) + 1)*high + low)
	return NewWave
def ChangeWaveOctave(wave, change=0):#change is number of octaves
	speed = 2.**change
	def NewWave(p):
		return wave(p*speed)
	return NewWave
def CombineWaves(wave1, wave2, v1, v2):
	def NewWave(p):
		return wave1(p)*v1 + wave2(p)*v2
	return NewWave
def CompressWave(wave, gain=1.2):
	def NewWave(p):
		return min(max(wave(p)*gain, -1), 1)
	return NewWave
#perc
def highhatBeat(p):#short percussion
	#return (random.random()*2-1)/(1+p/10)
	return (random.random()*2-1) * max(1-p/30, 0)
def snareBeat(p):
	return min(max((random.random()*2-1) * max(2-p/24, 0), -1), 1)
def drumBeat(p):
	return triangleWave(math.sqrt(3.6*p), freq)*1.2

#soundfonts:
def MakeProgramTable():
	none = lambda x, y: 0.
	none = squareWave
	out = [none for i in range(128)]
	
	piano = CombineWaves(ChangeWaveOctave(sineWave, change=2), triangleWave, 0.18, 0.8)
	piano = AddAttack2Wave(piano, length=0.3)
	for i in xrange(0,8): out[i] = piano
	
	harpsichord = AddAttack2Wave(sawtoothWave, length=0.2)
	harpsichord = AddCrush2Wave(harpsichord, levels=8)
	out[6] = harpsichord
	
	ChromaticPercussion = AddAttack2Wave(squareWave, length=0.01)#, perSecond=True)
	ChromaticPercussion = ChangeWaveOctave(ChromaticPercussion, change=+1)
	for i in xrange(8,16): out[i] = ChromaticPercussion
	
	organ = AddAttack2Wave(sineWave, length=1.5)
	organ = AddPitchWobbles2Wave(organ, speed=3.2, strength=0.25)
	for i in xrange(16,20): out[i] = organ
	
	accordion = AddAttack2Wave(sine9Wave, length=1.5)
	accordion = AddVibrato2Wave(accordion, speed=3.2, low=0.7)
	for i in xrange(20,24): out[i] = accordion
	
	guitar = AddAttack2Wave(sine5Wave, length=0.20)
	for i in xrange(24, 32): out[i] = guitar
	
	overdrive = CompressWave(saw5Wave, gain=10)
	overdrive = AddAttack2Wave(overdrive, length=1.2)
	overdrive = AddVibrato2Wave(overdrive, speed=2, low=0.8)
	for i in xrange(29, 31): out[i] = overdrive
	
	
	
	sitar = AddCrush2Wave(guitar, levels=4)
	sitar = CompressWave(sitar, gain=1.5)
	sitar = ChangeWaveOctave(sitar, change=-1)
	out[104] = sitar
	
	#for i in xrange(128): out[i] = squareWave#AddAttack2Wave(squareWave, length=0.4)
	#for i in xrange(128): out[i] = sine3Wave#AddAttack2Wave(squareWave, length=0.4)
	#for i in xrange(128): out[i] = AddPitchWobbles2Wave(AddAttack2Wave(squareWave, length=0.4), speed=16, strength=0.25)
	return out

#generator
class generator():
	rate = float(RATE)
	channels = 2
	pitchrange = 2.0#semitones
	instruments = [sineWave for _ in xrange(16)]#15 channels instead?
	
	def __init__(self):
		self.notes = [set() for _ in xrange(16)]
		self.note = []#[i] = [channel, note, velocity, start pos, instrument, frequency/rate, wavefunction offset]
		self.pos = 0#position
		self.tuning = [0.0 for i in xrange(16)]
	#input
	def set_note(self, channel, note, velocity, modify=False):
		if note not in self.notes[channel]:
			self.note.append([channel, note, float(velocity)/7, self.pos, self.instruments[channel], self.get_freq(note + self.tuning[channel])/self.rate, 0.])
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
	def set_pitch(self, channel, pitch):#note + pitch*self.pitchrange()
		#todo: fix this?
		#pitch *= self.pitchrange
		self.tuning[channel] = pitch
		for i, n in enumerate(self.note):
			if n[0] == channel:
				note, startpos, freq = n[1], n[3], n[5]
				self.note[i][3] = self.pos
				self.note[i][5] = self.get_freq(note + pitch)/self.rate
				self.note[i][6] += (self.pos-startpos) * freq
		
	def get_frames(self, chunk):#render frames
		#speedup the name lookup a little
		#notes = tuple(self.note)
		notes = self.note[:]#is this a good enought copy? i'm trying to avoid any changes made during rendering
		
		if notes:
			out = np.fromiter((sum(n[4]((i-n[3]) * n[5] + n[6]) * n[2] for n in notes) for i in map(float, xrange(self.pos, self.pos+chunk))), dtype=np.float32, count=chunk)
			#out = np.zeros(chunk, dtype=np.float32)
			#for e, i in enumerate(map(float, xrange(self.pos, self.pos+chunk))):
				#out[e, :] = sum(n[4]((i-n[3])*n[5]) * n[2] for n in notes)
				#out[e] = sum(n[4]((i-n[3])*n[5]) * n[2] for n in notes)
			
			if self.channels > 1:
				out = np.array([out]*self.channels)
		else:
			out = np.zeros((self.channels, chunk), dtype=np.float32)
				
		self.pos += chunk
		
		np.clip(out, -1, 1, out=out)
		
		return self.pack(out)
	
	#change this for other tunings:
	def get_freq(self, note):#tune for c4 = 60 and A = 440Hz
		return 440.*math.pow(2, float(note-58)/12.)
	
	#internal:
	def pack(self, frames):#np compatible
		frames *= 0x7FFF
		return frames.astype(np.int16).tostring("F")

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

