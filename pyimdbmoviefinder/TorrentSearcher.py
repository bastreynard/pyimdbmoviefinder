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
            if not jackettApiKey or not jackettHost:
                return False, str("Set a valid API key/Host to use jackett indexers")
            self.fetchers.append(JackettFetcher(id, title, jackettApiKey, jackettHost))
        return True, ""

    def run(self):
        result = []
        errors = []
        for fetcher in self.fetchers:
            res, output = fetcher.fetch()
            if res and output is not None:
                result += output
            elif not res:
                # Something went wrong with this fetcher
                errors += output
        newTorrents = TorrentData(self.id, result)
        existing = self.getTorrentsDataFromId(self.id)
        if existing:
            existing.torrents = result
        else:
            self.torrentsList.append(newTorrents)
        self.fetchers = []
        return newTorrents, errors

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
