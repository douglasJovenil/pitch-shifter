from utils import States, process_stater, exit_handler, shared_array_to_numpy, thread_stater
import numpy as np
from settings import Settings
from PyQt6.QtWidgets import QApplication
from controllers.plotter import Plotter
import sounddevice as sd
import librosa
from time import perf_counter
from utils import time_it
import aubio


def main():
  states = States()
  app = QApplication([])
  plotter = Plotter(states=states)

  plotter.show()
  process_stater(microphone_process, states)
  process_stater(audio_synthesis_process, states)
  process_stater(playback_handler, states)    
  exit_handler(states, app)
  app.exec()

  
def microphone_process(states: States):
  stream = sd.Stream(samplerate=Settings.SAMPLE_RATE, channels=Settings.CHANNELS, blocksize=Settings.INPUT_CHUNK, latency='low')
  stream.start()
  
  while states.running.value:
    # with time_it('microphone_process'):
    if stream.read_available >= Settings.INPUT_CHUNK:
      sample = stream.read(Settings.INPUT_CHUNK)[0]
      
      with states.lock:
        states.input_sample[:] = sample[:]

  stream.abort()

def audio_synthesis_process(states):
  print('audio_synthesis_process started')
  while states.running.value:
    # with time_it('audio_synthesis_process'):
    with states.lock:
      sample = shared_array_to_numpy(states.input_sample)
      mean = np.mean(np.abs(sample))
      
      if mean > 0.0001:
        pitch_shift_steps = states.pitch_offset.value
        sample = librosa.effects.pitch_shift(
          sample, 
          sr=Settings.SAMPLE_RATE, 
          n_steps=pitch_shift_steps
        )
        states.output_sample[:] = sample[:]

def playback_handler(states: States):
  stream = sd.OutputStream(
    samplerate=Settings.SAMPLE_RATE,
    channels=Settings.CHANNELS,
    dtype=Settings.DTYPE,
    blocksize=Settings.INPUT_CHUNK,
    latency='low'
  )
  
  stream.start() 
  
  while states.running.value:
    # with time_it('playback_handler'):
    if stream.write_available >= Settings.INPUT_CHUNK * 2:
      with states.lock:
        sample = shared_array_to_numpy(states.output_sample)
        stream.write(sample)
        states.output_sample[:] = np.zeros(Settings.INPUT_CHUNK, dtype=Settings.DTYPE)[:]

  stream.abort()

  

if __name__ == '__main__':
  main()
