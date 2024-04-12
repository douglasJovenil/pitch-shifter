from PyQt6.QtWidgets import QApplication, QLabel
from pynput.keyboard import Key, Listener
from threading import Thread


app = QApplication([])

def init_pyqt():
  # Criação de uma instância de aplicativo Qt

  # Criação de um rótulo com o texto "Hello, World!"
  label = QLabel("Hello, World!")

  # Exibição da janela
  label.show()

  # Execução do loop de eventos do aplicativo
  app.exec()
  # app.quit()

def init_pynput():
  def on_press(key):
    if key == Key.esc:
      app.exit()
      return False

  # Cria e inicia o Listener
  with Listener(on_press=on_press) as listener:
    listener.join() 


Thread(target=init_pynput).start()
init_pyqt()