
from typing import Any

import librosa
import numpy as np
import scipy



def pitch_shift(sample: np.ndarray, sr: int, n_steps: int) -> np.ndarray:
  rate = 2.0 ** (-float(n_steps) / 12) # 12 semitones per octave

  # Stretch in time, then resample
  y_shift = resample(
    time_stretch(sample, rate=rate),
    orig_sr=float(sr) / rate,
    target_sr=sr
  )

  # Crop to the same dimension as the input
  return fix_length(y_shift, size=sample.shape[-1])


def time_stretch(y: np.ndarray, rate: float) -> np.ndarray:
  # Construct the short-term Fourier transform (STFT)
  stft = librosa.core.stft(y)

  ###############
  
  n_fft = 2 * (stft.shape[-2] - 1)
  hop_length = int(n_fft // 4)

  time_steps = np.arange(0, stft.shape[-1], rate, dtype=np.float64)

  # Create an empty output array
  shape = list(stft.shape)
  shape[-1] = len(time_steps)
  stft_stretch = np.zeros_like(stft, shape=shape)

  # Expected phase advance in each bin
  phi_advance = np.linspace(0, np.pi * hop_length, stft.shape[-2])

  # Phase accumulator; initialize to the first sample
  phase_acc = np.angle(stft[..., 0])

  # Pad 0 columns to simplify boundary logic
  padding = [(0, 0) for _ in stft.shape]
  padding[-1] = (0, 2)
  stft = np.pad(stft, padding, mode="constant")

  for t, step in enumerate(time_steps):
    columns = stft[..., int(step) : int(step + 2)]

    # Weighting for linear magnitude interpolation
    alpha = np.mod(step, 1.0)
    mag = (1.0 - alpha) * np.abs(columns[..., 0]) + alpha * np.abs(columns[..., 1])

    # Store to output array
    stft_stretch[..., t] = librosa.util.phasor(phase_acc, mag=mag)

    # Compute phase advance
    dphase = np.angle(columns[..., 1]) - np.angle(columns[..., 0]) - phi_advance

    # Wrap to -pi:pi range
    dphase = dphase - 2.0 * np.pi * np.round(dphase / (2.0 * np.pi))

    # Accumulate phase
    phase_acc += phi_advance + dphase
  
  #############

  # Predict the length of y_stretch
  len_stretch = int(round(y.shape[-1] / rate))

  # Invert the STFT
  y_stretch = librosa.core.istft(stft_stretch, dtype=y.dtype, length=len_stretch)

  return y_stretch

def resample(y: np.ndarray, orig_sr: float, target_sr: float, axis: int = -1,) -> np.ndarray:
  if orig_sr == target_sr:
    return y

  ratio = float(target_sr) / orig_sr
  n_samples = int(np.ceil(y.shape[axis] * ratio))
  y_hat = scipy.signal.resample(y, n_samples, axis=axis)

  # Match dtypes
  return np.asarray(y_hat, dtype=y.dtype)


def fix_length(data: np.ndarray, *, size: int, axis: int = -1) -> np.ndarray:
  slices = [slice(None)] * data.ndim
  slices[axis] = slice(0, size)
  return data[tuple(slices)]