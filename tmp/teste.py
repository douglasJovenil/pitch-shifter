import sounddevice as sd
import numpy as np

# Definir as configurações de gravação
RATE = 44100  # Taxa de amostragem em Hz
DURATION = 2  # Duração da gravação em segundos

# Função de callback para processar os blocos de áudio
def callback(indata, frames, time, status):
    if status:
        print('Erro:', status)
    print(indata, indata.shape, indata.size, indata.dtype)
    # print(np.mean(indata))  # Processamento do áudio (exemplo: calcular a média dos dados de entrada)

print("Gravando...")
# Iniciar a gravação
with sd.InputStream(samplerate=RATE, channels=1, callback=callback, blocksize=1024):
    sd.sleep(int(DURATION * 1024))  # Aguardar o término da gravação

print("Gravação concluída.")