'''
Utility module for HTTP requests
'''
import logging

from urllib import parse, request
from urllib.error import URLError

logger = logging.getLogger('pyimdbmoviefinder')


def build_url(ssl, baseUrl:str, path:str, argsDict:dict) -> str:
    """
    Given the parameters joins them together to a url to
    :param bool ssl: if ssl is to be used or not
    :param str baseUrl: the start of the url (http://thepiratebay.org)
    :param list path: the rest of the path to the url (['search', 'lucifer', '0'])
    :param dict args_dict: a dict with the query element we want to append to the url
    :return: complete url based on the inputs
    :rtype: str
    """
    url_parts = list(parse.urlparse(baseUrl))
    url_parts[0] = 'https' if ssl else 'http'
    url_parts[2] = '/'.join(path)
    url_parts[4] = parse.urlencode(argsDict)
    return parse.urlunparse(url_parts)


def convert_query_to_percent_encoded_octets(inputQuery):
    """
    Converts a string with spaces to a string separated by '%20'
    :param str inputQuery:
    :return: string with spaces replaced with '%20' if found any
    :rtype: str
    """
    if isinstance(inputQuery, list):
        inputQuery = ' '.join(inputQuery)

    return parse.quote(inputQuery)


def fetch_url(url):
    """
    Call and get output for a given url
    :param str url: the url we want to make a request to
    :return: a response object with contents and status code of the request
    :rtype: http.client.HTTPResponse
    """
    logger.debug('Fetching query: %s', url)
    req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    try:
        with request.urlopen(req, timeout=60) as response:
            return True, response.read()
    except URLError as e:
        e = ('We failed to reach a server with request: %s\n', str(e))
        return False, e
