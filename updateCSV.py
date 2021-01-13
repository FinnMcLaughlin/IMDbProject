from imdb import IMDb
import pandas as pd
import imdb.helpers
import urllib.request
from string import printable as pt
import csv
import os

curr_directory_path = os.getcwd()
last_updated_list_array = []

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

# Function to get the index of a movie in the imdb_movie_list based on it's title
def getIndexOfMovie_IMDbSearch(movie_title):
    index = 0

    for movie in all_imdb_movies:
        if movie_title in movie["title"]:
            return index

        index += 1

# Function to get the movie title from the original movie list based on a specified index
def getMovieTitleFromIndex(specified_index):
    curr_index = 0

    movie_list_ = open("../../Documents/Movie_List.txt", "r")
    print(specified_index)

    for movie in movie_list_:
        if specified_index == curr_index:
            movie_list_.close()
            return movie.replace("\n", "")

        curr_index += 1

# Function to get imdb movie data based on the given movie list
def getMovies(movies):
    imdb_movies = []

    index = 0

    for movie in movies:
        if not checkForUpdateInList(movie):
            print("\n-------\nFinding: " + movie)
            imdb_movie = _imdb.get_movie(
                    _imdb.search_movie(movie)[0].getID()
                )

            if set(imdb_movie["title"]).difference(pt):
                print("Title Reverted")
                imdb_movie["title"] = getMovieTitleFromIndex(index)

            if not checkPosterIsPresent(imdb_movie["title"]):
                if imdb_movie["title"][0].isdigit():
                    folder_path = "movie_posters\#\\" + imdb_movie["title"] + ".jpg"
                else:
                    folder_path = "movie_posters\\" + imdb_movie["title"][0].upper() + "\\" + imdb_movie["title"] + ".jpg"

                urllib.request.urlretrieve(imdb.helpers.fullSizeCoverURL(imdb_movie), folder_path)

            else:
                print(imdb_movie["title"] + " poster found")

            imdb_movies.append(imdb_movie)

            index += 1

    return imdb_movies

# Function to check if the value is present, if not replaces the value with standardised "N/A"
def checkValueIsPresent(movie, key):
    try:
        type(movie[key])

        if key == "title":
            if set(movie["title"]).difference(pt):
                return getMovieTitleFromIndex(getIndexOfMovie_IMDbSearch(movie["title"]))

    except:
        return "N/A"

    return movie[key]

# Function to check if poster has already been downloaded based on the given movie title
def checkPosterIsPresent(movie_title):
    poster_folder_path = os.path.join(curr_directory_path, "movie_posters", movie_title[0].upper())

    try:
        poster_ = open(os.path.join(poster_folder_path, movie_title + ".jpg"))
        poster_.close()
        return True

    except IOError:
        return False

# Function to check if a given movie title is present in the last updated list text file
# If so, it is removed from the array
def checkForUpdateInList(movie_title):
    if movie_title in last_updated_list_array:
        last_updated_list_array.remove(movie_title)
        return True

    else:
        return False

#def updateRemovedItems():
    #for

# Function to populate an array with the contents of the last updated movies text file
def populateLastUpdatedArray(last_updated_file):
    for column in last_updated_file:
        last_updated_list_array.append(column)

# Function to update the last updated movies text file to most recent version
def updateLastUpdatedMovieList(last_updated_list, most_recent_list):
    print("Last Updated List Array: ")
    for movie in last_updated_list_array:
        print(movie)
    print("-------------------------")
    #for line in most_recent_list:
    #    last_updated_list.write(line)

# Function to create a CSV file with the given imdb movie data
def createCSVfile(movies):
    with open("movie_info.csv", "a", newline="", encoding='utf-8') as file:
        headers = ["title", "year", "genre", "director", "cast", "countries", "rating", "languages"]

        writer = csv.DictWriter(file, headers)

        '''writer.writerow({"title": "title",
                                 "year": "year",
                                 "genre": "genre",
                                 "director": "director",
                                 "cast": "cast",
                                 "countries": "countries",
                                 "rating": "rating",
                                 "languages": "languages"})'''

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

movie_list = open("../../Documents/Movie_List.txt", "r")

last_updated_movie_list = open("last_updated_list.txt", "r")

populateLastUpdatedArray(last_updated_movie_list)

all_imdb_movies = getMovies(movie_list)

updateLastUpdatedMovieList(last_updated_movie_list, movie_list)

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
