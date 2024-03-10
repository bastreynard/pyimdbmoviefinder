'''
Module used to search for IMDb objects matching a specific search.
Found results are then stored as MovieData objects for further processing.
'''
from typing import List
from dataclasses import dataclass
import logging
from imdb import Cinemagoer

logger = logging.getLogger('pyimdbmoviefinder')


@dataclass
class MovieData():
    '''Dataclass used to store all data related to a movie'''
    imdbId: str
    title: str
    year: str
    coverUrl: str
    rating: str
    summary: str = ""
    plot: str = ""
    trailerUrl: str = ""
    fullySearched: bool = False


class ImdbSearcher():
    '''
    Interacts with the IMDbPY API and maintain a list of MovieData for holding current search result
    The intended use is to :
    1) Make a title search which returns a fast result with movie titles but not much details
    2) Make a search by ID for a specific movie with detailed informations
    '''

    def __init__(self) -> None:
        '''Constructor'''
        self.imdbApi = Cinemagoer()
        self.moviesList: List[MovieData] = []

    def search_by_title(self, title, maxResult=10, includeTv=False):
        """Search Movie on IMDb by title

        Args:
            title (str): Title of wanted movie
            maxResult (int, optional): Max number of results. Defaults to 10.
            includeTv (bool, optional): If TV shows results should be included. Defaults to False.

        Returns:
            List: List of MovieData result
        """
        logger.info("Search movie by title: %s", title)
        logger.debug("Include TV : %s", includeTv)
        try:
            # TODO(fixme): search_movie_advanced() does not work anymore ?
            movieResult = self.imdbApi.search_movie(title, results=maxResult)
        except Exception: #pylint: disable=broad-exception-caught
            logger.warning("No results")
            return None
        if movieResult is None:
            logger.warning("No results")
            return None
        for mov in movieResult:
            coverUrl = None
            if 'full-size cover url' in mov.keys():
                coverUrl = mov['full-size cover url']
            if not includeTv and ('kind' in mov.keys()) \
                    and mov['kind'].lower() != "movie":
                logger.info("Skipped Serie %s", mov['title'])
                # Skip series
                continue
            year = self.find_movie_info(mov, 'year')
            rating = self.find_movie_info(mov, 'rating')
            mov = MovieData(
                mov.getID(), mov['long imdb title'], year, coverUrl, rating)
            self.moviesList.append(mov)
        return self.moviesList

    def search_by_id(self, imdbId):
        """Start searching for a movie by IMDb ID

        Args:
            imdbId (str): The  IMDb ID of the movie

        Returns:
            MovieData: A filled MovieData object containing result
        """
        logger.info("Search movie by ID: %s", imdbId)
        movieResult = self.imdbApi.get_movie(imdbId)
        mov = self.get_movie_from_id(imdbId)
        vids = self.find_movie_info(movieResult, 'videos')
        if vids:
            trailerUrl = "https://www.imdb.com/video/imdb/"+vids[0].rsplit('/', 1)[-1] \
                + "/imdb/embed?autoplay=false&width=720"
        if not mov:

            movieObj = MovieData(imdbId,
                                 self.find_movie_info(
                                     movieResult, 'long imdb title'),
                                 self.find_movie_info(movieResult, 'year'),
                                 self.find_movie_info(
                                     movieResult, 'full-size cover url'),
                                 self.find_movie_info(movieResult, 'rating'),
                                 movieResult.summary(),
                                 self.find_movie_info(
                                     movieResult, 'plot outline'),
                                 trailerUrl if vids else None,
                                 fullySearched=True)
            self.moviesList.append(movieObj)
            return movieObj

        mov.fullySearched = True
        mov.rating = self.find_movie_info(movieResult, 'rating')
        mov.year = self.find_movie_info(movieResult, 'year')
        mov.summary = movieResult.summary()
        mov.plot = self.find_movie_info(movieResult.data, 'plot outline')
        return mov

    def get_cover_url(self, imdbId):
        """Find the movie cover url in the movie object

        Args:
            imdbId (str): The  IMDb ID of the movie

        Returns:
            str: The URL of the Movie cover
        """
        # getting cover url of the series
        return self.imdbApi.get_movie(imdbId).data['full-size cover url']

    def get_summary(self, imdbId):
        """Get the summary of a IMDb object

        Args:
            imdbId (str): The  IMDb ID of the movie

        Returns:
            str: The summare of the IMDb object
        """
        return self.imdbApi.get_movie(imdbId).summary()

    def get_movie_from_title(self, title: str):
        """Returns the MovieData corresponding to the given title

        Args:
            title (str): Title of the movie

        Returns:
            MovieData: The corresponding MovieData if found
        """
        for mov in self.moviesList:
            if mov.title == title:
                return mov
        return None

    def get_movie_from_id(self, imdbId: str):
        """Returns the MovieData corresponding to the given ID

        Args:
            imdbId (str): IMDb ID of the movie

        Returns:
            MovieData: The corresponding MovieData if found
        """
        for mov in self.moviesList:
            if mov.imdbId == imdbId:
                return mov
        return None

    def find_movie_info(self, movie: MovieData, key: str):
        """Find movie info from the IMDb Movie object, if available

        Args:
            movie (str): The IMDb Movie object

        Returns:
            str: The requested info if available
        """
        if key in movie.keys():
            return movie[key]
        return None

    def clear(self):
        """Clear all found matching movies in this instance
        """
        logger.debug("Clear IMDb search results !")
        self.moviesList = []
