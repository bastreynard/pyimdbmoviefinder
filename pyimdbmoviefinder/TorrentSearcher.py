'''
Module used by upper layer to start a torrent search using all available fetchers
'''
from typing import List
from dataclasses import dataclass
from pyimdbmoviefinder.YtsFetcher import YtsFetcher
from pyimdbmoviefinder.JackettFetcher import JackettFetcher
from pyimdbmoviefinder.TorrentFetcher import TorrentResult


@dataclass
class TorrentData():
    """Dataclass for holding torrent data with the corresponding ID.
    """
    imdbId: str
    torrents: List[TorrentResult]


class TorrentSearcher:
    """Class for searching torrents matching the provided IMDb ID
    """
    def __init__(self):
        """Constructor
        """
        self.fetchers = []
        self.torrentsList: List[TorrentData] = []
        self.imdbId = None

    def set_search(self, imdbId: str, title: str, yts: bool = True, jackett: bool = True,
                  jackettApiKey: str = None, jackettHost: str = None):
        #pylint: disable=too-many-arguments
        """Prepare a torrent search

        Args:
            imdbId (str): IMDb ID
            title (str): Movie/TV title
            yts (bool, optional): True for searching YTS. Defaults to True.
            jackett (bool, optional): True for searching using Jackett. Defaults to True.
            jackettApiKey (str, optional): Jackett API key. Defaults to None.
            jackettHost (str, optional): Jackett Host. Defaults to None.

        Returns:
            _type_: True if all fetchers are ready, False otherwise
        """
        self.imdbId = imdbId
        if yts:
            self.fetchers.append(YtsFetcher(imdbId))
        if jackett:
            if not jackettApiKey or not jackettHost:
                return False, str("Set a valid API key/Host to use jackett indexers")
            self.fetchers.append(JackettFetcher(
                imdbId, title, jackettApiKey, jackettHost))
        return True, ""

    def run(self):
        """Run the torrent search

        Returns:
            List: List of found torrent for the search specified in set_search
        """
        result = []
        errors = []
        for fetcher in self.fetchers:
            res, output = fetcher.fetch()
            if res and output is not None:
                result += output
            elif not res:
                # Something went wrong with this fetcher
                errors += output
        newTorrents = TorrentData(self.imdbId, result)
        existing = self.get_torrents_data_from_id(self.imdbId)
        if existing:
            existing.torrents = result
        else:
            self.torrentsList.append(newTorrents)
        self.fetchers = []
        return newTorrents, errors

    def get_torrents_data_from_id(self, imdbId):
        """Find all found torrents data from an IMDb ID

        Args:
            imdbId (str): IMDb ID

        Returns:
            TorrentData | None: the TorrentData object if found, None otherwise
        """
        for data in self.torrentsList:
            if data.imdbId == imdbId:
                return data
        return None

    def get_torrents_from_id(self, imdbId):
        """Find all found torrents from an IMDb ID

        Args:
            imdbId (str): IMDb ID

        Returns:
            TorrentResult | None: the TorrentResult object if found, None otherwise
        """
        for data in self.torrentsList:
            if data.imdbId == imdbId:
                return data.torrents
        return None

    def clear(self):
        """Clear all torrent data from the list
        """
        self.torrentsList = []
