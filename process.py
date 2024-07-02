
import librosa
import soundfile as sf
import numpy as np
import scipy
from typing import Any
from src import dsp


def main():
  sample, sr = librosa.load('./resources/sample.wav', sr=None, mono=False)
  n_steps = 32
  
  output_wave = dsp.pitch_shift(sample, sr, n_steps)
  
  sf.write('output.wav', output_wave[1], sr)



if __name__ == '__main__':
  main()