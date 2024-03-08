from typing import List
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pyimdbmoviefinder.TorrentFetcher import TorrentFetcher, TorrentResult

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

    def fetch(self) -> List[TorrentResult]:
        api_url = self.url + self.movie_id
        response = self.requests_retry_session().get(api_url, timeout=120).json()
        #print(response)
        data = response.get('data')
        movies = data.get('movies')
        if movies is None:
            print("Torrents not found on YTS")
            return None
        for movie in movies:
            title_long = movie.get('title_long')
            print("Found torrents on YTS for :", title_long)
            torrents = movie.get('torrents')
            if torrents is None:
                print("no torrent for this movie")
                continue
            descs = []
            for torrent in torrents:
                #print(torrent)
                desc = TorrentResult(title_long, 
                                    torrent.get('quality'), 
                                    torrent.get('type'), 
                                    torrent.get('seeds'), 
                                    torrent.get('size'),
                                    "YTS", 
                                    torrent.get('url'))
                descs.append(desc)
        return descs
