import sqlite3

def get_db_connection():
    conn = sqlite3.connect('movies.db')
    return conn

def get_all_movies():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, title, year, director FROM movies')
    # fetchall() returns a list of tuples
    movies_tuples_list = c.fetchall()
    conn.close()
    # transform it into a list of dict items
    return [{"id": id, "title": title, "year": year, "director": director} for id, title, year, director in movies_tuples_list]

def get_movie_by_id(movie_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
    movie = c.fetchone()
    conn.close()
    return movie