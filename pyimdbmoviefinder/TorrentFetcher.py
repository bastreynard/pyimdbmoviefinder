'''
Base class for Torrent Fetcher classes
'''
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
    """Datalass for holding Torrent result data
    """
    name: str
    quality: str
    type: str
    seeds: int
    size: str
    provider: str
    url: str
    description: str = ""

    def __post_init__(self):
        '''Constructor'''
        self.description = self.name + " " + str(self.find_release_type())

    def find_release_type(self):
        """Find the release type embedded in the title attribute

        Returns:
            str: The release type found
        """
        name = self.name.casefold()
        release_type = [r_type for r_type in RELEASE_TYPES if r_type in name]
        if len(release_type) == 0:
            return self.quality
        return release_type

class TorrentFetcher:
    """Abstract Class for Torrent Fetcher classes
    """
    def __init__(self):
        '''Constructor'''

    @abstractmethod
    def fetch(self) -> tuple[bool, List[TorrentResult]]:
        '''Run fetcher
        return:
            bool: returns True if the fetcher encountered no issues
            List: List of torrents found using the fetcher'''
