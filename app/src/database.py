from sqlmodel import SQLModel, create_engine, Field, Session
import models
from models import Ratings, Movies
import pandas as pd
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy.ext.declarative import declarative_base
import sqlite3
# define db filename
sqlite_filename = "database.db"
# create a sqlite db
sqlite_url = f"sqlite:///{sqlite_filename}"

Base = declarative_base()
# create a db engine
engine = create_engine(sqlite_url, echo=True, connect_args={"check_same_thread": False})


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# session = Session(bind=engine)
# session = SessionLocal()

conn = sqlite3.connect(sqlite_filename)
cur = conn.cursor()

def get_db():
    db: Session = SessionLocal()
    try:
        # the yield statement suspends the function’s execution and sends a value back to the caller
        yield db
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def insert_data_ratings(filename):
    f = pd.read_csv(filename, sep = "\t").head(1000)
    #print(f.columns)
    
    with Session(engine) as session:
        for id, row in f.iterrows():
            #print(row)
            item = Ratings(tconst = row.tconst, averageRating = row.averageRating, numVotes = row.numVotes)
            session.add(item)

        session.commit()


def insert_data_movies(filename):
    f = pd.read_csv(filename, sep = "\t").head(1000)

    with Session(engine) as session:
        for id, row in f.iterrows():
            #print(row)
            item = Movies(tconst = row.tconst, titleType = row.titleType, primaryTitle = row.primaryTitle,startYear= row.startYear, runtimeMinutes= row.runtimeMinutes,
            genres = row.genres )
            session.add(item)

        session.commit()

if __name__ == '__main__':
    print("start program")
    SQLModel.metadata.create_all(engine)
    print("insert rating in ratings table")
    filename = "../data/title.ratings.tsv/data.tsv"
    insert_data_ratings(filename)
    print("insert movi in movies table")
    filename = "../data/title.basics.movie.tsv"
    insert_data_movies(filename)
