import numpy as np
import librosa
import soundfile as sf


def main():
  waveform, sr = librosa.load('./resources/sample.wav', sr=None, mono=False)
  
  # output_wave = pitch_shift(waveform[1], 10)
  output_wave = librosa.effects.pitch_shift(
    waveform, 
    sr=sr, 
    n_steps=0
  )[1]
  
  print(output_wave.shape)
  
  sf.write('output.wav', output_wave, sr*2)

def pitch_shift(signal, n_steps):
  factor = 2**(n_steps / 12.0)
  window_size = 1024
  hop_size = window_size // 4

  # Pad the signal to make sure the end is handled properly
  signal = np.pad(signal, window_size, mode='constant')

  result = np.zeros_like(signal)

  for i in range(0, len(signal) - window_size, hop_size):
    # Apply a window function to the segment
    segment = signal[i:i+window_size] * np.hanning(window_size)

    # Transform to the frequency domain
    spectrum = np.fft.fft(segment)
    magnitude = np.abs(spectrum)
    phase = np.angle(spectrum)

    # Shift the frequencies
    new_spectrum = np.zeros_like(spectrum)
    indices = np.round(np.arange(0, window_size) * factor).astype(int)
    for j in range(window_size):
      if indices[j] < window_size:
        new_spectrum[indices[j]] = magnitude[j] * np.exp(1j * phase[j])

    # Transform back to the time domain
    new_segment = np.fft.ifft(new_spectrum).real

    # Overlap-add
    result[i:i+window_size] += new_segment * np.hanning(window_size)

  # Remove padding and normalize
  result = result[window_size:-window_size]
  result = np.int16(result / np.max(np.abs(result)) * 32767)

  return result


if __name__ == '__main__':
  main()