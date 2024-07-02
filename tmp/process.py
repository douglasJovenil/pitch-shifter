import librosa
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

def main():
  waveform, sr = librosa.load('./resources/sample.wav', sr=None, mono=False)
  CHANNELS, WAVE_TOTAL_LEN = waveform.shape
  WINDOW_LEN = 1351 # 1, 7, 97, 193, 679, 1351, 18721
  WINDOW_FUNCTION = np.hanning(WINDOW_LEN)
  HOP_LEN = 679

  f_scaling = lambda n: 2 ** (n/12) # N = numero de semitons para aumentar | 12 quantidade de simitons em uma oitava
  SCALING = f_scaling(5) # aumentar o tom em 5 semitons
  HOP_LEN_SCALING = int(HOP_LEN * SCALING) # constante utilizado para dar "stretch" no samplerate final
  SYNTH_WIN_LEN = int(WINDOW_LEN // SCALING)

  new_waveform_len = int(np.ceil(WAVE_TOTAL_LEN / HOP_LEN) * HOP_LEN_SCALING) + SYNTH_WIN_LEN
  new_waveform = np.zeros((CHANNELS, new_waveform_len))
  new_scales = np.zeros(new_waveform_len)

  # loop through windows
  for i in range(0, WAVE_TOTAL_LEN, HOP_LEN):
    clipped_len = min(i + WINDOW_LEN, WAVE_TOTAL_LEN - 2) - i
    
    # stretch to synth_win_len. see how this interpolation could lose information
    idxs = np.linspace(i, i + clipped_len, SYNTH_WIN_LEN)
    start = idxs.astype(int)
    frac = idxs - start
    window = waveform[:, start] * (1 - frac) + waveform[:, start + 1] * frac

    # add window to new waveform
    new_waveform[:, i:i + SYNTH_WIN_LEN] += window * WINDOW_FUNCTION[None, :]
    # add up windowing weights for normalization
    new_scales[i:i + SYNTH_WIN_LEN] += WINDOW_FUNCTION[:]

  # # splited_waves = np.split(waveform, WINDOWS, axis=0)
  # # ftf_sample_waves = [librosa.stft(wave, n_fft=1024) for wave in splited_waves]
  # # ftf_synthetized_waves = [ ftf_wave * PITCH_OFFSET for ftf_wave in ftf_sample_waves ]
  # # synthetized_waves = [ librosa.istft(wave) for wave in ftf_synthetized_waves ]
  # # concatenated_wave = np.concatenate(synthetized_waves)

  # sf.write('output.wav', output_wave, sr*2)

  # # print(waveform.shape)
  # # print(concatenated_wave.shape)

  # plt.plot(new_waveform_len)
  # plt.show()
  # # print(sr)


def calculate_possible_windows(array: np.ndarray) -> list[int]:
  return [ i for i in range(1, array.shape[0]) if array.shape[0] % i == 0 ]


# anls_win_len = 5000 # / 44100 = 113.3786848 ms
# anls_hop_len = 2000 # / 44100 = 45.35147392 ms
# scaling = 2 ** (5 / 12)
# synth_hop_len = anls_hop_len
# synth_win_len = int(anls_win_len // scaling)
# win_f = np.hanning(synth_win_len)

# new_waveform_len = int(np.ceil(og_len / anls_hop_len) * synth_hop_len) + synth_win_len
# new_waveform = np.zeros((channels, new_waveform_len)) # stereo audio
# new_scales = np.zeros(new_waveform_len)

# # loop through windows
# for i in range(0, og_len, anls_hop_len):
#     clipped_len = min(i + anls_win_len, og_len - 2) - i
    
#     # stretch to synth_win_len. see how this interpolation could lose information
#     idxs = np.linspace(i, i + clipped_len, synth_win_len)
#     start = idxs.astype(int)
#     frac = idxs - start
#     window = waveform[:, start] * (1 - frac) + waveform[:, start + 1] * frac

#     # add window to new waveform
#     new_waveform[:, i:i + synth_win_len] += window * win_f[None, :]
#     # add up windowing weights for normalization
#     new_scales[i:i + synth_win_len] += win_f[:]

# new_waveform = new_waveform / np.where(new_scales == 0, 1, new_scales)

# idisplay.display(idisplay.Audio(new_waveform, rate=sr))

if __name__ == '__main__':
  main()