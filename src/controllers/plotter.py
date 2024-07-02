from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QScrollBar
from PyQt6.QtCore import QTimer, Qt
import numpy as np
import pyqtgraph as pg
from utils import States, shared_array_to_numpy
from settings import Settings
from scipy.signal import spectrogram


class Plotter(QMainWindow):
  def __init__(self, states: States):
    super().__init__()

    self.states = states
    self.x_axis = np.linspace(0, Settings.SAMPLE_RATE, Settings.INPUT_CHUNK)
    self.y1_axis = np.zeros(Settings.INPUT_CHUNK)
    self.y2_axis = np.zeros(Settings.INPUT_CHUNK)

    self.setWindowTitle('Sintetizador de Voz')

    layout = QVBoxLayout()
    
    self.plot_widget1 = pg.PlotWidget(title='Sinal de Entrada')
    self.curve1 = self.plot_widget1.plot(pen='b')
    layout.addWidget(self.plot_widget1)
    
    self.plot_widget2 = pg.PlotWidget(title='Sinal Processado')
    self.curve2 = self.plot_widget2.plot(pen='r')
    layout.addWidget(self.plot_widget2)
    
    self.plot_widget3 = pg.PlotWidget(title='Espectrograma Sinal de Entrada')
    self.spectrogram_1 = pg.ImageItem()
    self.plot_widget3.addItem(self.spectrogram_1)
    layout.addWidget(self.plot_widget3)

    self.plot_widget4 = pg.PlotWidget(title='Espectrograma Sinal Processado')
    self.spectrogram_2 = pg.ImageItem()
    self.plot_widget4.addItem(self.spectrogram_2)
    layout.addWidget(self.plot_widget4)
    
    self.scroll_bar = QScrollBar()
    self.scroll_bar.setOrientation(Qt.Orientation.Horizontal)
    self.scroll_bar.setRange(-12, 12)
    layout.addWidget(self.scroll_bar)

    central_widget = QWidget()
    central_widget.setLayout(layout)
    self.setCentralWidget(central_widget)
    
    self.scroll_bar.valueChanged.connect(self.change_pitch)
    
    self.timer = QTimer()
    self.timer.timeout.connect(self.update_plots)
    self.timer.start(10)


  def change_pitch(self, value):
    with self.states.lock:
      self.states.pitch_offset.value = value

  def update_plots(self):
    with self.states.lock:
      input_sample = shared_array_to_numpy(self.states.input_sample)
      output_sample = shared_array_to_numpy(self.states.output_sample)
    
    step = 1
    self.y1_axis[:-step] = self.y1_axis[step:]
    self.y1_axis[-step] = input_sample[-step]
    self.y2_axis[:-step] = self.y2_axis[step:]
    self.y2_axis[-step:] = output_sample[:step]
    
    f, t, Sxx_input = spectrogram(input_sample, fs=Settings.SAMPLE_RATE, nperseg=256)
    f, t, Sxx_output = spectrogram(output_sample, fs=Settings.SAMPLE_RATE, nperseg=256)

    self.curve1.setData(self.x_axis, self.y1_axis)
    self.curve2.setData(self.x_axis, self.y2_axis)

    self.spectrogram_1.setImage(Sxx_input)
    self.spectrogram_2.setImage(Sxx_output)