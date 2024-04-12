
import pathlib
import numpy as np


class Path:
  ROOT = pathlib.Path(__file__).resolve().parent.parent
  RESOURCES = f'{ROOT}/resources'
  
  SAMPLE_WAV_FILE = f'{RESOURCES}/sample.wav'

class Settings:
  INPUT_CHUNK = 2048
  OUTPUT_CHUNK = INPUT_CHUNK * 2
  SAMPLE_RATE = 44100
  DTYPE = np.float32
  CHANNELS = 1