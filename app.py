from flask import Flask, render_template, request
import csv
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import pickle

app = Flask(__name__)

# Load the similarity matrix from the .pkl file
with open('model/similarity.pkl', 'rb') as file:
    similarity = pickle.load(file)

# Load the DataFrame containing movie details
new = pd.read_csv('dataset/preprocessed_movies.csv')

# Function to fetch movie IDs from the dataset
def fetch_movie_ids():
    movie_ids = []
    with open('dataset/preprocessed_movies.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            movie_ids.append(int(row['id']))
    return movie_ids

# Function to fetch details for 15 movies from the dataset
def fetch_top_movies():
    all_movies = []
    top_movies = []
    trending_movies = []
    popular_movies = []

    with open('dataset/preprocessed_movies.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            movie_detail = {
                'id': int(row['id']),
                'backdrop_path': "https://image.tmdb.org/t/p/w1280/" + row['backdrop_path'],
                'poster_path': "https://image.tmdb.org/t/p/w1280/" + row['poster_path'],
                'title': row['title'],
                'release_date': row['release_date'],
                'runtime': row['runtime'],
                'vote_average': row['vote_average'],
                'certification': row['certification'],
                'genres': row['genres'],
                'overview': row['overview'],
                'casts': row['casts'],
                'directors': row['directors'],
                'keywords': row['keywords'],
                'popularity': row['popularity'],
                'language': row['original_language']
            }
            add_videos(movie_detail, row['videos'])
            all_movies.append(movie_detail)

            # Check if the movie is trending
            if float(row['vote_average']) > 8:
                trending_movies.append(movie_detail)

            # Check if the movie is popular (released in the current year with rating above 8.0)
            if float(row['popularity']) > 100:
                popular_movies.append(movie_detail)

            # Break the loop if 15 eligible movies are found
            if len(top_movies) == 50 and len(trending_movies) >= 5:
                break

    top_movies = all_movies[:15]
    popular_movies = popular_movies[:15]

    return all_movies, top_movies, trending_movies, popular_movies  

# Function to add videos to the movie details dictionary
def add_videos(movie_detail, videos):
    video_urls = videos.split(', ')  # Assuming videos are separated by commas in the CSV
    movie_detail['videos'] = ["https://www.youtube.com/embed/" + url + "?&theme=dark&color=white&rel=0" for url in video_urls]

# Route for rendering the index page with top 15 movies
@app.route('/')
def index():
    all_movies, top_movies, trending_movies, popular_movies = fetch_top_movies()
    return render_template('index.html', movies=top_movies, trending=trending_movies, popular=popular_movies)


@app.route('/detail/<int:movie_id>')
def detail(movie_id):
    movie_ids = fetch_movie_ids()
    if movie_id in movie_ids:
        # Fetch details for all movies
        all_movies, _, _, _ = fetch_top_movies()
        # Find the movie with the specified ID
        movie_details = next((movies for movies in all_movies if movies['id'] == movie_id), None)
        recommended_movies = recommend(movie_details['title'])
        if movie_details:
            return render_template('detail.html', movies=movie_details, recommended=recommended_movies)
        else:
            return "Movie details not found", 404
    else:
        return "Movie not found", 404
    
@app.route('/movie-list/<genre>')
def genre_movie_list(genre):
    # Fetch all movies
    all_movies, _, _, _ = fetch_top_movies()
    
    # Filter movies based on the genre
    genre_movies = [movie for movie in all_movies if isinstance(movie, dict) and movie.get('genres') and genre.lower() in movie['genres'].lower()]

    # Handle search query
    search_query = request.args.get('q', '')
    if search_query:
        # First, filter genre_movies based on title matches
        title_matches = [movie for movie in all_movies if search_query.lower() in movie['title'].lower()]

        # Then, filter remaining genre_movies based on keyword matches
        keyword_matches = [movie for movie in all_movies if movie not in title_matches and movie.get('keywords') and any(search_query.lower() in movie['keywords'].lower() for keyword in movie['keywords'].split(', '))]

        # Concatenate the lists to get the final search results
        search_results = title_matches + keyword_matches
        genre_movies = search_results

    return render_template('movie-list.html', movies=genre_movies)

# Function to recommend movies
def recommend(movie, k=10):
    # Convert the search query to lowercase
    movie = movie.lower()
    
    # Find the index of the movie in the DataFrame
    index = new[new['title'].str.lower() == movie].index
    
    if len(index) == 0:
        print("Movie not found.")
        return []
    
    index = index[0]
    
    # Initialize the KNN model
    knn = NearestNeighbors(n_neighbors=k, metric='cosine')
    knn.fit(similarity)  # similarity is the similarity matrix
    
    # Get the indices of the nearest neighbors
    distances, indices = knn.kneighbors([similarity[index]])
    
    # Return the titles of the top k similar movies
    recommended_movies = [new.iloc[i].to_dict() for i in indices[0][1:]]
    return recommended_movies

if __name__ == '__main__':
    app.run(debug=True)
