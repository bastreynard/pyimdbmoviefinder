import argparse
import configparser
import pathlib
import sys
from getpass import getpass
import threading
import time
from pyimdbmoviefinder import ImdbSearcher
from pyimdbmoviefinder import TorrentSearcher
from pyimdbmoviefinder import TorrentDownloader

DEFAULT_MAX_RESULT = 8

class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False
        
def showImdb(imdbResult):
    for i, movie in enumerate(imdbResult):
        s_link = "https://www.imdb.com/title/tt" + movie.id
        print(str(i) + ": " + movie.title + s_link)
    # Ask user choice
    try:
        num = int(input("Enter choice: "))
    except ValueError:
        print("Invalid input")
        sys.exit(0)
    assert num >= 0 and num < len(imdbResult), "Invalid input"
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
        print(s)
    # Ask user choice
    try:
        num = int(input("Enter choice: "))
    except ValueError:
        print("Invalid input")
        sys.exit(0)
    assert num >= 0 and num < len(torrentResult.torrents), "Invalid input"
    for i, torrent in enumerate(torrentResult.torrents):
        if i == num:
            return torrent
    return None

def cli():                
    print('PyTorrSearch CLI')
    parser = argparse.ArgumentParser(description="PyTorrSearch CLI usage")
    parser.add_argument("-t","--title", help="Search movie by Title")
    parser.add_argument("-i","--id", help="Search movie by ID")
    parser.add_argument("-a","--all", help="Search torrents on all providers, otherwise only YTS is used", action="store_true")
    parser.add_argument("-n","--num", help="Maximum number of search results")
    if len(sys.argv)==0:
        parser.print_help()
        parser.exit()
    args = vars(parser.parse_args())
    print(args)
    
    max_result = args["num"] if args["num"] else DEFAULT_MAX_RESULT
    all_providers = args["all"]
    
    # User Configuration 
    config = configparser.ConfigParser()
    config_path = str(pathlib.Path(__file__).parent.parent.parent) + "/config/config.ini"
    config.read(config_path)
    if config.has_section("Jackett"):
        jackettHost = config.get("Jackett", "Host")
        jackettApiKey = config.get("Jackett", "ApiKey")
        
    # 1. Search IMDb
    with Spinner():
        if args["title"]:
            imdbResult = ImdbSearcher().searchByTitle(args['title'], max_result, no_series = True)
        elif args["id"]:
            imdbResult = ImdbSearcher().searchById(args['id'])
        else:
            parser.print_help()
            parser.exit()

    if imdbResult is None:
        print("No IMDb results")
        sys.exit(0)
    else:
        choice = showImdb(imdbResult)

    # Search torrents
    with Spinner():
        searcher = TorrentSearcher()
        searcher.setSearch(choice.id, choice.title, yts=True, jackett=all_providers,  jackettApiKey=jackettApiKey, jackettHost=jackettHost)
        torrentResult = searcher.run()
    
    if torrentResult is None:
        print("No Torrents found")
        sys.exit(0)
    else:
        choice = showTorrent(torrentResult)

    # RPC server configuration
    if config.has_section("RPC"):
        print("Using config.ini for RPC configuration")
        rpc_host, rpc_user, rpc_password = \
            config.get('RPC','Host'), config.get('RPC','User'), config.get('RPC','Password')
    else:
        print("No config.ini found, enter RPC config manually:")
        rpc_host = input('RPC Address: ')
        rpc_user = input('Username: ')
        rpc_password = getpass()

    # Send to server
    dl = TorrentDownloader(rpc_host, rpc_user, rpc_password)
    print(dl.add_torrent_magnet(choice.url) + " to " + rpc_host)

if __name__ == '__main__':
    cli()
