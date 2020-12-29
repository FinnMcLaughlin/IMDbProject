import pandas as pd
import streamlit as st

year = []
genre = []
language = []
actor = []
director = []

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

movies = pd.read_csv("movie_info.csv")
#print(movies[movies.genre.str.contains('Horror')])
getOptions(movies)


st.title("Title")
st.sidebar.title("Genre(s)")
for g in genre:
    st.sidebar.checkbox(label=str(g), key=g, value=False)
st.sidebar.title("Year")
for y in year:
    st.sidebar.checkbox(label=str(y), key=y, value=False)
#st.write(movies[movies.genre.str.contains('Horror')])

