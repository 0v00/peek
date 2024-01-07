import sqlite3

def get_db_connection():
    conn = sqlite3.connect('movies.db')
    return conn

def get_movie_by_id(movie_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
    movie = c.fetchone()
    conn.close()
    return movie