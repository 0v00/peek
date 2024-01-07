import sqlite3

conn = sqlite3.connect('movies.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS movies (
          id INTEGER PRIMARY KEY,
          title TEXT NOT NULL,
          year INTEGER NOT NULL,
          director TEXT NOT NULL,
          file_name TEXT NOT NULL
)
''')

initial_movies = [
    (1, "Blood Sport", 1988, "Newt Arnold", "blood_sport.mkv"),
    (2, "Boiling Point", 1990, "Takeshi Kitano", "boiling_point.mkv"),
    (3, "Ghost in the Shell", 1995, "Mamoru Oshii", "ghost_in_the_shell.mkv")
]
c.executemany('INSERT INTO movies VALUES (?,?,?,?,?)', initial_movies)

conn.commit()
conn.close()