'''
Command Line Interface for searching for torrents
'''
import argparse
import configparser
import pathlib
import logging
import sys
from getpass import getpass
from pyimdbmoviefinder.ImdbSearcher import ImdbSearcher
from pyimdbmoviefinder.TorrentSearcher import TorrentSearcher
from pyimdbmoviefinder.TorrentDownloader import TorrentDownloader
from pyimdbmoviefinder.utils import Spinner

DEFAULT_MAX_RESULT = 8
logger = logging.getLogger('pyimdbmoviefinder')


def show_imdb(imdbResult):
    """Show result from IMDb search

    Args:
        imdbResult (List): List of IMDb results

    Returns:
        int: User choice
    """
    for i, movie in enumerate(imdbResult):
        s_link = "https://www.imdb.com/title/tt " + movie.imdbId
        logger.info(str(i) + ": " + movie.title + s_link)
    # Ask user choice
    invalid = True
    while invalid:
        try:
            num = int(input("Enter choice: "))
        except ValueError:
            invalid=True
            logger.error("Invalid user input")
        if num >=len(imdbResult) or num < 0:
            invalid=True
            logger.error("Invalid user input !")
        else:
            invalid=False

    for i, movie in enumerate(imdbResult):
        if i == num:
            return movie
    return None


def show_torrent(torrentResult):
    """Show result from torrent search

    Args:
        imdbResult (List): List of torrent results

    Returns:
        int: User choice
    """
    for i, torrent in enumerate(torrentResult.torrents):
        s = str(i) + ": "
        s += torrent.name
        s += f" ({torrent.quality})"
        s += f" ({torrent.provider})"
        s += f' seeders :{torrent.seeds}'
        logger.info(s)
    # Ask user choice
    invalid = True
    while invalid:
        try:
            num = int(input("Enter choice: "))
        except ValueError:
            invalid=True
            logger.error("Invalid user input")
        if num >=len(torrentResult.torrents) or num < 0:
            invalid=True
            logger.error("Invalid user input !")
        else:
            invalid=False

    for i, torrent in enumerate(torrentResult.torrents):
        if i == num:
            return torrent
    return None


def cli():
    """
    CLI entry
    """
    #pylint: disable=too-many-branches, too-many-statements
    logger.info('PyMovieFinder CLI\n')
    parser = argparse.ArgumentParser(description="PyTorrSearch CLI usage")
    parser.add_argument("-t", "--title", help="Search movie by Title")
    parser.add_argument("-i", "--id", help="Search movie by ID")
    parser.add_argument(
        "-a", "--all", help="Search torrents on YTS and using Jackett, otherwise only YTS is used",
        action="store_true")
    parser.add_argument("-n", "--num", help="Maximum number of search results")
    parser.add_argument("--tv", help="Include TV shows in search", action="store_true")
    if len(sys.argv) == 0:
        parser.print_help()
        parser.exit()
    args = vars(parser.parse_args())

    maxResult = args["num"] if args["num"] else DEFAULT_MAX_RESULT
    searchAll = args["all"]
    includeTv = args["tv"]

    # User Configuration
    config = configparser.ConfigParser()
    config_path = str(pathlib.Path(__file__).parent) + "/config.ini"
    config.read(config_path)
    jackettHost = config.get("Jackett", "Host")
    jackettApiKey = config.get("Jackett", "ApiKey")

    # 1. Search IMDb
    with Spinner():
        if args["title"]:
            imdbResult = ImdbSearcher().search_by_title(
                args['title'], maxResult, includeTv=includeTv)
        elif args["id"]:
            imdbResult = ImdbSearcher().search_by_title(args['id'])
        else:
            parser.print_help()
            parser.exit()

    if imdbResult is None:
        logger.warning("No IMDb results")
        sys.exit(0)
    else:
        choice = show_imdb(imdbResult)

    torrent_errors = []
    # Search torrents
    with Spinner():
        searcher = TorrentSearcher()
        res, error = searcher.set_search(choice.imdbId, choice.title, yts=True,
                                        jackett=searchAll,  jackettApiKey=jackettApiKey,
                                        jackettHost=jackettHost)
        if not res:
            torrent_errors.append(error)
        torrentResult, errors = searcher.run()

    if errors:
        torrent_errors.append(errors)
    if torrent_errors:
        for err in torrent_errors:
            logger.error(err)
    if torrentResult is None:
        logger.warning("No Torrents found")
        sys.exit(0)
    else:
        choice = show_torrent(torrentResult)

    # RPC server configuration
    if config.has_section("RPC"):
        logger.info("Using config.ini for RPC configuration")
        rpc_host, rpc_user, rpc_password = \
            config.get('RPC', 'Host'), config.get(
                'RPC', 'User'), config.get('RPC', 'Password')
    else:
        logger.warning("No config.ini found, enter RPC config manually:")
        logger.info("Or download the magnet directly: %s", choice.url)
        rpc_host = input('RPC Address: ')
        rpc_user = input('Username: ')
        rpc_password = getpass()

    # Send to server
    dl = TorrentDownloader(rpc_host, rpc_user, rpc_password)
    result, info = dl.add_torrent_magnet(choice.url)
    if result:
        logger.info(info)
    else:
        logger.error(info)


if __name__ == '__main__':
    cli()
