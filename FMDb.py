import pandas as pd
import streamlit as st
from PIL import Image, ImageFile
import random
import os

ImageFile.LOAD_TRUNCATED_IMAGES = True

# Array for all filter options that will be displayed on sidebar
year = []
genre = []
language = []
actor = []
director = []

# Array to keep track of previously recommended indexes to avoid repeat recommendations
#global used_index
used_index = []

# Dictionary to handle all active filters
filters = {
    "genre": [],
    "year": [],
    "languages": []
}

button_label = "Get Movie Recommendation"
no_data_tag = "N/A"

@st.cache(allow_output_mutation=True)
def initializeUsedIndexArray():
    """
    Function to initialize an array of previously suggested indexes, to prevent any repeat suggestions

    :return: An empty array
    """
    return []

def splitData(column, data):
    """
    Due to data format inconsistencies across different columns in the csv file, this function will manually extract the
    necessary data from the specified column until a suitable method is in place to make the data from each column uniform.
    Based on the column name passed to the function, the appropriate method of data extraction takes place, and a list
    containing the extracted data is returned

    :param column: the name of the column that the data is from, which determines the method of extracting it
    :param data: the pre-extracted data
    :return: an array containing the extracted data

    TODO: Once the logic is fully realised, clean up the code to make more efficient
    TODO: Create a method in updateCSV.py to make the data in the csv more uniform, to scale down the size of this method
    """
    data_array = []

    if column == "languages":
        if not type(data) is str:
            data_array.append(no_data_tag)
        elif len(data.split(",")) > 1:
            for item in data.split(","):
                data_array.append(item[1:-1].replace("'", "").replace(" ", ""))
        else:
            data_array.append(data[1:-1].replace("'", "").replace(" ", ""))

    else:
        for value in data.split(","):
            data_array.append(value[1:-1].replace("'",""))

    return data_array

def isPresent(array, item):
    """
    Function to check if a given item is in a specified array

    :param array: the array that the specified item may or may not be present in
    :param item: the item that is being looked for in the given array
    :return: a boolean denoting whether the item was found in the array
    """
    if item in array:
        return True
    else:
        return False

def getFilter(filter_key, filter_value, dataframe):
    """
    Function to return a filtered data frame based on the given filter option

    :param filter_value: the value of the filter option
    :param filter_key: the type of filter needed
    :param dataframe: the data frame that is being filtered
    :return: the filtered data frame

    TODO: Complete rework of this function in tandem with the getRecommendation function
    TODO: - Add an OR condition for actors, directors etc.
    """
    if filter_key == "genre":
        return dataframe[dataframe.genre.str.contains(filter_value)]

    if filter_key == "year":
        return dataframe.loc[dataframe.year == filter_value]

    if filter_key == "languages":
        return dataframe[dataframe.languages.str.contains(filter_value, na=False)]

def mergeFilteredMovieList(filtered_movie_list, new_movie_list, key):
    """
    Function to merge the filtered movie suggestion data frames. Genre concatenation will concatenate the two filtered
    data frame objects by the intersection, whereas other concatenation will concatenate by the union. The logic here
    is that you can have a movie of two different genres (Action Comedy) but not a movie from two different years.

    :param key: the filter key to determine what type of concatenation will occur
    :param filtered_movie_list: the prime filtered data frame
    :param new_movie_list: the data frame to be merged with the prime data frame
    :return: the merged data frame
    """
    if len(filtered_movie_list.index) > 0:
        if key == "genre" and genre_filter_type == "&&":
            return pd.concat([filtered_movie_list, new_movie_list], axis=1, join="inner")
        else:
            return pd.concat([filtered_movie_list, new_movie_list])
    else:
        return new_movie_list

def getRandomIndex(movie_list, attempt_count):
    """
    Function to get a random index from the given data set. The random range is between 0 and the length of the given
    data set's index count

    :param movie_list: the data set that the suggestion will come from
    :param attempt_count: the count of how many attempts it has been to find a unique suggestion. While the attempt_count
    is below a given threshold, an attempt will be made to find an index of a movie that has yet to be suggested. If the
    attempt_count goes above the given threshold, then the most recently decided random index is used, regardless of
    whether it is a repeat suggestion or not.
    :return: the index of the next randomly suggested movie from the given data set
    """
    print("-------------------------------" + str(len(movie_list)) + "-------------------------------")
    rand_index = random.randrange(0, len(movie_list.index))

    print("Attempt Count : " + str(attempt_count))

    if rand_index in used_index and attempt_count < 25:
        getRandomIndex(movie_list, attempt_count + 1)
    else:
        print("----------------------------\n\n")
        return rand_index

def insertIntoUsedIndexArray(index):
    """
    Function to insert an index into the used index array, to prevent repeat suggestions

    :param index: the most recently suggested index
    """
    used_index.append(index)

def resetUsedIndexArray():
    """
    Function to clear contents of used index array

    """
    used_index.clear()


def getOptions(movie_data):
    """
    Function to populate the filter lists based on the csv data. The function goes through each row and column, storing
    all necessary and new information in their respective arrays.

    :param movie_data: the data from the csv file
    """
    for ind in movie_data.index:
        genre_data = splitData("genre", movie_data["genre"][ind])
        #print("Genre Data: " + str(genre_data))
        for g in genre_data:
            if not isPresent(genre, g):
                genre.append(g)

        if not isPresent(year, movie_data["year"][ind]):
            year.append(movie_data["year"][ind])

        language_data = splitData("languages", movie_data["languages"][ind])
        for l in language_data:
            if not isPresent(language, l):
                language.append(l)

        actor_data = splitData("actor", movie_data["cast"][ind])
        for a in actor_data:
            if not isPresent(actor, a):
                actor.append(a)

        director_data = splitData("director", movie_data["director"][ind])
        for d in director_data:
            if not isPresent(director, d):
                director.append(d)

    actor.sort()
    director.sort()
    genre.sort()
    year.sort()
    language.sort()

def displayRecommendation():
    """
    Function to get a recommendation for the user, and display that recommendation information using streamline

    """
    st.title("Movie Recommended")
    recommendation = getRecommendation(movies)

    print(recommendation)

    if len(recommendation) > 0:
        st.write(used_index)
        st.write(genre_filter_type)

        # Title printed for image debug purposes
        st.write(recommendation.title)

        st.image(getMoviePoster(recommendation.title), "Poster for " + recommendation.title, use_column_width=True)

        st.header("Title")
        st.subheader(recommendation.title)

        st.header("Year")
        st.subheader(str(recommendation.year))

        st.header("Rating")
        st.subheader(str(recommendation.rating))

        st.header("Genre")
        st.subheader(formatArrayToString(splitData("genre", recommendation.genre)))

        st.header("Cast")
        st.subheader(formatArrayToString(splitData("actor", recommendation.cast)))

        st.header("Director")
        st.subheader(formatArrayToString(splitData("director", recommendation.director)))

        st.header("Language")
        st.subheader(formatArrayToString(splitData("languages", recommendation.languages)))
    else:
        st.write("Unfortunately no movie from the list fits this criteria")
        st.image("resources/no_rec_image.png", "Truly, a sad day", use_column_width=True)

def getRecommendation(movie_list):
    """
    Function to get a data frame of movies to be recommended, including filters if applicable, which are stored within
    the filters dictionary. If there are filters present, a data frame is created for each filter condition, and all
    data frames are merged to create the final filtered data frame containing the movie suggestions. If no filters are
    present, then a random index is produced from the unfiltered movie list

    :param movie_list: a list of all movies
    :return: the recommended movie data

    TODO: a complete rework of this function is necessary, as it currently deals with only AND logic when dealing with more than one filter
    """
    filtered_movie_list = movie_list

    if len(filters["genre"]) > 0 or len(filters["year"]) > 0 or len(filters["languages"]) > 0:
        filtered_movie_list = pd.DataFrame()

        print(str(filters))

        for key in filters:
            if len(filters[key]) > 0:
                if key == "genre":
                    for filter_option in filters[key]:

                        filtered_movie_list = mergeFilteredMovieList(filtered_movie_list, getFilter(key, filter_option, movie_list), key).drop_duplicates()
                        filtered_movie_list = filtered_movie_list.loc[:, ~filtered_movie_list.columns.duplicated()]

                else:
                    dataframes = []

                    for filter_option in filters[key]:
                        if len(filtered_movie_list.index) > 0:
                            dataframes.append(getFilter(key, filter_option, filtered_movie_list))
                        else:
                            dataframes.append(getFilter(key, filter_option, movie_list))

                    filtered_movie_list = dataframes[0]

                    if len(dataframes) > 1:
                        for df in dataframes[1:]:
                            filtered_movie_list = mergeFilteredMovieList(filtered_movie_list, df, key)
                            filtered_movie_list = filtered_movie_list.loc[:, ~filtered_movie_list.columns.duplicated()]


    print("Length: " + str(len(filtered_movie_list)))
    print(filtered_movie_list)

    if len(filtered_movie_list) > 0:
        random_index = getRandomIndex(filtered_movie_list, 0)

        print(random_index)
        # insertIntoUsedIndexArray(random_index)

        return filtered_movie_list.iloc[random_index].drop_duplicates()

    else:
        return filtered_movie_list

def getMoviePoster(movie_title):
    """
    Function to get the poster of the recommended movie from the movie poster folder based on the given movie title. The
    movie poster subfolders are sorted alphabetically, and so the first letter of the movie title is used in the path. If
    the movie title begins with a numeric value, then the '#' is folder is accessed.

    :param movie_title: movie title of the required movie poster image
    :return: the image of the requested movie poster
    """
    if movie_title[0].isdigit():
        poster_file_path = os.path.join(os.getcwd(), "movie_posters", "#", movie_title + ".jpg")
    else:
        poster_file_path = os.path.join(os.getcwd(), "movie_posters", movie_title[0].upper(), movie_title + ".jpg")

    Image.MAX_IMAGE_PIXELS = None
    poster_file = Image.open(poster_file_path)

    return poster_file

def formatArrayToString(data_array):
    """
    Function to format the contents of an array to a string of it's values. Used primarily when displaying the information
    of the recommended movie to the user, as some information is stored as an array, but needs to be displayed as a string

    :param data_array: an array of the required data to be formatted
    :return: the formatted data
    """
    formatted_string = ""
    for data in data_array:
        formatted_string = formatted_string + data + ", "

    return formatted_string[:-2]


if __name__ == "__main__":
    # Reads in movie data from csv file
    movies = pd.read_csv("movie_info.csv")

    #for name, dtype in movies.dtypes.iteritems():
        #print(name, dtype)

    # Extracts the filter options for the sidebar from the csv file and stores them in their respective arrays
    getOptions(movies)

    # Recommendation function request for testing purposes
    #filters["genre"].append("Comedy")
    #filters["genre"].append("Action")
    #filters["year"].append(1992)
    #filters["year"].append(1993)
    #filters["year"].append(1994)
    #filters["year"].append(1995)

    #print(getRecommendation(movies))

    # Streamlit code for the sidebar where users can add filters to their movie recommendations
    # Each filter options have a title and are taken from their respective arrays that were populated from
    # the CSV file previously.
    #
    # When a checkbox is chosen, the data is added to the filters dictionary
    # TODO: - Include Actors images

    with st.sidebar.beta_expander("Genre(s)"):
        for g in genre:
            if not g == no_data_tag:
                    if st.checkbox(label=str(g), key=g, value=False):
                            filters["genre"].append(g)

    with st.sidebar.beta_expander("Year(s)"):
        for y in year:
            if not y == no_data_tag:
                if st.checkbox(label=str(y), key=y, value=False):
                    filters["year"].append(y)

    with st.sidebar.beta_expander("Language(s)"):
        for l in language:
            if not l == no_data_tag:
                if st.checkbox(label=str(l), key=l, value=False):
                    filters["languages"].append(l)

    # TODO: Reset used_index array when filter option changes
    used_index = initializeUsedIndexArray()

    genre_filter_type = ""

    # TODO: Change the labels and display message to something more intuitive
    if len(filters["genre"]) > 1:
        genre_filter_type = st.radio("AND gate or OR gate", ('&&', '||'))


    if st.button(button_label):
        displayRecommendation()

    #st.write(movies[movies.genre.str.contains('Horror')])
    #print(movies.loc[movies.year == 1991])