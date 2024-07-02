from PyQt6.QtWidgets import QApplication
from threading import Thread
from pypattyrn.creational.singleton import Singleton
import numpy as np
from typing import Callable
from multiprocessing import Process, Value, Lock, Array

from keyboard._keyboard_event import KeyboardEvent

from time import perf_counter
from contextlib import contextmanager

import keyboard
from settings import Settings
from multiprocessing.sharedctypes import SynchronizedArray

class States(object, metaclass=Singleton):
  def __init__(self):
    super().__init__()
    # 'i': inteiro
    # 'd': ponto flutuante
    # 'b': booleano
    # 'c': caractere
    # 'h': inteiro longo
    # 'I': inteiro sem sinal
    # 'f': ponto flutuante de precisão simples
    # 'd': ponto flutuante de precisão dupla
    self.running = Value('b', True)
    self.input_sample = Array('f', np.zeros(Settings.INPUT_CHUNK, dtype=Settings.DTYPE))
    self.output_sample = Array('f', np.zeros(Settings.INPUT_CHUNK, dtype=Settings.DTYPE))
    self.pitch_offset = Value('i', 0)
    self.lock = Lock()


processes: list[Process] = []
threads: list[Thread] = []

def exit_handler(states: States, app: QApplication):
  def on_key_pressed(event: KeyboardEvent):
    if event.name == 'esc':
      print('Stopping')
      with states.lock:
        states.running.value = False

      # interface = Microphone()
      # interface.stop()
      for process in processes: process.terminate()
      for thread in threads: thread.join()
      app.exit()

  keyboard.on_press(on_key_pressed)


def shared_array_to_numpy(shared_array: SynchronizedArray):
  return np.array(shared_array.get_obj(), dtype=Settings.DTYPE)


def process_stater(target: Callable, *args: tuple):
  process = Process(target=target, args=args)
  processes.append(process)
  process.start()
  
def thread_stater(target: Callable, *args: tuple):
  thread = Thread(target=target, args=args)
  threads.append(thread)
  thread.start()

@contextmanager
def time_it(block_name: str):
  start = perf_counter()
  yield
  if perf_counter() - start > 1:
    print(f'{block_name} took: {perf_counter() - start}')