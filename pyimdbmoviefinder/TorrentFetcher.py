# This Python file uses the following encoding: utf-8
from abc import abstractmethod
from dataclasses import dataclass
from typing import List

RELEASE_TYPES = ('bdremux', 'brremux', 'remux',
	'bdrip', 'brrip', 'blu-ray', 'bluray', 'bdmv', 'bdr', 'bd5',
	'web-cap', 'webcap', 'web cap',
	'webrip', 'web rip', 'web-rip', 'web',
	'webdl', 'web dl', 'web-dl', 'hdrip',
	'dsr', 'dsrip', 'satrip', 'dthrip', 'dvbrip', 'hdtv', 'pdtv', 'tvrip', 'hdtvrip',
	'dvdr', 'dvd-full', 'full-rip', 'iso',
	'hdts', 'hdts', 'telesync', 'pdvd', 'predvdrip',
	'camrip', 'cam', '720p', '1080p', '2160p')

@dataclass
class TorrentResult():
    title: str
    quality: str
    type: str
    seeds : int
    size : str
    provider : str
    url : str
    description : str = ""

    def __post_init__(self):
        self.description = self.title + " " + str(self.find_release_type())
        
    def find_release_type(self):
        name = self.title.casefold()
        return [r_type for r_type in RELEASE_TYPES if r_type in name]

class TorrentFetcher:
    def __init__(self):
        pass

    @abstractmethod
    def fetch(self) -> List[TorrentResult]:
        pass

