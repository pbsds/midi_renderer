#!python2
import time, mido
from operator import mul
mido.set_backend('mido.backends.pygame')#change this if you use something else
import audio_renderer as audio
from instruments import Soundfont

def midoMainloop(gen, port, instruments, verbose=True):
	prev_print = time.time()
	last_few_renders = []#to keep an average
	neededRenderRate = str(round(float(audio.RATE)/float(audio.CHUNK), 2))
	neededRenderTime = str(round(float(audio.CHUNK)/float(audio.RATE) * 1000., 2)) #ms
	
	nq = 0
	pws = 2.**13
	for i in port:
		if i.type == "note_on":
			nq += 1
			if i.velocity == 0:
				gen.stop_note(i.channel, i.note)
			else:
				gen.set_note(i.channel, i.note, float(i.velocity)/127.)
			if verbose: print "note(%i,%i)" % (i.note, i.velocity),
		elif i.type == "note_off":
			nq += 1
			gen.stop_note(i.channel, i.note)
			if verbose: print "note(%i,0)" % i.note,
		elif i.type == "program_change":
			#print dir(i)
			if i.channel <> 9:
				gen.instruments[i.channel] = instruments[i.program]
				gen.instruments = gen.instruments[:]#apparently this makes it faster?
			if verbose: print "Instrument(%i,%i)"%(i.channel, i.program), #changes i.channel to the instrument here. https://en.wikipedia.org/wiki/General_MIDI#Program_change_events
		
		elif i.type == "pitchwheel": 
			#print dir(i)
			gen.set_pitch(i.channel, float(i.pitch)/pws)
			#if verbose or 1: print "pitch(%i,%.2f)" % (i.channel, float(i.pitch)*2/pws),
			
		elif i.type not in ("clock",) and verbose:
			#print i.type,
			#if i.type == "control_change": 
				#print dir(i)
				#print i.control, 
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
			

def main(keyboard=None, midifile=None, verbose=True):
	if keyboard:
		port = mido.open_input(keyboard)
	elif midifile:
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
	stream = audio.play(gen)
	
	midoMainloop(gen, port, instruments, verbose=verbose)#blocking
	
	port.close()

if __name__ == "__main__":
	f, k, s	= None, None, False
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
	f = "midis/Hare Hare Yukai.mid"
	#f = "midis/he is a pirate.mid"
	#f = "midis/kdikarus.mid"
	#f = "midis/Makrells.mid"
	#f = "midis/mt-pyre.mid"
	#f = "midis/native faith.mid"
	#f = "midis/portal_still_alive.mid"
	#f = "midis/Rhythm.mid"
	#f = "midis/Summer.mid"
	#f = "midis/Super_Smash_Bros_Brawl_Main_Theme.mid"
	#f = "midis/through-the-fire-and-flames.mid"
	#f = "midis/Windmill 2.mid"
	#f = "midis/Windmill.mid"
	
	#f = "midis/undertale/Death By Glamour.mid"
	#f = "midis/undertale/Determination.mid"
	#f = "midis/undertale/Dogsong.mid"
	#f = "midis/undertale/Enemy Approaching.mid"
	#f = "midis/undertale/Finale.mid"
	#f = "midis/undertale/Heartbreak.mid"
	#f = "midis/undertale/Megalovania.mid"
	#f = "midis/undertale/MIDIlovania.mid"
	#f = "midis/undertale/Ruins.mid"
	#f = "midis/undertale/Spider Dance.mid"
	
	#holy hell
	s = True
	#f = "midis/black midi/Death Waltz.mid"
	#f = "midis/black midi/bad apple 4.6 million.mid"#memoryerror
	#f = "midis/black midi/The Titan_2.mid"
	#f = "midis/black midi/.mid"
	
	main(keyboard=k, midifile=f, verbose=not s)
	








