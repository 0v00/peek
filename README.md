# peek
( ͡° ͜ʖ ͡°)	

Playing around with FastAPI, FFmpeg, and SQLite. Not really meant for anyone else to use (you obviously can't run this, unless you also have the same movie files inside of `peek/app/movie_files/`). A toy project to improve my Python.

1. `uvicorn app.main:app --reload`
2. `curl -o peek.jpg http://localhost:8000/movies/1/screenshot`
3. enjoy the screenshot. print it out. frame it.

### Get List of Movies

- **Endpoint**: `GET /movies`
- **Description**: Retrieves a list of all movies in the database, including their IDs, titles, release years, and directors.

```json
[
    {"id":1,"title":"Blood Sport","year":1988,"director":"Newt Arnold"},
    {"id":2,"title":"Boiling Point","year":1990,"director":"Takeshi Kitano"},
    {"id":3,"title":"Ghost in the Shell","year":1995,"director":"Mamoru Oshii"}
]
```

### Get Movie Screenshot

- **Endpoint**: `GET /movies/{movie_id}/screenshot`
- **Description**: Retrieves a random screenshot from the movie specified by the given `movie_id`.
- **Param**: 
    - `movie_id`
- **Returns**: `image/jpeg` in binary format

<img src="peek.jpg" alt="screenshot demo" width="500"/>

### Get Movie GIF

- **Endpoint**: `GET /movies/{movie_id}/gif`
- **Description**: Generates and retrieves a random 10-second GIF from the movie specified by the given `movie_id`.
- **Param**: 
    - `movie_id`
- **Returns**: `image/gif` in binary format

![Demo GIF](peek.gif)