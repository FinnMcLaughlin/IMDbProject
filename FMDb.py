import pandas as pd
import streamlit as st
import random

year = []
genre = []
language = []
actor = []
director = []

filters = {}

button_label = "Get Movie Recommendation"
no_data_tag = "N/A"

def splitData(column, data):
    data_array = []

    if column == "genre":
        for item in data.split(","):
            data_array.append(item.replace("'", "").replace("[", "").replace("]", "").replace(" ", ""))


    if column == "actor" or column == "director":
        for item in data.split(","):
            data_array.append(item.split("_")[1])

    if column == "languages":
        if not type(data) is str:
            data_array.append(no_data_tag)
        elif len(data.split(",")) > 1:
            for item in data.split(","):
                data_array.append(item.replace("'", "").replace("[", "").replace("]", "").replace(" ", ""))
        else:
            data_array.append(data.replace("'", "").replace("[", "").replace("]", "").replace(" ", ""))

    return data_array

def isPresent(array, item):
    if item in array:
        return True
    else:
        return False

def getOptions(movie_data):
    for ind in movie_data.index:
        if not isPresent(year, movie_data["year"][ind]):
            year.append(movie_data["year"][ind])

        genre_data = splitData("genre", movie_data["genre"][ind])
        for g in genre_data:
            if not isPresent(genre, g):
                genre.append(g)

        language_data = splitData("languages", movie_data["languages"][ind])
        for l in language_data:
            if not isPresent(language, l):
                language.append(l)

        actor_data = splitData("actor", movie_data["cast"][ind])
        for a in actor_data:
            if not isPresent(language, a):
                actor.append(a)

        director_data = splitData("director", movie_data["director"][ind])
        for d in director_data:
            if not isPresent(director, d):
                director.append(d)

    genre.sort()
    year.sort()
    language.sort()

def getRecommendation(movie_list):
    if len(filters) > 0:
        filtered_movie_list = pd.DataFrame()

        for filters_key in filters:
            filtered_movie_list = mergeFilteredMovieList(filtered_movie_list, getFilter(filters_key, filters[filters_key], movie_list))

        random_index = random.randrange(0, len(filtered_movie_list.index))
        return filtered_movie_list.iloc[random_index]

    else:
        random_index = random.randrange(0, len(movie_list.index))
        return movie_list.iloc[random_index]

def displayRecommendation():
    st.title("Movie Recommended")
    recommendation = getRecommendation(movies)

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

def formatArrayToString(data_array):
    formatted_string = ""
    for data in data_array:
        formatted_string = formatted_string + data + ", "

    return formatted_string[:-2]

def getFilter(key, value, dataframe):
    if value == "genre":
        return dataframe[dataframe.genre.str.contains(key)]
    '''
    if value == "year":
        return dataframe[dataframe.year.str.contains(key)]
    if value == "languages":
        return dataframe[dataframe.languages.str.contains(key)]
    '''

def mergeFilteredMovieList(filtered_movie_list, new_movie_list):
    if len(filtered_movie_list.index) > 0:
        return pd.merge(filtered_movie_list, new_movie_list, on=list(filtered_movie_list.columns.values), how="inner")
    else:
        return new_movie_list

movies = pd.read_csv("movie_info.csv")
getOptions(movies)

getRecommendation(movies)

st.sidebar.title("Genre(s)")
for g in genre:
    if not g == no_data_tag:
        if st.sidebar.checkbox(label=str(g), key=g, value=False):
            filters[g] = "genre"

st.sidebar.title("Year")
for y in year:
    if not y == no_data_tag:
        if st.sidebar.checkbox(label=str(y), key=y, value=False):
            filters[y] = "year"

st.sidebar.title("Languages")
for l in language:
    if not l == no_data_tag:
        if st.sidebar.checkbox(label=str(l), key=l, value=False):
            filters[l] = "languages"

if st.button(button_label):
    displayRecommendation()

#st.write(movies[movies.genre.str.contains('Horror')])

