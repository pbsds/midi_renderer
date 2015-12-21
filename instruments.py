# -*- coding: utf-8 -*-
import math, random

class Soundfont:
	def __init__(self):
		self.instruments = self.MakeProgramTable(none=self.squareWave)
		#self.instruments = self.MakeProgramTable(none=self.sineWave)
		
	#need4speed
	pi2 = math.pi*2
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
		return .8 if (p%1) > 0.5 else -.8
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
			return p
		elif p >= 3:
			return p-2
		else:
			return 1-p
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
		return self.triangleWave(math.sqrt(3.6*p))*1.2
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
		
		#Strings
		
		#Ensemble
		
		#Brass
		
		#Reeds
		
		#Pipe
		
		#Synth leads
		
		#Synth pad
		
		#Synth effects
		pass
		
		#ethnic
		sitar = self.AddCrush2Wave(guitar, levels=4)
		sitar = self.CompressWave(sitar, gain=1.5)
		sitar = self.ChangeWaveOctave(sitar, change=-1)
		out[104] = sitar
		
		#Percussive
		
		#Sound effects
		
		#for i in xrange(128): out[i] = squareWave#AddAttack2Wave(squareWave, length=0.4)
		#for i in xrange(128): out[i] = sine3Wave#AddAttack2Wave(squareWave, length=0.4)
		#for i in xrange(128): out[i] = AddPitchWobbles2Wave(AddAttack2Wave(squareWave, length=0.4), speed=16, strength=0.25)
		return out
