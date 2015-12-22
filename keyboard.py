#!python2
import time, mido
from operator import mul
mido.set_backend('mido.backends.pygame')#change this if you use something else
import audio_renderer as audio
from instruments import Soundfont

def HandleMessage(msg, gen, instruments, verbose=False):
	if msg.type == "note_on":
		if msg.velocity == 0:
			gen.stop_note(msg.channel, msg.note)
		else:
			gen.set_note(msg.channel, msg.note, float(msg.velocity)/127.)
		if verbose: print "note(%i,%i)" % (msg.note, msg.velocity),
	elif msg.type == "note_off":
		gen.stop_note(msg.channel, msg.note)
		if verbose: print "note(%i,0)" % msg.note,
	elif msg.type == "program_change":
		#print dir(msg)
		if msg.channel <> 9:
			gen.instruments[msg.channel] = instruments[msg.program]
			gen.instruments = gen.instruments[:]#apparently this makes it faster?
		if verbose or 1: print "Instrument(%i,%i)" % (msg.channel, msg.program), #changes msg.channel to the instrument here. https://en.wikipedia.org/wiki/General_MIDI#Program_change_events
	
	elif msg.type == "pitchwheel": 
		#print dir(msg)
		gen.set_pitch(msg.channel, float(msg.pitch)/8192.)
		if verbose: print "pitch(%i,%.2f)" % (msg.channel, float(msg.pitch)/8192.),
	elif msg.type not in ("clock",) and verbose:
		#print msg.type,
		#if msg.type == "control_change": 
			#print dir(msg)
			#print msg.control, 
		pass

def PlayMidoPort(gen, port, instruments, verbose=True):
	stream = audio.play(gen)
	
	prev_print = time.time()
	last_few_renders = []#to keep an average
	neededRenderRate = str(round(float(audio.RATE)/float(audio.CHUNK), 2))
	neededRenderTime = str(round(float(audio.CHUNK)/float(audio.RATE) * 1000., 2)) #ms
	
	nq = 0
	for msg in port:
		HandleMessage(msg, gen, instruments, verbose)
		
		if msg.type[:4] == "note":
			nq += 1
		elif msg.type not in ("clock", "program_change", "pitchwheel") and verbose:
			print msg.type,
			#if msg.type == "control_change": 
				#print dir(msg)
				#print msg.control, 
			pass
		
		#print pretty information
		t = time.time()
		if t - prev_print >= 1./10.:
			renderNum, renderTime = audio.get_rendercount_since_last_time()
			last_few_renders.append((renderNum, renderTime, prev_print))
			
			if len(last_few_renders)>10: del last_few_renders[0]
			renderRateAvg = sum(map(lambda x:x[0], last_few_renders)) / (t - last_few_renders[0][2])
			renderTimeAvg = sum(map(lambda x:x[1], last_few_renders)) / sum(map(lambda x:x[0], last_few_renders)) * 1000.#ms
			
			print "\n\nAudio renderer @%.2f/%sHz, %.2fms/%sms, Notes playing: %i, events: %i" % (renderRateAvg, neededRenderRate, renderTimeAvg, neededRenderTime, len(gen.note), nq)
			prev_print = t
			nq = 0
	
	stream.close()

def RenderMidi(gen, mid, instruments, verbose=True):#generator
	if verbose:
		print "render start"
	t = 0
	prev_time = 0
	pos = 0
	rate = audio.RATE
	if verbose:
		l = mid.length#very timeconsuming for black midis
		ls = "%i:%s" % (int(l)//60, str(int(l)%60).zfill(2))
		print "init loop"
	r = 0#notes, renders
	for n, msg in enumerate(mid):
		if msg.time > 0:
			t += msg.time
			chunk = int(t*rate - pos)
			yield gen.get_frames(chunk)
			pos += chunk
			r += 1
		HandleMessage(msg, gen, instruments)#, False)#redundant
		
		#for the bored:
		if time.time()-prev_time > 1./5.:
			print "Progress: %.2f%% (%i:%s / %s)  Events: %i  Renders: %i" % ((t/l)*100, int(t)//60, str(int(t)%60).zfill(2), ls, n+1, r)
			prev_time = time.time()

def main(keyboard=None, midifile=None, verbose=True, output=None):
	if keyboard:
		if output:
			raise Exception("Realtime output not implemented")#(yet?)
		port = mido.open_input(keyboard)
	elif midifile:
		if output:
			port =  mido.MidiFile(midifile)
		else:
			port =  mido.MidiFile(midifile).play()
	else:
		raise Exception("No input dumb dumb")
	
	gen = audio.generator()
	soundfont = Soundfont()
	instruments = soundfont.instruments
	
	#temp
	gen.instruments = [instruments[0] for _ in xrange(16)]
	gen.instruments[9] = soundfont.highhatBeat
	#gen.instruments[9] = soundfont.snareBeat
	#gen.instruments[9] = soundfont.drumBeat
	
	#do:
	if output:
		import wave
		f = wave.open(output, "w")
		f.setnchannels(audio.CHANNELS)
		f.setsampwidth(2)#more nydamic please?
		f.setframerate(audio.RATE)
		for data in RenderMidi(gen, port, instruments, verbose=verbose):
			f.writeframes(data)
		f.close()
	else:
		PlayMidoPort(gen, port, instruments, verbose=verbose)#blocking
	
	#if keyboard or output:
	#	port.close()

if __name__ == "__main__":
	f, k, s, o	= None, None, False, None
	#k = mido.get_input_names()[0]#todo: give the user a choice?
	
	#f = "midis/13417_Ballad-of-the-Windfish.mid"
	#f = "midis/27641_Green-Greens.mid"
	#f = "midis/circusgalop.mid"
	#f = "midis/Clock Town 2.mid"
	#f = "midis/Clock Town.mid"
	#f = "midis/Darude_-_Sandstorm.mid"
	#f = "midis/file.mid"
	#f = "midis/gerudo valley.mid"
	#f = "midis/Good Egg Galaxy.mid"
	#f = "midis/Gusty Garden Galaxy.mid"
	#f = "midis/Hare Hare Yukai.mid"
	#f = "midis/he is a pirate.mid"
	#f = "midis/kdikarus.mid"
	#f = "midis/Led_Zeppelin_-_Stairway_to_Heaven.mid"
	#f = "midis/Makrells.mid"
	f = "midis/mt-pyre.mid"
	#f = "midis/native faith.mid"
	#f = "midis/portal_still_alive.mid"
	#f = "midis/Rhythm.mid"
	#f = "midis/Summer.mid"
	#f = "midis/Super_Smash_Bros_Brawl_Main_Theme.mid"
	#f = "midis/through-the-fire-and-flames.mid"
	#f = "midis/Windmill 2.mid"
	#f = "midis/Windmill.mid"
	
	
	#f = "midis/animal crossing/title.mid"
	
	#f = "midis/undertale/Death By Glamour.mid"
	#f = "midis/undertale/Determination.mid"
	#f = "midis/undertale/Dogsong.mid"
	#f = "midis/undertale/Enemy Approaching.mid"
	#f = "midis/undertale/Finale.mid"
	#f = "midis/undertale/Ghost Fight.mid"
	#f = "midis/undertale/Heartbreak.mid"
	#f = "midis/undertale/Megalovania.mid"
	#f = "midis/undertale/MIDIlovania.mid"
	#f = "midis/undertale/Ruins.mid"
	#f = "midis/undertale/Spider Dance.mid"
	
	#holy hell
	s = True
	#f = "midis/black midi/Death Waltz.mid"
	#f = "midis/black midi/TheSuperMarioBros2 - bad apple 4.6 million.mid"#memoryerror
	#f = "midis/black midi/TheSuperMarioBros2 - The Destroyer 6.26 million.mid"#memoryerror
	#f = "midis/black midi/TheSuperMarioBros2 - The Titan_2.mid"
	#f = "midis/black midi/TheSuperMarioBros2 - Unbounded.mid"
	#f = "midis/black midi/TheSuperMarioBros2 - Voyage 1.26 million.mid"
	#f = "midis/black midi/.mid"
	
	o = "out.wav"; s = False
	main(keyboard=k, midifile=f, verbose=not s, output = o)
	








