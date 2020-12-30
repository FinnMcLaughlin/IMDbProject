import pandas as pd
import streamlit as st
import random

year = []
genre = []
language = []
actor = []
director = []

button_label = "Get Movie Recommendation"

def splitData(column, data):
    data_array = []

    if column == "genre" or column == "languages":
        for item in data.split(","):
            data_array.append(item.replace("'", "").replace("[", "").replace("]", "").replace(" ", ""))


    if column == "actor" or column == "director":
        for item in data.split(","):
            data_array.append(item.split("_")[1])

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

        language_data = splitData("language", movie_data["languages"][ind])
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

def getRecommendation(filtered_movie_list):
    random_index = random.randrange(0, len(filtered_movie_list.index))
    return filtered_movie_list.loc[random_index]

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
    st.subheader(str(recommendation.languages))

def formatArrayToString(data_array):
    formatted_string = ""
    for data in data_array:
        formatted_string = formatted_string + data + ", "

    return formatted_string[:-2]

movies = pd.read_csv("movie_info.csv")
getOptions(movies)


st.sidebar.title("Genre(s)")
for g in genre:
    st.sidebar.checkbox(label=str(g), key=g, value=False)
st.sidebar.title("Year")
for y in year:
    st.sidebar.checkbox(label=str(y), key=y, value=False)

if st.button(button_label):
    displayRecommendation()





#st.write(movies[movies.genre.str.contains('Horror')])

