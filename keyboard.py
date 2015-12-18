#!python2
import time, mido
from operator import mul
mido.set_backend('mido.backends.pygame')#change this if you use something else
import audio_renderer as audio


def main(generatorClass, keyboard=None, midifile=None):
	if keyboard:
		midi_stream = mido.open_input(keyboard)
	elif midifile:
		midi_stream =  mido.MidiFile(midifile).play()
	else:
		return
	
	gen = generatorClass()
	stream = audio.play(gen)
	
	
	prev_clock = -0
	last_few_renders = []
	renderRate = str(round(float(audio.RATE)/audio.CHUNK, 2))
	for i in midi_stream:
		if i.type == "clock" or time.time()-prev_clock > 1./25.:#debug data
			t = time.time()
			h = t-prev_clock
			prev_clock = t
			
			last_few_renders.append((audio.get_rendercount_since_last_time(), h if h > 0 else 1))#huehue
			if len(last_few_renders)>50: del last_few_renders[0]
			
			if h > 0:
				h = round(1./h, 2)
			else:
				h = 0
			
			r = round(sum(map(lambda x:x[0], last_few_renders)) / sum(map(lambda x:x[1], last_few_renders)), 2)
			
			print "\nMido clock @%sHz, Render @%s/%sHz, Notes: %i" % (str(h).zfill(5), str(r).zfill(len(renderRate)), renderRate, len(gen.notes)),
		
		if i.type == "note_on":#note input
			if i.velocity == 0:
				gen.stop_note(i.note)
			else:
				gen.set_note(i.note, i.velocity)
			print "note(%i,%i)" % (i.note, i.velocity),
		elif i.type == "note_off":
			gen.stop_note(i.note)
		elif i.type not in ("clock",):
			print i.type,
			#if i.type == "control_change": print dir(i)
	
	midi_stream.close()

if __name__ == "__main__":
	
	f, k = None, None
	#k = mido.get_input_names()[0]#todo: give the user a choice?
	
	#f = "midis/13417_Ballad-of-the-Windfish.mid"
	#f = "midis/27641_Green-Greens.mid"
	#f = "midis/Clock Town 2.mid"
	#f = "midis/Clock Town.mid"
	#f = "midis/file.mid"
	#f = "midis/gerudo valley.mid"
	#f = "midis/Good Egg Galaxy.mid"
	#f = "midis/Gusty Garden Galaxy.mid"
	#f = "midis/Hare Hare Yukai.mid"
	#f = "midis/he is a pirate.mid"
	#f = "midis/kdikarus.mid"
	f = "midis/Makrells.mid"
	#f = "midis/mt-pyre.mid"
	#f = "midis/native faith.mid"
	#f = "midis/portal_still_alive.mid"
	#f = "midis/Rhythm.mid"
	#f = "midis/Summer.mid"
	#f = "midis/Super_Smash_Bros_Brawl_Main_Theme.mid"
	#f = "midis/through-the-fire-and-flames.mid"
	#f = "midis/Windmill 2.mid"
	#f = "midis/Windmill.mid"
	
	
	
	#main(audio.squareGenerator,    keyboard=k, midifile=f)
	#main(audio.sineGenerator,      keyboard=k, midifile=f)
	#main(audio.triangleGenerator,  keyboard=k, midifile=f)
	#main(audio.sawtoothGenerator,  keyboard=k, midifile=f)
	main(audio.dafuqGenerator,     keyboard=k, midifile=f)
	








