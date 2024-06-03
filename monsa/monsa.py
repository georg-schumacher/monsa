
from time import sleep
from os.path import basename, dirname
from typing import List, Tuple, Dict
from os.path import dirname, basename
import sys
from PyQt5.QtWidgets import (
    QLabel,
    QApplication,
    QCheckBox,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTableView,
    QPushButton,
    QLineEdit,
    QSplitter,
    QProgressBar,
    QHeaderView,
    QListView,
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QStringListModel, Qt
# https://otrkeyfinder.com/de/?search=ard+HD

import os
from os.path import basename, dirname, abspath
from typing import List
import pickle
from PyQt5.QtCore import QThread, pyqtSignal

import requests
from bs4 import BeautifulSoup
##################################
##################################
##################################
current_dir = dirname(abspath(__file__))
parent_dir = dirname(current_dir)
sys.path.insert(0, parent_dir)
##################################
##################################


ALLOWED_EXTENSIONS = [".mp4", ".mkv", ".avi", ".ts"]
IGNORED_FOLDERS = [
    ".actors",
    ".deletedByTMM",
    "$RECYCLE.BIN",
]


class FileCollector(QThread):
    progress = pyqtSignal(int)
    file_list_collected_signal = pyqtSignal(list)

    def __init__(
        self,
        # persistency_file="C:\\ws\\py\\jsoup\\local_file_list_cached.pkl",
        persistency_file="/home/sg82fe/.local_file_list_cached.pkl",

    ):
        super().__init__()
        self.persistency_file = persistency_file
        if os.path.exists(self.persistency_file):
            with open(self.persistency_file, "rb") as f:
                self.file_list_cached = pickle.load(f)
        else:
            self.file_list_cached = []
        self.total_files = max(10, len(self.file_list_cached))

    def set_dir(self, directories: str):
        self.directories = directories

    def run(self):
        file_list = []
        current_files = 0
        for directory in self.directories.split(";"):
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS]
                for file in files:
                    if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                        full_file_path = os.path.join(root, file)
                        size_b = os.path.getsize(full_file_path)
                        size_gb = size_b / (1024*1024*1024)
                        entry = (size_gb, file, root)
                        file_list.append(entry)
                        current_files += 1
                        self.progress.emit(
                            int(current_files / self.total_files * 100))

        self.file_list_collected_signal.emit(file_list)

        # Save the converted file list
        with open(self.persistency_file, "wb") as f:
            pickle.dump(file_list, f)


class OtrCollector(QThread):
    progress = pyqtSignal(int)
    otrkey_list_collected_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def set_search_args(
        self,
        stations: List[str] = None,
        duration: str = None,
        formats: List[str] = None,
        airdate: str = None,
    ):
        self.stations = stations or ["ard"]
        self.duration = duration or 90
        self.formats = formats or ["mpg.HD.avi", "mpg.HQ.avi"]
        self.airdate = airdate or "2024-05-27"

    def run(self):
        otrkey_list = self.get_otrkey_list()
        self.otrkey_list_collected_signal.emit(otrkey_list)

    def get_otrkey_list(self):
        otrkey_list = []
        for s in self.stations:
            url = f"https://otrkeyfinder.com/de/?search=station%3A{s}+-HD.ac3+--mpg.avi+-mpg.mp4"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find_all('a', class_='download_link')
            for result in results:
                found_url = result['href']
                print(found_url)
                otrkey_list.append(found_url)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MOvies aNd SERies APp")
        screen = QApplication.primaryScreen()
        geometery = screen.availableGeometry()
        self.setGeometry(
            int(geometery.width() * 0.5),
            32,
            int(geometery.width() * 0.3),
            geometery.height() - 32,
        )
        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        splitter = QSplitter(Qt.Horizontal)

        # Left panel widget and layout
        left_widget = QWidget()
        left_widget_layout = QVBoxLayout(left_widget)
        splitter.addWidget(left_widget)

        # Right panel widget and layout
        right_widget = QWidget()
        right_widget_layout = QVBoxLayout(right_widget)
        splitter.addWidget(right_widget)

        # Left panel widgets
        button_local = QPushButton("Scan/Update local")
        button_local.clicked.connect(self.scan_local)
        self.local_dir_txtedit = QLineEdit()
        # self.local_dir_txtedit.setText("T:\\video\\;C:\\Downloads\\")
        self.local_dir_txtedit.setText("/home/sg82fe/Videos/Screencasts")

        self.local_model = QStandardItemModel(0, 3)
        self.local_model.setHorizontalHeaderLabels(["Gb", "File", "Path"])
        self.local_view = QTableView()
        self.local_view.setModel(self.local_model)
        self.local_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.local_view.verticalHeader().setDefaultSectionSize(16)
        self.local_view.setColumnWidth(0, 33)
        self.local_view.setColumnWidth(1, 190)
        self.local_view.setColumnWidth(2, 400)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("QProgressBar { height: 2px; }")
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # Adding widgets to the left panel layout
        left_widget_layout.addWidget(self.local_view)
        left_widget_layout.addWidget(self.local_dir_txtedit)
        left_widget_layout.addWidget(button_local)
        left_widget_layout.addWidget(self.progress_bar)

        # Right panel widgets
        button_otrkey = QPushButton("Scan/Update otrkey", parent=right_widget)
        button_otrkey.clicked.connect(self.scan_otrkey)
        self.otrkey_view = QListView(parent=right_widget)
        self.otrkey_model = QStringListModel()
        self.otrkey_view.setModel(self.otrkey_model)

        # Adding widgets to the right panel layout
        right_widget_layout.addWidget(button_otrkey)
        right_widget_layout.addWidget(self.otrkey_view)

        toolbar = QWidget()
        toolbar.setFixedHeight(32)
        toolbar_layout = QHBoxLayout(toolbar)
        self.local_search_txtedit = QLineEdit()
        self.local_search_txtedit.setText("")
        self.local_search_txtedit.textChanged.connect(self.filter_local_list)
        self.raw_toggle = QCheckBox("RAW")
        self.raw_toggle.setChecked(True)
        self.raw_toggle.clicked.connect(lambda: self.filter_local_list())

        toolbar_layout.addWidget(QLabel("Suchfilter: "))
        toolbar_layout.addWidget(self.local_search_txtedit)
        toolbar_layout.addWidget(self.raw_toggle)

        main_layout.addWidget(toolbar)
        main_layout.addWidget(splitter)

        # Hauptwidget
        self.setCentralWidget(main_widget)

        self.fc = FileCollector()
        self.all_local_movies = []
        if self.fc.file_list_cached:
            self.all_local_movies = self.fc.file_list_cached
            self.update_local_model(self.fc.file_list_cached)
        self.fc.file_list_collected_signal.connect(self.init_all_local_movies)
        self.fc.progress.connect(
            lambda value: self.progress_bar.setValue(value))

        self.oc = OtrCollector()
        self.oc.otrkey_list_collected_signal.connect(self.update_otrkeys)
        button_otrkey.clicked.connect(self.scan_otrkey)

    def scan_otrkey(self):
        self.oc.set_search_args()
        # self.oc.start()
        otrkey_list = self.oc.get_otrkey_list()
        self.update_otrkeys(otrkey_list)

    def update_otrkeys(self, otrkey_list):
        self.otrkey_model.setStringList(otrkey_list)

    def init_all_local_movies(self, file_list):
        self.all_local_movies = file_list
        self.update_local_model(self.all_local_movies)

    def update_local_model(self, file_list):
        self.local_model.setRowCount(0)
        for size_gb, file, root in file_list:
            item1 = QStandardItem(f"{size_gb:.1f}")
            item1.setTextAlignment(Qt.AlignCenter)
            f = file
            r = root
            if not self.raw_toggle.isChecked():
                if str(file).startswith(basename(root)):
                    f = basename(root)
                f = f.replace("_", " ")
                r = r.replace("[_incoming]\\", "")
                for directory in self.local_dir_txtedit.text().split(";"):
                    r = str(r).replace(directory, "")

            item2 = QStandardItem(f)
            item3 = QStandardItem(r)
            self.local_model.appendRow([item1, item2, item3])
        self.progress_bar.setValue(0)

    def scan_local(self):
        self.fc.set_dir(self.local_dir_txtedit.text())
        self.fc.start()

    def filter_local_list(self):
        search_term = self.local_search_txtedit.text().strip().lower()

        if not search_term:
            self.update_local_model(self.all_local_movies)
            return

        filtered_list = [
            (s, f, r) for s, f, r in self.all_local_movies if search_term in f.lower()
        ]
        self.update_local_model(filtered_list)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
