import sys
from PyQt6.QtWidgets import QApplication
from Vue import Vue
from Modele import Modele
from AddArchive import AddArchive

class Controller:
    def __init__(self):
        
        self.app = QApplication([])
        self.vue = Vue(self.app)
        self.modele = Modele()
        self.add_archive_window = None

        self.update_vue()

        self.vue.main_widget.left.filterClicked.connect(self.update_vue)
        self.vue.main_widget.center.search.searchClicked.connect(self.update_vue)
        self.vue.main_widget.center.search.sortClicked.connect(self.update_vue)
        self.vue.main_widget.right.refreshClicked.connect(self.update_vue)
        self.vue.main_widget.right.addClicked.connect(self.open_archive_popup)
        self.vue.main_widget.right.openClicked.connect(self.open_folder)
        self.vue.main_widget.right.editAllClicked.connect(self.edit_all)
        self.vue.main_widget.right.confirmAllClicked.connect(self.confirm_all)
        self.vue.entree.connect(self.update_vue)

    
    def open_archive_popup(self):
        self.add_archive_window = AddArchive(self.vue.current_theme)
        self.add_archive_window.show()

        self.add_archive_window.confirmClicked.connect(self.add_archive)

    def add_archive(self, infos:dict):
        self.modele.add_archive(infos)
        self.update_vue()

    def edit(self, modifications:dict):
        self.modele.edit_archive(modifications)

    def edit_all(self):
        for entry in self.vue.main_widget.center.list.widget_list:
            entry.infos.enable_edit()

    def confirm_all(self):
        for entry in self.vue.main_widget.center.list.widget_list:
            entry.infos.edit_archive()

    def show_image(self, path:str):
        self.modele.open_archive(path)

    def open_folder(self):
        self.modele.open_folder()

    def update_vue(self):
        refreshed_list = self.modele.get_list()

        if self.vue.main_widget.center.search.search_bar.text():
            refreshed_list = self.modele.get_searched_list(self.vue.main_widget.center.search.search_bar.text())
        
        if self.vue.main_widget.center.search.sort.currentIndex() != 0:
            refreshed_list = self.modele.get_sorted_list(self.vue.main_widget.center.search.sort.itemText(self.vue.main_widget.center.search.sort.currentIndex()), refreshed_list)
        
        if self.vue.main_widget.left.after_date.date() != self.vue.main_widget.left.before_date.date() or self.vue.main_widget.left.img.isChecked() or self.vue.main_widget.left.pdf.isChecked() or self.vue.main_widget.left.other.isChecked():
            refreshed_list = self.modele.get_filtered_list({"after": self.vue.main_widget.left.after_date.date(),
                                                            "before": self.vue.main_widget.left.before_date.date(),
                                                            "img": self.vue.main_widget.left.img.isChecked(),
                                                            "other": self.vue.main_widget.left.other.isChecked(),
                                                            "pdf": self.vue.main_widget.left.pdf.isChecked()}, refreshed_list)
        
        if refreshed_list is not None:
            self.vue.main_widget.center.list.update_list(refreshed_list)
    
        self.connect_entries_signals()

    def connect_entries_signals(self):
        for entry in self.vue.main_widget.center.list.widget_list:
            entry.infos.editClicked.connect(self.edit)
            entry.image.imageClicked.connect(self.show_image)


if __name__ == "__main__":
    controller = Controller()
    sys.exit(controller.app.exec())
