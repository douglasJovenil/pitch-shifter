from PyQt6.QtWidgets import QApplication
from controllers.plotter import Plotter
from controllers.microphone import Microphone
from utils import exit_handler, playback_handler, thread_starter, process_stater, States, print_handler
import sys
from multiprocessing import Process, Manager
from time import sleep
from random import randint

# def test_process():
#   print('process')
  
#   states = States()
#   from time import sleep
#   while True:
#     print(f'process: {states.dummy}')
#     sleep(0.2)

def main():
  print('main')
  # app = QApplication([])
  # interface = Microphone(chunk=1024)
  
  # plotter = Plotter(micrphone_interface=interface)
  # plotter.show()

  manager = Manager()
  # states = States()
  shared_states = manager.Value(States, States())
  
  Process(target=process_a, args=(shared_states, )).start()
  Process(target=process_b, args=(shared_states, )).start()
  
  
def process_a(states: States):
  while True:
    states.dummy = randint(1, 100)
    print(f'process A: {states.dummy}')
    sleep(0.2)

def process_b(states: States):
  while True:
    print(f'process B: {states.dummy}')
    sleep(0.2)


if __name__ == '__main__':
  main()
