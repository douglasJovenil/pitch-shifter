import librosa
import numpy as np
import scipy



def pitch_shift(sample: np.ndarray, sr: int, n_steps: int) -> np.ndarray:
  rate = 2.0 ** (-float(n_steps) / 12) # 12 tom por oitava

  y_shift = resample(
    time_stretch(sample, rate=rate),
    orig_sr=float(sr) / rate,
    target_sr=sr
  )

  # Mantém a mesma dimensao do sinal de entrada
  return fix_length(y_shift, size=sample.shape[-1])


def time_stretch(y: np.ndarray, rate: float) -> np.ndarray:
  stft = librosa.core.stft(y)
  n_fft = 2 * (stft.shape[-2] - 1)
  hop_length = int(n_fft // 4)
  time_steps = np.arange(0, stft.shape[-1], rate, dtype=np.float64)

  # Array de saida vazio
  shape = list(stft.shape)
  shape[-1] = len(time_steps)
  stft_stretch = np.zeros_like(stft, shape=shape)

  # A fase avanca a cada iteracao
  phi_advance = np.linspace(0, np.pi * hop_length, stft.shape[-2])

  # Acumulador de fase vazio
  phase_acc = np.angle(stft[..., 0])

  # Adiciona zero nas bordas para facilitar o merge das bordas das janelas
  padding = [(0, 0) for _ in stft.shape]
  padding[-1] = (0, 2)
  stft = np.pad(stft, padding, mode="constant")

  for t, step in enumerate(time_steps):
    columns = stft[..., int(step) : int(step + 2)]

    # Normalizacao da magnitude da interpolacao
    alpha = np.mod(step, 1.0)
    mag = (1.0 - alpha) * np.abs(columns[..., 0]) + alpha * np.abs(columns[..., 1])

    # Adiciona o resultado no vetor de saida
    stft_stretch[..., t] = librosa.util.phasor(phase_acc, mag=mag)

    # Calcula o avanco de fase
    dphase = np.angle(columns[..., 1]) - np.angle(columns[..., 0]) - phi_advance

    # Envelopa no range de -pi até pi
    dphase = dphase - 2.0 * np.pi * np.round(dphase / (2.0 * np.pi))

    # Soma a fase
    phase_acc += phi_advance + dphase

  # Calcula a largura de y_strech
  len_stretch = int(round(y.shape[-1] / rate))

  # Transformada inversa
  y_stretch = librosa.core.istft(stft_stretch, dtype=y.dtype, length=len_stretch)

  return y_stretch

def resample(y: np.ndarray, orig_sr: float, target_sr: float, axis: int = -1,) -> np.ndarray:
  if orig_sr == target_sr:
    return y

  ratio = float(target_sr) / orig_sr
  n_samples = int(np.ceil(y.shape[axis] * ratio))
  y_hat = scipy.signal.resample(y, n_samples, axis=axis)
  return np.asarray(y_hat, dtype=y.dtype)


def fix_length(data: np.ndarray, *, size: int, axis: int = -1) -> np.ndarray:
  slices = [slice(None)] * data.ndim
  slices[axis] = slice(0, size)
  return data[tuple(slices)]