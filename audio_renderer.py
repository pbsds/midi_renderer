import pyaudio, math, random, time, numpy as np

#global settings
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

#generator
class generator():
	rate = float(RATE)
	channels = 2
	pitchRange = 2.0#semitones
	instruments = [(lambda x: 1 if x%1>0.5 else -1) for _ in xrange(16)]
	
	def __init__(self):
		self.notes = [set() for _ in xrange(16)]
		self.note = []#[i] = [channel, note, velocity, start pos, instrument, frequency/rate, wavefunction offset, raw velocity]
		self.pos = 0#position
		self.pitches = [0.0 for i in xrange(16)]
		self.volumes = [1.0 for i in xrange(16)]
	#input
	#vel, start, freq, offset
	def set_note(self, channel, note, velocity, modify=False):
		velocity = float(velocity)/6
		if note not in self.notes[channel]:
			self.note.append([channel,
			                  note,
			                  velocity * self.volumes[channel],
			                  self.pos,
			                  self.instruments[channel],
			                  self.get_freq(note + self.pitches[channel])/self.rate,
			                  0.,
			                  velocity])
			self.notes[channel].add(note)
		else:
			for i, n in enumerate(self.note):
				if n[0] == channel and n[1] == note:
					self.note[i][2] = velocity * self.volumes[channel]
					self.note[i][7] = velocity
					if not modify: self.note[i][3] = self.pos
					return
	def stop_note(self, channel, note):
		for i, n in enumerate(self.note):
			if n[0] == channel and n[1] == note:
				del self.note[i]
				self.notes[channel].remove(note)
				return
	def set_pitch(self, channel, pitch):#note + pitch*self.pitchRange = newnote
		pitch *= self.pitchRange
		self.pitches[channel] = pitch
		for i, n in enumerate(self.note):
			if n[0] == channel:
				note, startpos, freq = n[1], n[3], n[5]
				self.note[i][3] = self.pos
				self.note[i][5] = self.get_freq(note + pitch)/self.rate
				self.note[i][6] += (self.pos-startpos) * freq
	def set_volume(self, channel, volume):
		volume = math.log10(volume*9. + 1)#is this right?
		self.volumes[channel] = volume
		for i, n in enumerate(self.note):
			if n[0] == channel:
				self.note[i][2] = n[7]*volume
		
	def get_frames(self, chunk):#render frames
		#speedup the name lookup a little:
		#notes = tuple(self.note)
		notes = self.note[:]#is this a good enought copy? i'm trying to avoid any changes made during rendering
		
		if notes:
			out = np.fromiter((sum(n[4]((i-n[3]) * n[5] + n[6]) * n[2] for n in notes) for i in map(float, xrange(self.pos, self.pos+chunk))), dtype=np.float32, count=chunk)
			
			#out = np.zeros(chunk, dtype=np.float32)
			#for e, i in enumerate(map(float, xrange(self.pos, self.pos+chunk))):
			#	out[e] = sum(n[4]((i-n[3])*n[5] + n[6]) * n[2] for n in notes)
			
			if self.channels > 1:
				out = np.array([out]*self.channels)
			
			self.pos += chunk
			np.clip(out, -1, 1, out=out)
			return self.pack(out)
		else:
			self.pos += chunk
			#out = np.zeros((self.channels, chunk), dtype=np.float32)
			#return self.pack(out)
			return "\0\0" * (self.channels * chunk)
	#change this for other tunings:
	def get_freq(self, note):#tune for a4 = 57(58 if 1-128) and A = 440Hz
		#return 440.*math.pow(2, float(note-69)/12.)
		return 440.*math.pow(2, float(note-57)/12.)
	
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
def get_rendercount_since_last_time():#horribly long name
	global renders
	ret = (len(renders), sum(renders))
	del renders[:]
	return ret

