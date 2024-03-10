from typing import List
import requests
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pyimdbmoviefinder.TorrentFetcher import TorrentFetcher, TorrentResult

logger = logging.getLogger('pyimdbmoviefinder')
class YtsFetcher(TorrentFetcher):
    def __init__(self, id):
        self.url = "https://yts.mx/api/v2/list_movies.json?query_term="
        self.movie_id = "tt"+id
        
    def requests_retry_session(
            self,
            retries=3,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 504),
            session=None,
        ):
            session = session or requests.Session()
            retry = Retry(
                total=retries,
                read=retries,
                connect=retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_forcelist,
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            return session

    def fetch(self) -> tuple[bool, List[TorrentResult]]:
        api_url = self.url + self.movie_id
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
