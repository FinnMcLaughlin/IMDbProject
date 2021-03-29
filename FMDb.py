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

current_filter_options = ["genre", "year", "languages", "rating"]


# Dictionary to handle all active filters
filters = {}

# Dictionary to store all decades in for mass filter selection on years
decades = {}

button_label = "Get Movie Recommendation"
no_data_tag = "N/A"

@st.cache(allow_output_mutation=True)
def initializeUsedIndexArray():
    """
    Function to initialize an array of previously suggested indexes as well as a dictionary to keep track of updates or
    changes to the filter options, to prevent any repeat suggestions

    :return: An empty array and dictionary
    """
    return [], {}

def splitData(column, data):
    """
    Based on the column name passed to the function, the appropriate method of data extraction takes place, and a list
    containing the extracted data is returned

    :param column: the name of the column that the data is from, which determines the method of extracting it
    :param data: the pre-extracted data
    :return: an array containing the extracted data

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

def initializeDecadesArray():
    """
    Function to populate the decades dictionary, a dictionary that contains the values of all available years for each
    decade in an attempt to streamline the year filter process

    """
    current_decade = str(year[0])[:-1]

    decades[current_decade + "0s"] = []

    for _year in year:
        if  not current_decade in str(_year):
            current_decade = str(_year)[:-1]
            decades[current_decade + "0s"] = []

        decades[current_decade + "0s"].append(_year)

def getFilter(filter_key, filter_value, dataframe):
    """
    Function to return a filtered data frame based on the given filter option

    :param filter_value: the value of the filter option
    :param filter_key: the type of filter needed
    :param dataframe: the data frame that is being filtered
    :return: the filtered data frame

    TODO: - Add an OR condition for actors, directors etc.
    """
    if filter_key == "genre":
        return dataframe[dataframe.genre.str.contains(filter_value)]

    if filter_key == "year":
        return dataframe.loc[dataframe.year == filter_value]

    if filter_key == "languages":
        return dataframe[dataframe.languages.str.contains(filter_value, na=False)]

    if filter_key == "rating":
        return dataframe[dataframe.rating >= filter_value]

def mergeFilteredMovieList(filtered_movie_list, new_movie_list, key):
    """
    Function to merge the filtered movie suggestion data frames. By default genre concatenation will concatenate the two
    filtered data frame objects by the intersection, whereas other concatenation will concatenate by the union. The logic here
    is that you can have a movie of two different genres (Action Comedy) but not a movie from two different years. However
    users can choose to be recommended movies that fit either genres, when more than one genre is selected.

    :param key: the filter key to determine what type of concatenation will occur
    :param filtered_movie_list: the prime filtered data frame
    :param new_movie_list: the data frame to be merged with the prime data frame
    :return: the merged data frame
    """
    if len(filtered_movie_list.index) > 0:
        if key == "rating":
            return pd.concat([filtered_movie_list, new_movie_list], axis=1, join="inner")
        elif key == "genre" and filters["genre_filter_type"] == "Must fit all genres":
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

    rand_index = random.randrange(0, len(movie_list.index))

    if rand_index in used_index_array and attempt_count < 25:
        return getRandomIndex(movie_list, attempt_count + 1)
    else:
        return rand_index

def insertIntoUsedIndexArray(index):
    """
    Function to insert an index into the used index array, to prevent repeat suggestions

    :param index: the most recently suggested index
    """
    global used_index_array

    used_index_array.append(index)

def resetUsedIndexArray():
    """
    Function to clear contents of used index array

    """
    global used_index_array

    used_index_array.clear()

def updateFilterOptionsDictionary():
    """
    Function to update the updated_filter_options_dictionary data, to the most recent version of the selected filters

    """
    global updated_filter_options_dictionary

    updated_filter_options_dictionary.clear()

    for key in filters.keys():
        updated_filter_options_dictionary[key] = filters[key]

def checkForChangeInFilters(random_index):
    """
    Function to check for changes made to the selected filters. If the filters dictionary and the updated_filter_options_dictionary
    are no the same, then the used index array is reset. If they are the same, the current index is added to the used index array
    to prevent repeat recommendations

    :param random_index: the index of the recommended movie from the data frame

    """
    global updated_filter_options_dictionary

    if not updated_filter_options_dictionary == filters:
        resetUsedIndexArray()
        updateFilterOptionsDictionary()

    insertIntoUsedIndexArray(random_index)



def getOptions(movie_data):
    """
    Function to populate the filter lists based on the csv data. The function goes through each row and column, storing
    all necessary and new information in their respective arrays.

    :param movie_data: the data from the csv file
    """
    for ind in movie_data.index:
        genre_data = splitData("genre", movie_data["genre"][ind])
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

    # Initialize the decades array
    initializeDecadesArray()

def addFilterToFiltersDictionary(filter_key, value):
    """
    Function to add chosen filters to the fitlers dictionary

    :param filter_key: the filter type, and the key in which the filter value will be stored under
    :param value: the filter value
    """
    if filter_key in filters.keys():
        filters[filter_key].append(value)
    else:
        filters[filter_key] = [value]

def displayRecommendation():
    """
    Function to get a recommendation for the user, and display that recommendation information using streamline
    """
    st.title("Movie Recommended")
    recommendation = getRecommendation(movies)

    if len(recommendation) > 0:
        # Title printed for image debug purposes
        st.write(recommendation.title)

        st.image(getMoviePoster(recommendation.title.replace(":", "")), "Poster for " + recommendation.title, use_column_width=True)

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
        st.image("resources/resource_images/no_rec_image.png", "Truly, a sad day", use_column_width=True)

def getRecommendation(movie_list):
    """
    Function to get a data frame of movies to be recommended, including filters if applicable, which are stored within
    the filters dictionary. If there are filters present, a data frame is created for each filter condition, and all
    data frames are merged to create the final filtered data frame containing the movie suggestions. If no filters are
    present, then a random index is produced from the unfiltered movie list.

    If the combination of genres results in an empty data frame, then no other filters are checked, and an empty data
    frame is returned. This is due to how the data frame merging implementation results in trying to intersect other
    filter's data frames with an empty data frame, which leads to recommendations that do not fit the genres selected

    :param movie_list: a list of all movies
    :return: the recommended movie data
    """
    filtered_movie_list = movie_list

    if any(x in current_filter_options for x in filters.keys()):
        filtered_movie_list = pd.DataFrame()

        for key in filters:

            if not key == "genre_filter_type":

                if not key == "genre" and "genre" in filters.keys():
                    if len(filtered_movie_list) < 1:
                        return pd.DataFrame()

                if (key == "genre" and filters["genre_filter_type"] == "Must fit all genres") or key == "rating":
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


    if len(filtered_movie_list) > 0:

        if not len(filtered_movie_list) > len(used_index_array):
            st.write("All recommendations for this set of filters has been recommended!")
            resetUsedIndexArray()

        random_index = getRandomIndex(filtered_movie_list, 0)

        checkForChangeInFilters(random_index)

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
    # Array to keep track of previously recommended indexes to avoid repeat recommendations
    # global used_index_array, updated_filter_options_dictionary
    used_index_array, updated_filter_options_dictionary = initializeUsedIndexArray()

    # Reads in movie data from csv file
    movies = pd.read_csv("movie_info.csv")

    # Extracts the filter options for the sidebar from the csv file and stores them in their respective arrays
    getOptions(movies)


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
                            addFilterToFiltersDictionary("genre", g)

    with st.sidebar.beta_expander("Year(s)"):
        year_filter_type = st.radio("By Decade or specific year(s)", ("Decade", "Specific Year(s)"))
        if year_filter_type == "Decade":
            for key in decades:
                if st.checkbox(label=str(key), key=key, value=False):
                    for val in decades[key]:
                        addFilterToFiltersDictionary("year", val)
        else:
            for y in year:
                if not y == no_data_tag:
                    if st.checkbox(label=str(y), key=y, value=False):
                        addFilterToFiltersDictionary("year", y)

    with st.sidebar.beta_expander("Language(s)"):
        for l in language:
            if not l == no_data_tag:
                if st.checkbox(label=str(l), key=l, value=False):
                    addFilterToFiltersDictionary("languages", l)

    with st.sidebar.beta_expander("Rating"):
        rating_filter_type = st.radio("", ("Any Rating", "Minimum Rating"))
        if rating_filter_type == "Minimum Rating":
            filters["rating"] = [st.slider("Minimum Rating", 0.0, 10.0, 0.0, 0.1, "%f")]


    if "genre" in filters.keys() and len(filters["genre"]) > 1:
        filters["genre_filter_type"] = st.radio("More than one genre selected. Do you want recommendations for movies that fit all selected genres"
                                     "or any movie that fits any of the selected genres", ('Must fit all genres', 'Any of the selected genres'))
    else:
        filters["genre_filter_type"] = ""


    if st.button(button_label):
        displayRecommendation()