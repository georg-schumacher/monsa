# https://otrkeyfinder.com/de/?search=ard+HD

import os
from os.path import basename, dirname
from typing import List
import pickle
from PyQt5.QtCore import QThread, pyqtSignal

import requests
from bs4 import BeautifulSoup


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
        otrkey_list = []
        current_otrkeys = 0
        for s in self.stations:
            url = f"https://otrkeyfinder.com/de/?search=station%3A{s}+-HD.ac3+--mpg.avi+-mpg.mp4"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find_all('a', class_='download_link')
            for result in results:
                found_url = result['href']
                print(found_url)
                otrkey_list.append(found_url)

        self.otrkey_list_collected_signal.emit(otrkey_list)
