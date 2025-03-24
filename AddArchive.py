import os
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton, QCalendarWidget, QWidget, QVBoxLayout, QFileDialog, QTextEdit, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QIcon
from utils import convert_date_to_str

class AddArchive(QWidget):

    confirmClicked = pyqtSignal(dict)

    def __init__(self, theme:str):
        super().__init__()

        self.setWindowTitle("Ajoutez une archive")
        self.setWindowIcon(QIcon(os.path.join("icones", "j-archives.png")))

        layout = QVBoxLayout() ; self.setLayout(layout)
        file_layout = QHBoxLayout()

        if theme.startswith("dark"):
            self.setStyleSheet("color: white")
        else:
            self.setStyleSheet("color: black")

        self.selected_archive_file_name = ""

        self.import_button = QPushButton("Importer une archive")
        self.name_label = QLabel("Nom du fichier:")
        self.name = QLineEdit()
        self.name.setPlaceholderText("Entrez un nom du fichier")
        self.extension = QLabel(".???")
        self.description_label = QLabel("Description:")
        self.description = QTextEdit()
        self.description.setPlaceholderText("Entrez une description")
        self.date_label = QLabel("Date:")
        self.date = QCalendarWidget()
        self.date.setMinimumDate(QDate(0, 1, 1))
        self.date.setMaximumDate(QDate(10000, 31, 12))
        self.confirm = QPushButton("Ajouter l'archive")


        layout.addWidget(self.import_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)
        file_layout.addWidget(self.name)
        file_layout.addWidget(self.extension)
        layout.addLayout(file_layout)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description)
        layout.addWidget(self.date_label)
        layout.addWidget(self.date)
        layout.addWidget(self.confirm)


        self.import_button.clicked.connect(self.import_archive)
        self.confirm.clicked.connect(self.send_confirm)

    
    def import_archive(self):
        file = QFileDialog().getOpenFileName()[0]
        if file:
            self.selected_archive_file_name = file

            name, extension = file.split(".")

            cut_name = ""
            counter = len(name)-1
            while name[counter] != "/":
                cut_name += name[counter]
                counter -= 1
            cut_name = cut_name[::-1]
            extension = "." + extension

            self.name.setText(cut_name)
            self.extension.setText(extension)
        
    def send_confirm(self):
        if self.selected_archive_file_name:
            self.confirmClicked.emit({"src": self.selected_archive_file_name,
                                    "name": self.name.text() + self.extension.text(),
                                    "description": self.description.toPlainText(),
                                    "date": convert_date_to_str(self.date.selectedDate())})
            self.close()
            del self