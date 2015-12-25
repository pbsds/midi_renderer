# -*- coding: utf-8 -*-
import math, random

class Soundfont:
	def __init__(self):
		self.instruments = self.MakeProgramTable(none=self.triangleWave)
		#self.instruments = self.MakeProgramTable(none=self.sineWave)
		
	#need4speed
	pi2 = math.pi*2
	pi8 = math.pi*8
	#sin = math.sin
	#Wavefunctions:
	def sineWave(self, p):
		return math.sin(p*self.pi2)
	def sine3Wave(self, p):
		return math.sin(p*self.pi2)**3
	def sine5Wave(self, p):
		return math.sin(p*self.pi2)**5
	def sine7Wave(self, p):
		return math.sin(p*self.pi2)**7
	def sine9Wave(self, p):
		return math.sin(p*self.pi2)**9
	def squareWave(self, p):
		return .7 if (p%1) > 0.5 else -.7
	def sawtoothWave(self, p):
		return (p%1)*2. - 1.
	def saw3Wave(self, p):
		return ((p%1)*2. - 1.)**3
	def saw5Wave(self, p):
		return ((p%1)*2. - 1.)**5
	def triangleWave(self, p):
		p = (p%1)*4
		if p <= 1:
			return p
		elif p >= 3:
			return p-4
		else:
			return 2-p
	def dafuqWave(self, p):#a happy little accident
		p = (p%1)*4
		if p <= 1:
			return p*0.7
		elif p >= 3:
			#return p-2
			return p*0.7-1.4
		else:
			#return 1-p
			return 0.7-p*0.7
	def trianglesWave(self, p):
		# /  \  |
		#/    \/ \
		#0--1--2--3--4
		#         \ /
		#          |
		p = (p%1)*4
		#p = (p%2)*2#one octave lower, faster than using the modifier
		if p <= 1:
			return p*0.7
		elif p <= 2:
			#return (2-p)*0.7
			return 1.4-p*0.7
		elif p <= 2.5:
			#return (p*2-4)*0.7
			return p*1.4-2.8
		elif p <= 3.5:
			#return (5-p*2)*0.7
			return 3.5-p*1.4
		else:
			#return (p*2-7)*0.7
			return p*1.4-4.9
	#spesific instrument tibmres/wavefunctions:
	def fluteWave(self, p):
		return (math.sin(self.pi2*p)**3 + 2*math.sin(self.pi2*p)**2 - 1 - 0.25*math.cos(self.pi2*p)) / 2
		pass#return (math.sin(self.pi2*p)**3 + 2*math.sin(self.pi2*p)**2 - 1) / 2 
	def trumpetWave(self, p):
		p = p%1
		#could be done more elegantly than just regregating over points extracted from a image...
		#http://www.feilding.net/sfuad/musi3012-01/images/lectures/trumpet.gif
		#from
		#http://www.feilding.net/sfuad/musi3012-01/html/lectures/005_sound_IV.htm
		return (-33623.26*p**9 + 142968.91*p**8 - 245850.26*p**7 + 217707.81*p**6 - 103541.23*p**5 + 24034.6*p**4 - 1388.21*p**3 - 349.88*p**2 + 41.49*p) / 2
	def violinWave(self, p):
		#f(x) = sin(2π x) + 0.6sin(8π x)
		#f(x) a g(x)² abs(sin(π x))
		#http://www.feilding.net/sfuad/musi3012-01/images/lectures/violin.gif
		#return (0.5-(p%1))**2 * 19 * (math.sin(p*self.pi2) + 0.7*math.sin(p*self.pi8)) * abs(math.sin(math.pi*p))
		#return (0.5-(p%1))**2 * 19 * (math.sin(p*self.pi2) + 0.7*math.sin(p*self.pi8)) * abs(math.sin(math.pi*p))
		
		#http://static1.squarespace.com/static/528952fde4b088c60f4cae09/t/5496326ce4b0630c86f263a3/1419129455996/
		return 0.
	#modifiers:
	def AddAttack2Wave(self, wave, length=0.5):#length is number of seconds untill the velocity is halved for A4
		def NewWave(p):
			return wave(p)/(1. + p/(length*440.))
		return NewWave
	def AddCrush2Wave(self, wave, levels=8):
		def NewWave(p):
			return float(int(wave(p)*levels))/levels
		return NewWave
	def AddPitchWobbles2Wave(self, wave, speed=7, strength=.25):#wobbles speed times per second for a A4
		speed *= 2*math.pi/440
		def NewWave(p):
			return wave(p + math.sin(p*speed)*strength)
		return NewWave
	def AddVibrato2Wave(self, wave, speed=15., low=0.5):#speed = times a second for A4
		speed *= 2*math.pi
		high = (1-low)/2
		def NewWave(p):
			return wave(p) * ((math.cos(p*speed/440.) + 1)*high + low)
		return NewWave
	def ChangeWaveOctave(self, wave, change=0):#change is number of octaves
		speed = 2.**change
		def NewWave(p):
			return wave(p*speed)
		return NewWave
	def CombineWaves(self, wave1, wave2, v1, v2):
		def NewWave(p):
			return wave1(p)*v1 + wave2(p)*v2
		return NewWave
	def CompressWave(self, wave, gain=1.2):
		def NewWave(p):
			return min(max(wave(p)*gain, -1), 1)
		return NewWave
	#percussion waves
	def highhatBeat(self, p):#short percussion
		#return (random.random()*2-1)/(1+p/10)
		return (random.random()*2-1) * max(1-p/30, 0)
	def snareBeat(self, p):
		return min(max((random.random()*2-1) * max(2-p/24, 0), -1), 1)
	def drumBeat(self, p):
		return self.triangleWave(math.sqrt(4*p))*1.2
	def drum2Beat(self, p):
		return self.triangleWave((4*p)**0.56)*1.2
	def drum2sBeat(self, p):
		return self.sineWave((4*p)**0.6)*1.2
	def timpaniBeat(self, p):
		return self.sineWave(math.sqrt(4*p))*0.8 + self.triangleWave(math.sqrt(16*p))*0.6 + self.triangleWave(math.sqrt(8*p))*0.4
	#The soundfont:
	def MakeProgramTable(self, n=128, none=None):
		if not none:
			none = lambda x: 0.
		out = [none for i in range(n)]
		
		#https://en.wikipedia.org/wiki/General_MIDI#Program_change_events
		
		#piano
		piano = self.CombineWaves(self.ChangeWaveOctave(self.sineWave, change=2), self.triangleWave, 0.18, 0.8)
		piano = self.AddAttack2Wave(piano, length=0.3)
		for i in xrange(0,8): out[i] = piano
		
		harpsichord = self.AddAttack2Wave(self.sawtoothWave, length=0.2)
		harpsichord = self.AddCrush2Wave(harpsichord, levels=8)
		out[6] = harpsichord
		
		#chromatic percussion
		ChromaticPercussion = self.AddAttack2Wave(self.squareWave, length=0.01)#, perSecond=True)
		ChromaticPercussion = self.ChangeWaveOctave(ChromaticPercussion, change=+1)
		for i in xrange(8,16): out[i] = ChromaticPercussion
		
		#organs:
		organ = self.AddAttack2Wave(self.sineWave, length=1.5)
		organ = self.AddPitchWobbles2Wave(organ, speed=3.2, strength=0.25)
		for i in xrange(16,20): out[i] = organ
		
		accordion = self.AddAttack2Wave(self.sine9Wave, length=1.5)
		accordion = self.AddVibrato2Wave(accordion, speed=3.2, low=0.7)
		for i in xrange(20,24): out[i] = accordion
		
		#guitar
		guitar = self.AddAttack2Wave(self.sine5Wave, length=0.20)
		for i in xrange(24, 32): out[i] = guitar
		
		overdrive = self.CompressWave(self.saw5Wave, gain=10)
		overdrive = self.AddAttack2Wave(overdrive, length=1.2)
		overdrive = self.AddVibrato2Wave(overdrive, speed=2, low=0.8)
		for i in xrange(29, 31): out[i] = overdrive
		
		#bass
		bass = self.AddAttack2Wave(self.trianglesWave, length=0.10)
		bass = self.ChangeWaveOctave(bass, change=-1)
		for i in xrange(32, 41): out[i] = bass
		
		
		#Strings
		violin = self.violinWave
		#out[]
		
		out[47] = self.timpaniBeat#timpani (drum)
		
		#Ensemble
		
		#Brass
		trumpet = self.trumpetWave
		for i in xrange(56, 64): out[i] = trumpet
		tuba = self.ChangeWaveOctave(trumpet, change=-1)
		out[58] = tuba
		
		#Reeds
# 65 Soprano Sax
# 66 Alto Sax
# 67 Tenor Sax
# 68 Baritone Sax
# 69 Oboe
# 70 English Horn
# 71 Bassoon
# 72 Clarinet
		#sax = 
		#horn = 
		
		#Pipe
		flute = self.AddAttack2Wave(self.fluteWave, length=3)
		for i in xrange(72, 80): out[i] = flute
		out[79] = self.AddAttack2Wave(self.sineWave, length=3)#ocarina
		
		#Synth leads
		out[80] = self.squareWave
		out[81] = self.sawtoothWave
		
		
		out[84] = self.AddAttack2Wave(self.ChangeWaveOctave(self.dafuqWave, change=-2), length=0.5)#charang
# 81 Lead 1 (square)
# 82 Lead 2 (sawtooth)
# 83 Lead 3 (calliope)
# 84 Lead 4 chiff
# 85 Lead 5 (charang)
# 86 Lead 6 (voice)
# 87 Lead 7 (fifths)
# 88 Lead 8 (bass + lead)
		
		
		#Synth pad
		
		#Synth effects
		pass
		for i in xrange(96, 104): out[i] = lambda x: 0.
		crystal = self.AddAttack2Wave(self.saw3Wave, length=0.08)
		crystal = self.ChangeWaveOctave(crystal, change=-1)
		#out[98] = crystal#crystal
		out[98] = self.CompressWave(crystal, gain=1.4)#crystal
		
		#ethnic
		sitar = self.AddCrush2Wave(guitar, levels=4)
		sitar = self.CompressWave(sitar, gain=1.5)
		sitar = self.ChangeWaveOctave(sitar, change=-1)
		#sitar = self.ChangeWaveOctave(sitar, change=-2)
		out[104] = sitar
		
		#Percussive
# 113 Tinkle Bell
# 114 Agogo
# 115 Steel Drums
# 116 Woodblock
# 117 Taiko Drum
# 118 Melodic Tom
# 119 Synth Drum
# 120 Reverse Cymbal
		out[117] = self.drum2Beat#Melodic Tom
		
		#Sound effects
		pass
		for i in xrange(120,128): out[i] = lambda x: 0.
		
		#ech
		#for i in xrange(128): out[i] = violin
		#for i in xrange(128): out[i] = self.triangleWave
		#for i in xrange(128): out[i] = self.sineWave
		#for i in xrange(128): out[i] = self.AddAttack2Wave(self.squareWave, length=0.4)
		#for i in xrange(128): out[i] = self.AddAttack2Wave(self.triangleWave, length=0.4)
		#for i in xrange(128): out[i] = self.AddAttack2Wave(self.dafuqWave, length=0.4)
		#for i in xrange(128): out[i] = self.sine3Wave#self.AddAttack2Wave(self.squareWave, length=0.4)
		#for i in xrange(128): out[i] = self.ChangeWaveOctave(lambda p: self.triangleWave(p if p%1 < 0.5 else (p%1 - 0.5)*2)**2, change=-1)
		#for i in xrange(128): out[i] = self.trianglesWave
		
		#for the dogsong:
		#for i in xrange(128): out[i] = self.AddPitchWobbles2Wave(self.AddAttack2Wave(self.squareWave, length=0.3), speed=7, strength=0.25)
		return out

