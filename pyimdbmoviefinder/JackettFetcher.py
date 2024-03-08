import operator
from typing import List

from requests import HTTPError
from pyimdbmoviefinder.TorrentFetcher import TorrentFetcher, TorrentResult
import humanize

import logging
import re

import xml.etree.ElementTree as ET

from pyimdbmoviefinder.http_utils import build_url, fetch_url

logger = logging.getLogger('torrentSearch')
DEFAULT_HOST = "http://localhost:9117"

class JackettFetcher(TorrentFetcher):
    """docstring for JackettFetcher"""
    def __init__(self, id, title, apiKey, host=DEFAULT_HOST, path="torznab/all", limit=25, ssl=False):
        self.movie_id = "tt"+id
        self.title = title
        if not host:
            host = DEFAULT_HOST
            
        print(f'Host {host}, API key {apiKey}')
        self.api = Jackett(apiKey, host, path, limit, ssl)
    
    def fetch(self) -> List[TorrentResult]:
        torrents = self.api.search(self.title)
        if not torrents:
            # Give up
            return None
        torrents_final = []
        for torrent in torrents:
            if 'chinese' in torrent.title.lower():
                # Lots of chinese ensubbed movies on rarbg...
                continue
            if torrent.seeds is not None and torrent.seeds == 0:
                print("No seeders, skipping...")
                continue
            print("Found torrent with seeders:", torrent.title)
            torrents_final.append(torrent)
        # Sort by seeders
        sorted_torrents = sorted(torrents_final, key= lambda e:e.seeds, reverse=True)
        return sorted_torrents

class Jackett(object):
    """docstring for Jackett"""
    def __init__(self, apikey, host, path, limit, ssl):
        super(Jackett, self).__init__()
        self.apikey = apikey
        self.host = host
        self.path = path
        self.page_limit = limit
        self.ssl = ssl

    def get_apikey(self):
        logger.debug('Using api key: {}'.format(self.apikey))
        return self.apikey

    def get_path(self):
        return self.path

    def get_page_limit(self):
        logger.debug('Current page limit: {} pages'.format(self.page_limit))
        return self.page_limit

    def search(self, query):
        """
        Starts the call to getting result from our indexer
        :param jackett.Jackett self: object instance
        :param str query: query we want to search for
        :return: list of results we found from scraping jackett output based on query
        :rtype: list
        """
        path = self.get_path().split('/')
        url_args = {
            'apikey': self.get_apikey(),
            'limit': self.get_page_limit(),
            'q': query
        }
        logger.debug('Url arguments for jackett search: {}'.format(url_args))

        url = build_url(self.ssl, self.host, path, url_args)
        url = url.replace('+', '%20')
        res = fetch_url(url)

        return self.parse_xml_for_torrents(res.read())


    def find_xml_attribute(self, xml_element, attr):
        """
        Finds a specific XML attribute given a element name
        :param jackett.Jackett self: object instance
        :param xml.etree.ElementTree.Element xml_element: the xml tree we want to search
        :param str attr: the attribute/element name we want to find in the xml tree
        :return: the value of the element fiven the attr/element name
        :rtype: str
        """
        value = xml_element.find(attr)
        if (value != None):
            logger.debug('Found attribute: {}'.format(attr))
            return value.text
        else:
            logger.warning('Could not find attribute: {}'.format(attr))
            return ''

    def parse_xml_for_torrents(self, raw_xml):
        """
        Finds a specific XML attribute given a element name
        :param jackett.Jackett self: object instance
        :param bytes raw_xml: the xml page returned by querying jackett
        :return: all the torrents we found in the xml page
        :rtype: list
        """
        tree = ET.fromstring(raw_xml)
        channel = tree.find('channel')
        results = []
        
        for child in channel.findall('item'):
            title = self.find_xml_attribute(child, 'title')
            date = self.find_xml_attribute(child, 'pubDate')
            magnet = self.find_xml_attribute(child, 'link')
            size = self.find_xml_attribute(child, 'size')
            indexer = self.find_xml_attribute(child, 'jackettindexer')
            foundUploader = re.findall('-1? *\w*', title)
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

            logger.debug('Found torrent with info: \n\ttitle: {}\n\tmagnet: {}\n\tsize: {}\n\tdate: {}\
            \n\tseeders: {}\n\tpeers: {}'.format(title, magnet, size, date, seeders, peers))
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