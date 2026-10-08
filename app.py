import streamlit as st
import pickle
import joblib
import difflib
from streamlit_searchbox import st_searchbox
st.title("Movie Recommendation System")
with open("movies.pkl", "rb") as m:
    data = pickle.load(m)
similarities = joblib.load("similarity.joblib")
movies=sorted(set(data['title'].values))
def recommend(movie):
    movie_index = data[data['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarities[movie_index])), reverse=True, key=lambda x: x[1])
    recommend_movie = []
    for i in distances[1:6]:
        recommend_movie.append(data.iloc[i[0]].title)
    return recommend_movie

def search_movies(term):
    term = term.strip().lower()
    # titles starting with the typed letters first, then titles where a later word starts with them ("conjuring" -> "The Conjuring")
    matches = [t for t in movies if t.lower().startswith(term)]
    matches += [t for t in movies if " " + term in t.lower() and t not in matches]
    if not matches:
        # nothing found: allow small spelling mistakes ("comjuring" -> "The Conjuring")
        lower_titles = {t.lower(): t for t in movies}
        matches = [lower_titles[t] for t in difflib.get_close_matches(term, list(lower_titles), n=10, cutoff=0.6)]
    if term:
        # typing a new name replaces the movie picked before
        st.session_state["typed_match"] = matches[0] if matches else None
        st.session_state["not_found"] = not matches
        st.session_state["searchbox"]["result"] = None
    return matches

def pick_movie(title):
    # a recommended movie was clicked: put it in the search box and recommend for it
    st.session_state["movie"] = title
    st.session_state["box_text"] = title
    st.session_state["typed_match"] = None
    st.session_state["not_found"] = False
    del st.session_state["searchbox"]

box_text = st.session_state.get("box_text", "")
# a clicked movie is shown in the box as its placeholder, so typing a new name replaces it
selected_movie = st_searchbox(search_movies, label="Enter the Movie Name", placeholder=box_text or "Type a movie name...", default=box_text or None, default_options=movies)
if st.button("Recommend"):
    # use the picked movie, else the first movie matching what was typed, else the first movie in the data
    movie = selected_movie or st.session_state.get("typed_match") or data["title"][0]
    if not selected_movie and st.session_state.get("not_found"):
        st.session_state.pop("movie", None)
        st.warning("No movie found with that name.")
    elif movie == selected_movie:
        st.session_state["movie"] = movie
    else:
        pick_movie(movie)
        st.rerun()
if "movie" in st.session_state:
    st.write("The Recommended Movies for", st.session_state["movie"], "are :")
    for title in recommend(st.session_state["movie"]):
        st.button(title, key="rec_" + title, type="tertiary", on_click=pick_movie, args=(title,))
