from imdb import IMDb
from string import printable as pt
import csv

'''
TODO: Add method to append new additions to list to the CSV file, without
    the need to search each movie on the list again 

def formatTitle_List(movie_title):
    return movie_title.replace("\n", "").replace(" ", "").lower()


def formatTitle_CSV(movie_title):
    return movie_title.split(",")[0].replace(" ", "").lower()


def isMovieNew(movie, csv_file):
    for existing_movies in csv_file:

        if formatTitle_List(movie) in formatTitle_CSV(existing_movies):
            return True

    return False
'''


def getIndexOfMovie_IMDbSearch(movie_title):
    index = 0

    for movie in all_imdb_movies:
        if movie_title in movie["title"]:
            return index

        index += 1


def getMovieTitleFromIndex(specified_index):
    curr_index = 0

    movie_list_ = open("movie_list.txt", "r")
    print(specified_index)

    for movie in movie_list_:
        if specified_index == curr_index:
            movie_list_.close()
            return movie.replace("\n", "")

        curr_index += 1


def getMovies(movies):
    imdb_movies = []

    for movie in movies:
        print("Finding: " + movie)
        imdb_movies.append(
            _imdb.get_movie(
                _imdb.search_movie(movie)[0].getID()
            )
        )

    return imdb_movies


def checkValueIsPresent(movie, key):
    try:
        type(movie[key])

        if key == "title":
            if set(movie["title"]).difference(pt):
                return getMovieTitleFromIndex(getIndexOfMovie_IMDbSearch(movie["title"]))

    except:
        return "N/A"

    return movie[key]


def createCSVfile(movies):
    with open("movie_info.csv", "w", newline="", encoding='utf-8') as file:
        headers = ["title", "year", "genre", "director", "cast", "countries", "rating", "languages"]

        writer = csv.DictWriter(file, headers)

        writer.writerow({"title": "title",
                                 "year": "year",
                                 "genre": "genre",
                                 "director": "director",
                                 "cast": "cast",
                                 "countries": "countries",
                                 "rating": "rating",
                                 "languages": "languages"})

        for movie in movies:
            try:
                print(movie["title"])

                writer.writerow({"title": checkValueIsPresent(movie, "title"),
                                 "year": checkValueIsPresent(movie, "year"),
                                 "genre": checkValueIsPresent(movie, "genre")[:3],
                                 "director": checkValueIsPresent(movie, "director")[:2],
                                 "cast": checkValueIsPresent(movie, "cast")[:10],
                                 "countries": checkValueIsPresent(movie, "countries")[:3],
                                 "rating": checkValueIsPresent(movie, "rating"),
                                 "languages": checkValueIsPresent(movie, "languages")[:3]})

                # TODO: movie["duration"]

            except:
                print("########\nERROR: " + movie["title"] + "\n########")


_imdb = IMDb()

movie_list = open("movie_list.txt", "r")

all_imdb_movies = getMovies(movie_list)

movie_list.close()

createCSVfile(all_imdb_movies)

'''
title
year
cast []
director []
genres []
countries []
languages []
rating
'''
