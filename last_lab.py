import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QDialog, QLabel, QLineEdit, QComboBox, QMessageBox
import sqlite3

class FilmDialog(QDialog):
   def __init__(self, film_id=None):
      super().__init__()
      self.setWindowTitle('Добавить фильм')
      self.setFixedSize(300, 200)
      self.film_id = film_id  # Добавляем атрибут film_id

      layout = QVBoxLayout()

      self.title_input = QLineEdit()
      layout.addWidget(QLabel('Название:'))
      layout.addWidget(self.title_input)

      self.year_input = QLineEdit()
      layout.addWidget(QLabel('Год выпуска:'))
      layout.addWidget(self.year_input)

      self.genre_input = QComboBox()
      layout.addWidget(QLabel('Жанр:'))
      self.genre_input.addItems(['Драма', 'Комедия', 'Боевик', 'Фантастика', 'Триллер'])  
      layout.addWidget(self.genre_input)

      self.save_button = QPushButton('Сохранить')
      self.save_button.clicked.connect(self.save_film)
      layout.addWidget(self.save_button)

      self.setLayout(layout)

      # Если передан film_id, заполним поля диалога значениями фильма для редактирования
      if film_id:
         self.fill_fields()

   def fill_fields(self):
      conn = sqlite3.connect('films_db.sqlite')
      cursor = conn.cursor()
      cursor.execute('SELECT * FROM films WHERE id = ?', (self.film_id,))
      film = cursor.fetchone()
      conn.close()

      if film:
         self.title_input.setText(film[1])
         self.year_input.setText(str(film[2]))
         self.genre_input.setCurrentText(film[3])

   def save_film(self):
      title = self.title_input.text()
      year = self.year_input.text()
      genre = self.genre_input.currentText()

      if not title or not year:
         QMessageBox.warning(self, 'Предупреждение', 'Пожалуйста, заполните все поля.')
         return

      try:
         year = int(year)
      except ValueError:
         QMessageBox.warning(self, 'Предупреждение', 'Год выпуска должен быть числом.')
         return

      if year < 0 or year > 9999:
         QMessageBox.warning(self, 'Предупреждение', 'Некорректный год выпуска.')
         return

      conn = sqlite3.connect('films_db.sqlite')
      cursor = conn.cursor()
      if self.film_id:  # Если film_id задан, выполняем обновление записи
         cursor.execute('UPDATE films SET title = ?, year = ?, genre = ? WHERE id = ?',
                        (title, year, genre, self.film_id))
      else:
         cursor.execute('INSERT INTO films (title, year, genre) VALUES (?, ?, ?)', (title, year, genre))
      conn.commit()
      conn.close()

      self.accept()


class App(QWidget):
   def __init__(self):
      super().__init__()
      self.setWindowTitle('Фильмы')
      self.setGeometry(100, 100, 600, 400)

      layout = QVBoxLayout()

      self.table = QTableWidget()
      layout.addWidget(self.table)

      button_layout = QHBoxLayout()
      self.add_button = QPushButton('Добавить')
      self.add_button.clicked.connect(self.add_film)
      button_layout.addWidget(self.add_button)

      self.edit_button = QPushButton('Изменить')
      self.edit_button.clicked.connect(self.edit_film)
      button_layout.addWidget(self.edit_button)

      self.delete_button = QPushButton('Удалить')
      self.delete_button.clicked.connect(self.delete_film)
      button_layout.addWidget(self.delete_button)

      layout.addLayout(button_layout)

      self.setLayout(layout)

      self.update_table()

   def update_table(self):
      conn = sqlite3.connect('films_db.sqlite')
      cursor = conn.cursor()
      cursor.execute('SELECT * FROM films')
      films = cursor.fetchall()
      conn.close()

      self.table.setColumnCount(4)
      self.table.setHorizontalHeaderLabels(['ID', 'Название', 'Год', 'Жанр'])
      self.table.setRowCount(len(films))
      for i, film in enumerate(films):
         for j, value in enumerate(film):
               self.table.setItem(i, j, QTableWidgetItem(str(value)))

   def add_film(self):
      dialog = FilmDialog()
      if dialog.exec_() == QDialog.Accepted:
         self.update_table()

   def edit_film(self):
      selected_row = self.table.currentRow()
      if selected_row == -1:
         QMessageBox.warning(self, 'Предупреждение', 'Выберите фильм для редактирования.')
         return

      film_id = int(self.table.item(selected_row, 0).text())  # Преобразуем film_id в целое число
      dialog = FilmDialog(film_id)  # Передаем film_id в диалог редактирования
      dialog.setWindowTitle('Редактировать фильм')
      if dialog.exec_() == QDialog.Accepted:
         self.update_table()

   def delete_film(self):
      selected_row = self.table.currentRow()
      if selected_row == -1:
         QMessageBox.warning(self, 'Предупреждение', 'Выберите фильм для удаления.')
         return

      film_id = self.table.item(selected_row, 0).text()
      reply = QMessageBox.question(self, 'Удаление фильма', 'Вы уверены, что хотите удалить этот фильм?',
                                    QMessageBox.Yes | QMessageBox.No)
      if reply == QMessageBox.Yes:
         conn = sqlite3.connect('films_db.sqlite')
         cursor = conn.cursor()
         cursor.execute('DELETE FROM films WHERE id = ?', (film_id,))
         conn.commit()
         conn.close()
         self.update_table()


if __name__ == '__main__':
   conn = sqlite3.connect('films_db.sqlite')

   cursor = conn.cursor()

   cursor.execute('''
      CREATE TABLE IF NOT EXISTS films (
         id INTEGER PRIMARY KEY,
         title TEXT,
         year INTEGER,
         genre TEXT
      )
   ''')

   conn.commit()
   conn.close()

   app = QApplication(sys.argv)
   window = App()
   window.show()
   sys.exit(app.exec_())