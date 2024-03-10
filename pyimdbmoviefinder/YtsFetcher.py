'''
Module used to search for torrent on YTS.
Results are then stored in TorrentResult object for further processing
'''
from typing import List
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from pyimdbmoviefinder.TorrentFetcher import TorrentFetcher, TorrentResult

logger = logging.getLogger('pyimdbmoviefinder')


class YtsFetcher(TorrentFetcher):
    """
    Class for scraping YTS torrents
    """
    def __init__(self, imdbId):
        """Constructor
        Args:
            imdbId (str): The IMDb ID of the Movie/TV
        """
        self.url = "https://yts.mx/api/v2/list_movies.json?query_term="
        self.movieId = "tt"+imdbId
        
    def requests_retry_session(
        self,
        retries=3,
        backoffFactor=0.3,
        statusForcelist=(500, 502, 504),
        session=None,
    ):
        """Wrapper for HTTP retry

        Args:
            retries (int, optional): number of retries. Defaults to 3.
            backoffFactor (float, optional): Back Off factor. Defaults to 0.3.
            statusForcelist (tuple, optional): Force retry code list. Defaults to (500, 502, 504).
            session (_type_, optional): Request session if any. Defaults to None.

        Returns:
            Session: The session
        """
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoffFactor,
            status_forcelist=statusForcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def fetch(self) -> tuple[bool, List[TorrentResult]]:
        """Run the fetcher with provided arguments

        Returns:
            tuple[bool, List[TorrentResult]]: List of torrents found
        """
        api_url = self.url + self.movieId
        response = self.requests_retry_session().get(api_url, timeout=120).json()
        logger.debug(response)
        data = response.get('data')
        movies = data.get('movies')
        if movies is None:
            return False, "Torrents not found on YTS"
        for movie in movies:
            title_long = movie.get('title_long')
            logger.info("Found torrents on YTS for : %s", title_long)
            torrents = movie.get('torrents')
            if torrents is None:
                logger.info("no torrent for this movie")
                continue
            descs = []
            for torrent in torrents:
                logger.debug(torrent)
                desc = TorrentResult(title_long,
                                     torrent.get('quality'),
                                     torrent.get('type'),
                                     torrent.get('seeds'),
                                     torrent.get('size'),
                                     "YTS",
                                     torrent.get('url'))
                descs.append(desc)
        return True, descs
