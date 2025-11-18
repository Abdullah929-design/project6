import streamlit as st
import pickle
import requests
import os


# -----------------------------
# Function to fetch movie poster
# -----------------------------
def fetch_poster(movie_id):
    api_key = "117c8d6e27ad7ccca41f4b79f4534b4f"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')

    if poster_path:
        return "https://image.tmdb.org/t/p/w500" + poster_path
    else:
        return "https://via.placeholder.com/500x750?text=No+Image"


# -----------------------------
# Function to recommend movies
# -----------------------------
def recommend(movie):
    index = movies_df[movies_df['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:  # Top 5 recommendations
        movie_id = movies_df.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies_df.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters


# -----------------------------
# Load data
# -----------------------------
def download_large_file_from_google_drive(file_id, destination):
    # Adapted from: https://stackoverflow.com/a/39225039
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)
    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)
    with open(destination, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

FILE_ID = '1aysMEIEUNpTrC3RPkNE_lSevUniFgNLw'
SIMILARITY_PATH = 'similarity.pkl'

if not os.path.exists(SIMILARITY_PATH):
    st.info('Downloading similarity.pkl from Google Drive...')
    try:
        download_large_file_from_google_drive(FILE_ID, SIMILARITY_PATH)
        st.success('similarity.pkl downloaded!')
    except Exception as e:
        st.error(f"Failed to download similarity.pkl: {e}")

if not os.path.exists(SIMILARITY_PATH):
    st.error("similarity.pkl not found. Download failed or not accessible. Please check your Google Drive link and sharing settings.")
    st.stop()

movies_df = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies_list = movies_df['title'].values


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox("Select a Movie", movies_list)

if st.button("Show Recommendations"):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    cols = st.columns(5)  # 5 columns for 5 recommendations
    for col, name, poster in zip(cols, recommended_movie_names, recommended_movie_posters):
        col.text(name)
        col.image(poster, use_container_width=True)  # Updated parameter
