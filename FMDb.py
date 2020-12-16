import pandas as pd
import streamlit as st

movies = pd.read_csv("movie_info.csv")
#print(movies[movies.genre.str.contains('Horror')])

st.title("Title")
st.write(movies[movies.genre.str.contains('Horror')])

