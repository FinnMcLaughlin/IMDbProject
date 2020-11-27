from imdb import IMDb
import csv


def isMovieNew(movie, csv_file):
    for existing_movies in csv_file:
        print("|" + existing_movies.split(",")[0] + "| - |" + movie.replace("\n", "") + "|")
        if movie.replace("\n", "").lower() == existing_movies.split(",")[0].lower():
            print("Found: " + movie)
            return True

    return False


def getMovies(movies):
    imdb_movies = []

    csv_file = open("movie_info.csv", "r")

    for movie in movies:
        print("Finding: " + movie)
        if not isMovieNew(movie, csv_file):
            imdb_movies.append(
                _imdb.get_movie(
                    _imdb.search_movie(movie)[0].getID()
                )
            )

    # for movie in imdb_movies:
    #     print(movie["title"])
    #     print(movie["languages"][:2])
    #     print("\n")

    return imdb_movies


def createCSVfile(movies):
    with open("movie_info.csv", "a", newline="") as file:
        headers = ["title", "year", "genre", "director", "cast", "countries"]

        writer = csv.DictWriter(file, headers)

        for movie in movies:
            print(movie["title"])
            writer.writerow({"title": movie["title"], "year": movie["year"], "genre": movie["genre"][:3],
                             "director": movie["director"][:2], "cast": movie["cast"][:10],
                             "countries": movie["countries"][:3]})
            # TODO: movie["rating"] , movie["languages"]


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
