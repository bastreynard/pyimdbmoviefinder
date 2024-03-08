# This Python file uses the following encoding: utf-8
from typing import List
from imdb import Cinemagoer
from dataclasses import dataclass

@dataclass
class MovieData():
    '''Dataclass used to store all data related to a movie'''
    id: str
    title: str
    year: str
    cover_url: str
    rating: str
    summary: str = ""
    plot: str = ""
    trailer_url: str = ""
    fully_searched: bool = False

class ImdbSearcher():
    '''
    Interacts with the IMDbPY API and maintain a list of MovieData for holding current search result
    The intended use is to :
    1) Make a title search which returns a fast result with movie titles but not much details
    2) Make a search by ID for a specific movie with detailed informations
    '''
    def __init__(self) -> None:
        self.imdbApi = Cinemagoer()
        self.moviesList: List[MovieData] = []

    def searchByTitle(self, title, max_result = 10, no_series = False):
        print("Search movie by title: {}".format(title))
        print("Include TV : %d" % (not no_series))
        try:
            # TODO: search_movie_advanced() does not work anymore ?
            movieResult = self.imdbApi.search_movie(title, results=max_result)
        except Exception:
            print("No results")
            return None
        if movieResult is None:
            print("No results")
            return None
        else:
            for i in range(len(movieResult)):
                cover_url = None
                if 'full-size cover url' in movieResult[i].keys():
                    cover_url = movieResult[i]['full-size cover url']
                if no_series and ('kind' in movieResult[i].keys()) and movieResult[i]['kind'].lower() != "movie":
                    print("skipped %s serie" % movieResult[i]['title'])
                    # Skip series
                    continue
                id = movieResult[i].getID()
                year = self.findMovieInfo(movieResult[i], 'year')
                rating = self.findMovieInfo(movieResult[i], 'rating')
                mov = MovieData(id, movieResult[i]['long imdb title'], year, cover_url, rating)
                self.moviesList.append(mov)
        return self.moviesList
        
    def searchById(self, id):
        print("Search movie by ID: {}".format(id))
        movieResult = self.imdbApi.get_movie(id)
        mov = self.getMovieFromId(id)
        vids = self.findMovieInfo(movieResult, 'videos')
        if vids:
            trailer_url = "https://www.imdb.com/video/imdb/"+vids[0].rsplit('/', 1)[-1]+ "/imdb/embed?autoplay=false&width=720"
        if not mov:
            
            movieObj = MovieData(id, 
                    self.findMovieInfo(movieResult, 'long imdb title'), 
                    self.findMovieInfo(movieResult, 'year'), 
                    self.findMovieInfo(movieResult, 'full-size cover url'), 
                    self.findMovieInfo(movieResult, 'rating'), 
                    movieResult.summary(),
                    self.findMovieInfo(movieResult, 'plot outline'),
                    trailer_url if vids else None,
                    fully_searched=True)
            self.moviesList.append(movieObj)
            return movieObj
        else:
            mov.fully_searched = True
            mov.rating = self.findMovieInfo(movieResult, 'rating')
            mov.year = self.findMovieInfo(movieResult, 'year')
            mov.summary = movieResult.summary()
            mov.plot = self.findMovieInfo(movieResult.data, 'plot outline')
            return mov

    def getCoverUrl(self, id):
        # getting cover url of the series
        return self.imdbApi.get_movie(id).data['full-size cover url']

    def getSummary(self, id):
        return self.imdbApi.get_movie(id).summary()

    def getMovieFromTitle(self, title:str):
        '''
        Find a movie in the local movieResult object
        '''
        for mov in self.moviesList:
            if mov.title == title:
                return mov
        return None

    def getMovieFromId(self, id:str):
        '''
        Find a movie in the local movieResult object
        '''
        for mov in self.moviesList:
            if mov.id == id:
                return mov
        return None

    def findMovieInfo(self, movieResult, key:str):
        '''
        Find movie info from the Movie object, if available
        '''
        if key in movieResult.keys():
            return movieResult[key]
        return None
    
    def clear(self):
        print("Clear IMDb search results !")
        self.moviesList = []
