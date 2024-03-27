'''
Module used to search for torrents using a Jackett server.
Results are then stored in TorrentResult object for further processing
'''

from typing import List
import logging
import re
import xml.etree.ElementTree as ET
import humanize
from pyimdbmoviefinder.http_utils import build_url, fetch_url
from pyimdbmoviefinder.TorrentFetcher import TorrentFetcher, TorrentResult

logger = logging.getLogger('pyimdbmoviefinder')
DEFAULT_HOST = "http://localhost:9117"


class JackettFetcher(TorrentFetcher):
    """docstring for JackettFetcher"""

    def __init__(self, imdbId, title, apiKey, host=DEFAULT_HOST, path="torznab/all", \
        limit=25, ssl=False): #pylint: disable=too-many-arguments
        '''Constructor'''
        self.movieId = "tt"+imdbId
        self.title = title
        if not host:
            host = DEFAULT_HOST

        logger.info('Host %s, API key %s', host, apiKey)
        self.api = Jackett(apiKey, host, path, limit, ssl)

    def fetch(self) -> tuple[bool, List[TorrentResult]]:
        """Run the fetcher with provided arguments

        Returns:
            tuple[bool, List[TorrentResult]]: List of torrents found
        """
        success, output = self.api.search(self.title)
        if success and not output:
            # Give up
            return None, output
        if not success:
            return success, output
        torrents_final = []
        for torrent in output:
            #pylint: disable=no-member
            if torrent.seeds is not None and torrent.seeds == 0:
                logger.debug("No seeders, skipping...")
                continue
            logger.debug("Found torrent with seeders: %s", torrent.name)
            torrents_final.append(torrent)
        # Sort by seeders
        sorted_torrents = sorted(
            torrents_final, key=lambda e: e.seeds, reverse=True)
        return True, sorted_torrents


class Jackett():
    """docstring for Jackett"""

    def __init__(self, apikey, host, path, limit, ssl): #pylint: disable=too-many-arguments
        super().__init__()
        self.apikey = apikey
        self.host = host
        self.path = path
        self.pageLimit = limit
        self.ssl = ssl

    def get_apikey(self):
        """Get the configured Jackett API Key

        Returns:
            str: The API Key
        """
        logger.debug('Using api key: %s', self.apikey)
        return self.apikey

    def get_path(self):
        """Get the configured torznab path

        Returns:
            str: the torznab path
        """
        return self.path

    def get_page_limit(self):
        """Get the configured page limit

        Returns:
            str: The page limit
        """
        logger.debug('Current page limit: %s pages', self.pageLimit)
        return self.pageLimit

    def search(self, query) -> tuple[bool, List[TorrentResult]]:
        """
        Starts the call to getting result from our indexer
        :param str query: query we want to search for
        :return: list of results we found from scraping jackett output based on query
        :rtype: bool, list
        """
        path = self.get_path().split('/')
        url_args = {
            'apikey': self.get_apikey(),
            'limit': self.get_page_limit(),
            'q': query
        }
        logger.debug('Url arguments for jackett search: %s',url_args)

        url = build_url(self.ssl, self.host, path, url_args)
        url = url.replace('+', '%20')
        res, output = fetch_url(url)
        if res:
            return True, self.parse_xml_for_torrents(output)
        return False, output

    def find_xml_attribute(self, xmlElement, attr):
        """
        Finds a specific XML attribute given a element name
        :param jackett.Jackett self: object instance
        :param xml.etree.ElementTree.Element xmlElement: the xml tree we want to search
        :param str attr: the attribute/element name we want to find in the xml tree
        :return: the value of the element fiven the attr/element name
        :rtype: str
        """
        value = xmlElement.find(attr)
        if value is not None:
            logger.debug('Found attribute: %s', attr)
            return value.text
        logger.warning('Could not find attribute: %s', attr)
        return ''

    def parse_xml_for_torrents(self, rawXml):
        """
        Finds a specific XML attribute given a element name
        :param jackett.Jackett self: object instance
        :param bytes rawXml: the xml page returned by querying jackett
        :return: all the torrents we found in the xml page
        :rtype: list
        """
        tree = ET.fromstring(rawXml)
        channel = tree.find('channel')
        results = []

        for child in channel.findall('item'):
            title = self.find_xml_attribute(child, 'title')
            date = self.find_xml_attribute(child, 'pubDate')
            magnet = self.find_xml_attribute(child, 'link')
            size = self.find_xml_attribute(child, 'size')
            indexer = self.find_xml_attribute(child, 'jackettindexer')
            foundUploader = re.findall(r'-1? *\w*', title)
            if len(foundUploader) > 0:
                uploader = str(foundUploader[-1][1:])
            else:
                uploader = ''
            seeders = 0
            peers = 0

            for elm in child.findall('{http://torznab.com/schemas/2015/feed}attr'):
                if elm.get('name') == 'seeders':
                    seeders = elm.get('value')
                if elm.get('name') == 'peers':
                    peers = elm.get('value')
                try:
                    size = int(size)
                    size = humanize.naturalsize(size)
                except ValueError:
                    pass

            logger.debug('Found torrent with info: \n\ttitle: %s\n\tmagnet: %s\n\tsize: \
                %s\n\tdate: %s \n\tseeders: %s\n\tpeers: %s', \
                    title, magnet, size, date, seeders, peers)
            torrent = TorrentResult(title,
                                    '?',
                                    '?',
                                    seeders,
                                    size,
                                    f'{indexer} - {uploader}',
                                    magnet)
            torrent.quality = torrent.find_release_type()
            # Let's just skip cam torrent...
            if 'cam' in torrent.quality:
                continue
            results.append(torrent)

        return results
