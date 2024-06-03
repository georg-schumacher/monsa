import os
from os.path import basename, dirname
import pickle
from PyQt5.QtCore import QThread, pyqtSignal


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
        persistency_file="C:\\ws\\py\\jsoup\\local_file_list_cached.pkl",
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
                        size_gb = size_b  / (1024*1024*1024)
                        entry = (size_gb, file, root)
                        file_list.append(entry)
                        current_files += 1
                        self.progress.emit(int(current_files / self.total_files * 100))

        self.file_list_collected_signal.emit(file_list)

        # Save the converted file list
        with open(self.persistency_file, "wb") as f:
            pickle.dump(file_list, f)
