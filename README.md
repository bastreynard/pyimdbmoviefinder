# PyImdbMovieFinder

Package for searching torrents that match an IMDb search.
The torrent found can be sent to a torrent downloader such as a [transmission](https://github.com/transmission/transmission) daemon running on a remote server using RPC protocol.

The Jackett part is heavily inspired by https://github.com/KevinMidboe/torrent_search

Some exemple apps are available [here](https://github.com/bastreynard/pymf-apps).

### Prerequisite 

- `pip install pyimdbmoviefinder`

#### CLI

`pyimdbmoviefinder [OPTIONS]`

```bash
pyimdbmoviefinder CLI
usage: pyimdbmoviefinder [-h] [-t TITLE] [-i ID] [-a] [-n NUM] [--tv]

pyimdbmoviefinder CLI usage

options:
  -h, --help              show this help message and exit
  -t TITLE, --title TITLE Search movie by Title
  -i ID, --id ID          Search movie by IMDb ID
  -a, --all               Search torrents on all providers, otherwise only YTS is used
  -n NUM, --num NUM       Maximum number of search results
  --tv                    Include TV shows results
```

A `config.ini` file can be used to pass the RPC server settings to the CLI (see `config/config.ini.sample`).

## Dependencies

This app makes use of these projects:
* [IMDbPY](https://github.com/MaximShidlovski23/imdbpy)
* [torrent_search](https://github.com/KevinMidboe/torrent_search)
