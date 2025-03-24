import sys
import os
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QCheckBox, QComboBox, QDateEdit, QScrollArea, QTextEdit, QLineEdit
from PyQt6.QtGui import QPainter, QPixmap, QPen, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from qt_material import apply_stylesheet
from utils import convert_date_to_str

class Vue(QMainWindow):

    entree = pyqtSignal()

    def __init__(self, app):
        super().__init__()


        self.setWindowTitle("J-Archives")
        self.setWindowIcon(QIcon(os.path.join("icones", "j-archives.png")))

        self.app = app
        self.main_widget = MainWidget()
        self.current_theme = "light_blue.xml"

        self.setStyle(self.current_theme)

        self.setCentralWidget(self.main_widget)

        menu_bar = self.menuBar()
        styles = ["dark_blue.xml", "light_blue.xml"]
        styles_fr = ["Sombre", "Clair"]

        menu_file = menu_bar.addMenu("&Fichier")
        menu_file.addAction("Ajouter une archive", self.main_widget.right.send_add)

        menu_edit = menu_bar.addMenu("&Edition")
        menu_edit.addAction("Ouvrir le fichier d'archives", self.main_widget.right.send_open)
        menu_edit.addAction("Actualiser la liste", self.main_widget.right.send_refresh)
        menu_edit.addAction("Passer toutes les archives en édition", self.main_widget.right.send_edit_all)
        menu_edit.addAction("Confirmer la modifications de toutes les archives", self.main_widget.right.send_confirm_all)
        menu_edit.addAction("Réinitialiser tous les filtres", self.main_widget.left.reset_filters)
        menu_theme = menu_bar.addMenu("&Thèmes")

        for i in range(len(styles)):
            action = menu_theme.addAction(styles_fr[i])
            action.triggered.connect(lambda checked, style=styles[i]: self.setStyle(style))

        self.show()

    
    def setStyle(self, style:str):
        apply_stylesheet(self.app, style)
        self.current_theme = style
        if style.startswith("dark"):
            self.main_widget.setStyleSheet("color: white")
        else:
            self.main_widget.setStyleSheet("color: black")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            self.entree.emit()


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout() ; self.setLayout(layout)

        self.left = Left()
        self.center = Center()
        self.right = Right()

        layout.addWidget(self.left)
        layout.addWidget(self.center)
        layout.addWidget(self.right)


class Left(QWidget):

    filterClicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout() ; self.setLayout(layout)

        self.type = QLabel("Type de fichiers")
        self.pdf = QCheckBox("PDF")
        self.img = QCheckBox("Image (png, jpg, jpeg...)")
        self.other = QCheckBox("Autres")

        self.before = QLabel("Avant le:")
        self.before_date = QDateEdit()
        self.before_date.setMinimumDate(QDate(0, 1, 1))
        self.before_date.setMaximumDate(QDate(10000, 31, 12))

        self.after = QLabel("Après le:")
        self.after_date = QDateEdit()
        self.after_date.setMinimumDate(QDate(0, 1, 1))
        self.after_date.setMaximumDate(QDate(10000, 31, 12))

        self.filter = QPushButton("Filtrer")
        self.reset = QPushButton("Réinitialiser les\nfiltres")


        layout.addStretch()
        layout.addWidget(self.type)
        layout.addWidget(self.pdf)
        layout.addWidget(self.img)
        layout.addWidget(self.other)
        layout.addSpacing(10)
        layout.addWidget(self.before)
        layout.addWidget(self.before_date)
        layout.addSpacing(10)
        layout.addWidget(self.after)
        layout.addWidget(self.after_date)
        layout.addSpacing(20)
        layout.addWidget(self.filter)
        layout.addWidget(self.reset)
        layout.addStretch()


        self.filter.clicked.connect(self.send_filter)
        self.reset.clicked.connect(self.reset_filters)
    
    
    def send_filter(self):
        self.filterClicked.emit()

    def reset_filters(self):
        self.pdf.setChecked(False)
        self.img.setChecked(False)
        self.other.setChecked(False)
        self.before_date.setDate(QDate(2000, 1, 1))
        self.after_date.setDate(QDate(2000, 1, 1))
        self.send_filter()


class Center(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout() ; self.setLayout(layout)

        self.search = Search()
        self.list = Liste()
        self.scrollable_list = QScrollArea()
        self.scrollable_list.setWidget(self.list)
        self.scrollable_list.setWidgetResizable(True)
        self.scrollable_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollable_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollable_list.setMinimumSize(640, 480)

        layout.addWidget(self.search)
        layout.addWidget(self.scrollable_list)

    
    def paintEvent(self, event):
            painter = QPainter(self)
            pen = QPen(Qt.GlobalColor.gray)
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
            painter.drawLine(0, 0, 0, self.height())


class Search(QWidget):

    searchClicked = pyqtSignal()
    sortClicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        layout = QHBoxLayout() ; self.setLayout(layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Tapez votre recherche...")

        self.search_button = QPushButton("Rechercher")

        self.sort = QComboBox()
        self.sort.addItem("Trier par")
        self.sort.addItem("Nom (alphabétique)")
        self.sort.addItem("Nom (antialphabétique)")
        self.sort.addItem("Date (du plus ancien)")
        self.sort.addItem("Date (du plus récent)")
        self.sort.setMinimumWidth(200)


        layout.addWidget(self.search_bar)
        layout.addWidget(self.sort)
        layout.addWidget(self.search_button)


        self.search_button.clicked.connect(self.send_search)
        self.sort.currentIndexChanged.connect(self.send_sort)


    def send_search(self):
        self.searchClicked.emit()

    def send_sort(self):
        self.sortClicked.emit()


class Right(QWidget):

    addClicked = pyqtSignal()
    openClicked = pyqtSignal()
    refreshClicked = pyqtSignal()
    editAllClicked = pyqtSignal()
    confirmAllClicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout() ; self.setLayout(layout)

        self.setMaximumWidth(200)

        self.logo = Image(os.path.join("icones", "j-archives.png"), width=150)

        self.label1 = QLabel("Actualisez la liste après")
        self.label2 = QLabel("avoir ajouté ou retiré des")
        self.label3 = QLabel("archives du fichier d'archives.")

        self.add = QPushButton("Ajouter une archive")
        self.open = QPushButton("Ouvrir le fichier\nd'archives")
        self.refresh = QPushButton("Actualiser la\nliste d'archives")
        self.edit_all = QPushButton("Passer toutes les\n archives en édition")
        self.confirm_all = QPushButton("Confirmer toutes\n les archives")

        self.add.setFixedHeight(50)
        self.open.setFixedHeight(50)
        self.refresh.setFixedHeight(50)
        self.edit_all.setFixedHeight(50)
        self.confirm_all.setFixedHeight(50)


        layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.label1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label2, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label3, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(30)
        layout.addWidget(self.add)
        layout.addWidget(self.open)
        layout.addWidget(self.refresh)
        layout.addWidget(self.edit_all)
        layout.addWidget(self.confirm_all)
        layout.addStretch()


        self.add.clicked.connect(self.send_add)
        self.open.clicked.connect(self.send_open)
        self.refresh.clicked.connect(self.send_refresh)
        self.edit_all.clicked.connect(self.send_edit_all)
        self.confirm_all.clicked.connect(self.send_confirm_all)


    def send_add(self):
        self.addClicked.emit()

    def send_open(self):
        self.openClicked.emit()

    def send_refresh(self):
        self.refreshClicked.emit()

    def send_edit_all(self):
        self.editAllClicked.emit()
    
    def send_confirm_all(self):
        self.confirmAllClicked.emit()


class Liste(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout() ; self.setLayout(self.layout)

        self.widget_list = []

        self.setMinimumHeight(len(self.widget_list)*250)


    def update_list(self, liste:dict):
        self.widget_list.clear()

        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.layout.addStretch()
        for archive in liste.keys():
            entry = Entry(liste[archive], archive)
            self.widget_list.append(entry)
            self.layout.addWidget(entry)
        self.layout.addStretch()


class Entry(QWidget):
    def __init__(self, infos:dict, archive:str):
        super().__init__()

        layout = QHBoxLayout() ; self.setLayout(layout)

        if infos["path"][-4:] == ".pdf":
            self.image = Image("icones/pdf.png", infos["path"])
        else:
            self.image = Image(infos["path"])

        self.infos = Infos(infos, archive)

        layout.addWidget(self.image)
        layout.addWidget(self.infos)

        self.setFixedHeight(250)


    def paintEvent(self, event):
            painter = QPainter(self)
            pen = QPen(Qt.GlobalColor.gray)
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawLine(0, 0, self.width() - 1, 0)


class Infos(QWidget):

    editClicked = pyqtSignal(dict)

    def __init__(self, infos:dict, archive:str):
        super().__init__()
        
        layout = QVBoxLayout() ; self.setLayout(layout)
        name_layout = QHBoxLayout()

        self.infos_dict = infos
        self.archive = archive

        showed_name = self.archive if len(self.archive) <= 20 else self.archive[:20] + "..." + self.archive[-4:]
        self.name = QLabel("Nom du fichier: " + showed_name)
        self.name.setStyleSheet("font-size: 20px")

        if self.archive[-5:] != ".jpeg":
            self.edit_name = QLineEdit(self.archive[:-4])
            self.extension = QLabel(self.archive[-4:])
        else:
            self.edit_name = QLineEdit(self.archive[:-5])
            self.extension = QLabel(self.archive[-5:])


        if self.infos_dict["description"]:
            self.desc = QTextEdit(self.infos_dict["description"])
        else:
            self.desc = QTextEdit("Modifiez l'archive pour ajouter une description")

        self.desc.setReadOnly(True)
        self.desc.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.desc.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.desc.setStyleSheet("border: none")


        if self.infos_dict["date"]:
            self.date = QLabel("Date: " + self.infos_dict["date"])
            self.edit_date = QDateEdit(QDate(int(self.infos_dict["date"][-4:]), int(self.infos_dict["date"][3:5]), int(self.infos_dict["date"][:2])))
        else:
            self.date = QLabel("Date: Modifiez l'archive pour ajouter une date")
            self.edit_date = QDateEdit()

        self.date.setStyleSheet("font-size: 18px")
        self.edit_date.setMinimumDate(QDate(0, 1, 1))
        self.edit_date.setMaximumDate(QDate(10000, 31, 12))


        self.edit = QPushButton("Modifier l'archive")
        self.confirm_edit = QPushButton("Confirmer la modification")


        self.edit_name.hide()
        self.extension.hide()
        self.edit_date.hide()
        self.confirm_edit.hide()


        name_layout.addWidget(self.name)
        name_layout.addWidget(self.edit_name)
        name_layout.addWidget(self.extension)
        layout.addLayout(name_layout)
        layout.addWidget(self.desc)
        layout.addWidget(self.date)
        layout.addWidget(self.edit_date)
        layout.addWidget(self.edit)
        layout.addWidget(self.confirm_edit)



        self.edit.clicked.connect(self.enable_edit)
        self.confirm_edit.clicked.connect(self.edit_archive)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            self.edit_archive()

    def enable_edit(self):
        self.name.hide()
        self.edit_name.show()
        self.extension.show()
        self.desc.setReadOnly(False)
        self.date.hide()
        self.edit_date.show()
        self.edit.hide()
        self.confirm_edit.show()

        self.edit_name.setStyleSheet("border: 2px solid black;")
        self.desc.setStyleSheet("border: 2px solid black;")
        self.edit_date.setStyleSheet("border: 2px solid black;")

    def edit_archive(self):
        self.editClicked.emit({"old_name": self.archive,
                               "name": self.edit_name.text() + self.extension.text(),
                               "description": self.desc.toPlainText(),
                               "date": convert_date_to_str(self.edit_date.date())})
        
        showed_name = self.edit_name.text() + self.extension.text() if len(self.edit_name.text()) <= 20 else self.edit_name.text()[:20] + "..." + self.extension.text()
        self.name.setText("Nom du fichier: " + showed_name)
        self.date.setText("Date: " + convert_date_to_str(self.edit_date.date()))
        self.archive = self.edit_name.text() + self.extension.text()
        
        self.edit_name.hide()
        self.extension.hide()
        self.name.show()
        self.desc.setReadOnly(True)
        self.edit_date.hide()
        self.date.show()
        self.confirm_edit.hide()
        self.edit.show()

        self.desc.setStyleSheet("border: none")


class Image(QLabel):
    
    imageClicked = pyqtSignal(str)

    def __init__(self, path:str, pdf_path:str=None, width:int=100):
        super().__init__()
        
        self.path = path
        self.pdf_path = pdf_path
        self.image = QPixmap(self.path).scaledToWidth(width)
        self.setPixmap(self.image)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            image_rect = self.pixmap().rect()
            image_rect.moveCenter(self.rect().center())

            if image_rect.contains(event.pos()):
                if self.pdf_path:
                    self.imageClicked.emit(self.pdf_path)
                else:
                    self.imageClicked.emit(self.path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Vue(app)
    sys.exit(app.exec())
