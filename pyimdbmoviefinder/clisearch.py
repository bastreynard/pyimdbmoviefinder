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
        
def showImdb(imdbResult):
    for i, movie in enumerate(imdbResult):
        s_link = "https://www.imdb.com/title/tt " + movie.id
        logger.info(str(i) + ": " + movie.title + s_link)
    # Ask user choice
    try:
        num = int(input("Enter choice: "))
    except ValueError:
        logger.error("Invalid user input")
        sys.exit(0)
    if 0 > num >= len(imdbResult):
        logger.error("Invalid user input")
        sys.exit(0)
    for i, movie in enumerate(imdbResult):
        if i == num:
            return movie
    return None

def showTorrent(torrentResult):
    for i, torrent in enumerate(torrentResult.torrents):
        s = str(i) + ": "
        s += torrent.title
        s += f" ({torrent.quality})"
        s += f" ({torrent.provider})"
        s += f' seeders :{torrent.seeds}'
        logger.info(s)
    # Ask user choice
    try:
        num = int(input("Enter choice: "))
    except ValueError:
        logger.error("Invalid user input")
        sys.exit(0)
    assert num >= 0 and num < len(torrentResult.torrents), "Invalid input"
    for i, torrent in enumerate(torrentResult.torrents):
        if i == num:
            return torrent
    return None

def cli():              
    logger.info('PyMovieFinder CLI\n')
    parser = argparse.ArgumentParser(description="PyTorrSearch CLI usage")
    parser.add_argument("-t","--title", help="Search movie by Title")
    parser.add_argument("-i","--id", help="Search movie by ID")
    parser.add_argument("-a","--all", help="Search torrents on YTS and using Jackett, otherwise only YTS is used", action="store_true")
    parser.add_argument("-n","--num", help="Maximum number of search results")
    parser.add_argument("--tv", help="Include TV shows in search")
    if len(sys.argv)==0:
        parser.print_help()
        parser.exit()
    args = vars(parser.parse_args())
    
    max_result = args["num"] if args["num"] else DEFAULT_MAX_RESULT
    search_all = args["all"]
    include_tv = args["tv"]
    
    # User Configuration 
    config = configparser.ConfigParser()
    config_path = str(pathlib.Path(__file__).parent) + "/config.ini"
    config.read(config_path)
    try:
        jackettHost = config.get("Jackett", "Host")
        jackettApiKey = config.get("Jackett", "ApiKey")
    except:
        jackettHost = jackettApiKey = None

    # 1. Search IMDb
    with Spinner():
        if args["title"]:
            imdbResult = ImdbSearcher().searchByTitle(args['title'], max_result, no_series = not include_tv)
        elif args["id"]:
            imdbResult = ImdbSearcher().searchById(args['id'])
        else:
            parser.print_help()
            parser.exit()

    if imdbResult is None:
        logger.warning("No IMDb results")
        sys.exit(0)
    else:
        choice = showImdb(imdbResult)

    torrent_errors = []
    # Search torrents
    with Spinner():
        searcher = TorrentSearcher()
        res, error = searcher.setSearch(choice.id, choice.title, yts=True, jackett=search_all,  jackettApiKey=jackettApiKey, jackettHost=jackettHost)
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
        choice = showTorrent(torrentResult)

    # RPC server configuration
    if config.has_section("RPC"):
        logger.info("Using config.ini for RPC configuration")
        rpc_host, rpc_user, rpc_password = \
            config.get('RPC','Host'), config.get('RPC','User'), config.get('RPC','Password')
    else:
        logger.warning("No config.ini found, enter RPC config manually:")
        logger.info(f"Or download the magnet directly: {choice.url}")
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
