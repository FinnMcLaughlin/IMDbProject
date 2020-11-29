from imdb import IMDb
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
        test = movie[key]

    except:
        return "N/A"

    return movie[key]


def createCSVfile(movies):
    with open("movie_info.csv", "w", newline="", encoding='utf-8') as file:
        headers = ["title", "year", "genre", "director", "cast", "countries", "rating", "languages"]

        writer = csv.DictWriter(file, headers)

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

                # TODO: movie["rating"] , movie["languages"]

            except:
                print("########\nERROR: " + movie["title"] + "\n########")


_imdb = IMDb()

movie_list = open("movie_list.txt", "r")

imdb_movies = getMovies(movie_list)
createCSVfile(imdb_movies)

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
