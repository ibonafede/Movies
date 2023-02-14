Requirements:

1) We would like to have an API with the following endpoints:

GET /movies

GET /movies/{id}

POST /movies

 

2) For each movie, the API JSON response shows its:

- title

- category/genre

- year

- rating

- runtime (how long it is)

- a link to the IMDB page of that movie -->not satisfied completely

 

3) we can order/sort by:

- year

- rating

- and of course, by title

 

4) we can filter by:

- category/genre

- rating

General information:

the app name is Movie. The version is 0.1.
the db used is a sqlite db. 
The data are first filtered by movies category. 
The filtered data are in title.basics.movie.tsv. 
The database is limited to a sample of 1000 movies

Folder description

1) src: is the sorce code folder.It has the following scripts:

- database.py : it creates a database with the tables movies and ratings. run python database.py to create the tables

- main.py : it is the main script with theapp command

- models.py: it contains the schema of the main tables

2) templates: it contains html file
3) static: it contains the css style script


Build the image and start the app:


1) build the image:

 docker build -t fastapi-app-image:0.1 . 

2) run the container

docker run -p 8000:8000 --name movies-app fastapi-app-image:0.1

3) go to http://127.0.0.1:8000/


To do steps:

- add logger
- improve the interface (eg insert a list of genre)
- insert a botton to sort and filter the HTML table
- insert an automatic download of the results (as a zip file)
- documentation (schema io.draw + help function)
