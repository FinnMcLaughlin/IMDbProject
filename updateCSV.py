from imdb import IMDb
import pandas as pd
import imdb.helpers
import urllib.request
from string import printable as pt
import csv
import os

curr_directory_path = os.getcwd()
last_updated_list_array = []

CSV_file = "movie_info.csv"
movie_list_file = "resources/Movie_List.txt"
#CSV_file = "temp_movie_info.csv"
#movie_list_file = "temp_movie_list.txt"

last_updated_list_file = "resources/last_updated_list.txt"

def checkForUpdateInList(movie_title):
    """
    Function to check if a given movie title is present in the last updated list text file, and if so then it is removed
    from the array. This is to remove any movies that had previously been on the original movie list that are no longer
    present.

    :param movie_title: the movie title that is being checked
    :return: a boolean value denoting whether the movie title is present or not
    """
    if movie_title in last_updated_list_array:
        last_updated_list_array.remove(movie_title)
        return True

    else:
        return False

def getMovieTitleFromIndex(specified_index):
    """
    Function to get the movie title from the orginial movie list based on a given index

    :param specified_index: the index of the requested movie
    :return: the movie title based on the given index
    """
    curr_index = 0

    movie_list_ = open(movie_list_file, "r")

    for movie in movie_list_:
        if specified_index == curr_index:
            movie_list_.close()
            return movie.replace("\n", "")

        curr_index += 1

def getIndexOfMovie_IMDbSearch(movie_title):
    """
    Function to get the index of a movie in the imdb_movie_list based on it's title

    :param movie_title: the movie title who's index is needed
    :return: the index of the given movie title
    """
    index = 0

    for movie in all_imdb_movies:
        if movie_title in movie["title"]:
            return index

        index += 1

def checkPosterIsPresent(movie_title):
    """
    Function to check if the poster of a given movie has already been downloaded and stored in the movie posters folder

    :param movie_title: the title of the movie that is being checked
    :return: a boolean value denoting whether the poster is present in the movie posters folder
    """
    poster_folder_path = os.path.join(curr_directory_path, "movie_posters", movie_title[0].upper())

    try:
        poster_ = open(os.path.join(poster_folder_path, movie_title + ".jpg"))
        poster_.close()
        return True

    except IOError:
        return False

def cleanValues(movie, key):
    """
    Function to clean up the data to make it more uniform, allowing for easier parsing in the future.
    The function will:
        - Replace any missing values with "N/A"
        - Update movie titles pulled from imdb that contain special characters to the original title in the .txt file
        - Simplify the lists of directors & cast to contain just their names

    :param movie: the imdb information of a movie
    :param key: the column that is being checked
    :return: the data that will be stored in the csv file column
    """
    try:
        type(movie[key])

        if key == "title":
            if set(movie["title"]).difference(pt):
                return getMovieTitleFromIndex(getIndexOfMovie_IMDbSearch(movie["title"]))

        elif key == "director" or key == "cast":
            formatted_names = []

            for names in movie[key]:
                formatted_names.append(names["long imdb name"])

            return formatted_names

    except:
        return "N/A"

    return movie[key]


def populateLastUpdatedArray(last_updated_file):
    """
    Function to populate an array with the contents of the last updated movies text file

    :param last_updated_file: the last updated movies text file
    """
    for column in last_updated_file:
        last_updated_list_array.append(column)

def getMovies(movies):
    """
    Function to get the imdb movie data based on the given movie list. The function goes through each movie in the movie
    list and performs the following steps:
    - Checks to see if the movie information has already been web-scraped and stored
    - If it hasn't already been stored, the web-scraped movie title is checked for special characters that might cause an
    issue when stored in the csv file, and if so, replaces the movie title with the title in the original movie list
    - Checks to see if the poster for the movie is present in the movie posters folder, and if not retrieves the poster
    from imdb
    - Then adds the movie to the imdb movie list

    :param movies: the original list of movies
    :return: the list of imdb information for the movies
    """
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

def appendToCSVfile(movies):
    """
    Function to create and populate a csv file with the given imdb movie data

    :param movies: the imdb movie data frame
    """
    with open(CSV_file, "a", newline="", encoding='utf-8') as file:
        headers = ["title", "year", "genre", "director", "cast", "countries", "rating", "languages"]

        writer = csv.DictWriter(file, headers)
        #writer.writeheader()
        for movie in movies:
            try:
                print("Appending " + movie["title"])

                writer.writerow({"title": cleanValues(movie, "title"),
                                 "year": cleanValues(movie, "year"),
                                 "genre": cleanValues(movie, "genre")[:3],
                                 "director": cleanValues(movie, "director")[:2],
                                 "cast": cleanValues(movie, "cast")[:10],
                                 "countries": cleanValues(movie, "countries")[:3],
                                 "rating": cleanValues(movie, "rating"),
                                 "languages": cleanValues(movie, "languages")[:3]})

                # TODO: movie["duration"]

            except:
                print("########\nERROR: " + movie["title"] + "\n########")

def removeFromCSVfile():
    """
    Function to remove any movie from the csv file that is no longer present in the movie text file

    """
    tempCSV = pd.read_csv(CSV_file)

    with open(CSV_file, "w", newline="", encoding='utf-8') as file:
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

        for index in tempCSV.index:
            title = str(tempCSV["title"][index]) +"\n"
            title_year = str(tempCSV["title"][index]) + " (" + str(tempCSV["year"][index]) + ")\n"

            if not title in last_updated_list_array and not title_year in last_updated_list_array:
                writer.writerow({"title": tempCSV["title"][index],
                                 "year": tempCSV["year"][index],
                                 "genre": tempCSV["genre"][index],
                                 "director": tempCSV["director"][index],
                                 "cast": tempCSV["cast"][index],
                                 "countries": tempCSV["countries"][index],
                                 "rating": tempCSV["rating"][index],
                                 "languages": tempCSV["languages"][index]})

            else:
                print("Removing: " + title_year)

def updateLastUpdatedMovieList(most_recent_list):
    """
    Function to update the last updated movies text file to the most recent version

    :param most_recent_list: the most recently updated list of last updated movies
    """
    most_recent_list.seek(0)

    last_updated_list = open(last_updated_list_file, "w")

    for line in most_recent_list:
        last_updated_list.write(line)

    last_updated_list.close()


_imdb = IMDb()

movie_list = open(movie_list_file, "r")
last_updated_movie_list = open(last_updated_list_file, "r")

populateLastUpdatedArray(last_updated_movie_list)
all_imdb_movies = getMovies(movie_list)

last_updated_movie_list.close()

appendToCSVfile(all_imdb_movies)

if len(last_updated_list_array) > 0:
    removeFromCSVfile()

updateLastUpdatedMovieList(movie_list)
movie_list.close()
