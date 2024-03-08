# This Python file uses the following encoding: utf-8
from typing import List

from pyimdbmoviefinder.YtsFetcher import YtsFetcher
from pyimdbmoviefinder.JackettFetcher import JackettFetcher
from pyimdbmoviefinder.TorrentFetcher import TorrentResult
from dataclasses import dataclass

@dataclass
class TorrentData():
    id: str
    torrents : List[TorrentResult]

class TorrentSearcher:
    def __init__(self):
        self.fetchers = []
        self.torrentsList: List[TorrentData] = []

    def setSearch(self, id:str, title:str, yts:bool=True, jackett:bool=True, jackettApiKey:str=None, jackettHost:str=None):
        self.id = id
        if yts:
            self.fetchers.append(YtsFetcher(id))
        if jackett:
            assert jackettApiKey, "Set a valid API key to use jackett indexers"
            self.fetchers.append(JackettFetcher(id, title, jackettApiKey, jackettHost))

    def run(self):
        result = []
        for fetcher in self.fetchers:
            tr = fetcher.fetch()
            if tr is not None:
                result += tr
        newTorrents = TorrentData(self.id, result)
        existing = self.getTorrentsDataFromId(self.id)
        if existing:
            existing.torrents = result
        else:
            self.torrentsList.append(newTorrents)
        self.fetchers = []
        return newTorrents

    def getTorrentsDataFromId(self, id):
        for data in self.torrentsList:
            if data.id == id:
                return data
        return None
    
    def getTorrentsFromId(self, id):
        for data in self.torrentsList:
            if data.id == id:
                return data.torrents
        return None
    
    def clear(self):
        self.torrentsList = []
