from fastapi import FastAPI, status, HTTPException, Request, Form
from fastapi import Depends
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Field, SQLModel, Session, select
from database import engine, get_db, cur
from typing import List
from models import Ratings, Movies, MoviesAndRating
import uvicorn
import sqlalchemy
from sqlalchemy import create_engine



app = FastAPI()

# for templating
app.mount("/static", StaticFiles(directory="static"), name = "static")
templates = Jinja2Templates(directory="templates")

# region forms

# list categories where rating> value

from typing import Optional
from fastapi_filter.contrib.sqlalchemy import Filter
from utils.libraries import convert_sort

# Send an HTML table of movies with click-to-edit icon
@app.get('/get_form_list_data', response_class=HTMLResponse)
async def get_form_data_list(request:Request,sort = "primaryTitle"):
    """
    Get all movies
    """ 
    with Session(engine) as session:
        statement = select(Movies.id,Movies.tconst,Movies.primaryTitle,Movies.startYear,Movies.runtimeMinutes,Movies.genres, Ratings.averageRating).join(Ratings,Movies.tconst==Ratings.tconst, isouter=True)
        if sort:
            print(f"sorting by: {sort}")
            statement = statement.order_by(convert_sort(sort))
        results = session.exec(statement).all() 
        context = {'request': request, 'movies':results, 'page_title':'Movies list'}
    return templates.TemplateResponse('form_list_data.html', context)


@app.get('/get_form_edit_data/{id}', response_class=HTMLResponse)
async def get_form_data_edit(id: int, request:Request):
    with Session(engine) as session:
        # Get the movie to edit
        #statement = select(Movies.id,Movies.tconst,Movies.primaryTitle,Movies.startYear,Movies.runtimeMinutes,Movies.genres, Ratings.averageRating).join(Ratings,Movies.tconst==Ratings.tconst, isouter=True).where(Movies.id==id)
        #movie  = session.exec(statement).scalars()
        movie  = session.get(Movies,id)
        print("movie: ", movie)
    # Get a list of genres fo the dropdown list on the form
    # todo: genres
    context = {'movies':movie,'request':request}
    return templates.TemplateResponse('form_edit_data.html', context)    


# Save edited movie
@app.post('/get_form_edit_data/{id}')
#Movies.tconst,Movies.primaryTitle,Movies.startYear,Movies.runtimeMinutes,Movies.genres, Ratings.averageRating
async def submit_form_data_edit(id: int, primaryTitle:str=Form(), startYear:str=Form(), runtimeMinutes:str=Form(),genres:str=Form()): 
    print(id,  primaryTitle)
    updated_item=Movies(id=id, primaryTitle=primaryTitle, startYear=startYear,runtimeMinutes=runtimeMinutes, genres=genres,averageRating=None)
    print(updated_item)
    with Session(engine) as session:
        original_item = session.get(Movies,id)
        items_dict = updated_item.dict(exclude_unset=True)
        for key, value in items_dict.items():
            setattr(original_item,key,value)

        session.commit()
        session.refresh(original_item)

    # Return to movies list page after user saved new item
    response = RedirectResponse(url='/get_form_list_data', status_code=302)
    return response

@app.get('/delete_form_movie/{id}')
async def delete_form_movie(id:int):
    with Session(engine) as session:
        original_video = session.get(Movie,id)
        original_video.is_active = False
        original_video.date_last_changed = datetime.utcnow()
        session.commit()
    # Return to videos list page after user saved new video
    response = RedirectResponse(url='/get_form_list_data', status_code=302)
    return response

# endregion

#root folder
@app.get("/", response_class= HTMLResponse)
async def home():
    return '''<h1> Home Page </h1>
    <div>
    <a href= http://127.0.0.1:8000/docs>documentation</a>
    <p>
    <a href= http://127.0.0.1:8000/get_form_list_data> list of movies </a>
    </p>
    </div>'''
    pass


# get movies_with_ratings
@app.get("/movies", response_model = List[MoviesAndRating])
async def get_movies_with_rating(skip: int = 0, limit: int = 10):
    """ get all movies with a rating value if exists
    :param :\n
    1) skip: it allows to skip the items before this number
    2) limit: max number of items to fetch starting from skip (skip + limit) """
    with Session(engine) as session:
        statement = select(Movies.id, Movies.tconst,Movies.primaryTitle,Movies.startYear,Movies.runtimeMinutes,Movies.genres, Ratings.averageRating).join(Ratings,Movies.tconst==Ratings.tconst, isouter=True)
        results = session.exec(statement).all()[skip:skip+limit]
    return results


# get movies_with_ratings
@app.get("/movies_and_ratings/filter", response_model = List[MoviesAndRating])
async def get_movies_by_filters(genre:str = None, rating_get: float = None, rating_let = None,sort = None):
    """ get all movies, filter or/and sort the results

        :param : \n
            1) genre (eg. romance, adventure ... )
            2) rating_get : greater or equal than
            3) rating_let : lower or equal than
            4) sort: column by which sort the results
        
    """
    args = [genre, rating_get, rating_let]
    with Session(engine) as session:
        if list(filter(None,args)):
            rating_list = list(filter(None,[rating_get, rating_let]))
            statement = select(Movies.id,Movies.tconst,Movies.primaryTitle,Movies.startYear,Movies.runtimeMinutes,Movies.genres, Ratings.averageRating).join(Ratings,Movies.tconst==Ratings.tconst, isouter=True)
            if len(rating_list)==1:
                if rating_get is not None:
                    print("grater than")
                    rating = rating_get
                    statement = statement.where(Ratings.averageRating>=rating)
                    #statement = select(Movies.tconst,Movies.primaryTitle,Movies.startYear,Movies.runtimeMinutes,Movies.genres, Ratings.averageRating).where(Movies.tconst==Ratings.tconst).where(Movies.genres.contains(genre))
                    if genre:
                        statement = statement.where(Movies.genres.ilike(genre))
                elif rating_let is not None:
                    print("lower than")
                    rating = rating_let
                    statement = statement.where(Ratings.averageRating<=rating)

                    if genre:
                        statement = statement.where(Movies.genres.ilike(genre))
            elif  len(rating_list)==2:
                    print( f"gte than {rating_get} and lower than {rating_let}")
                    
                    statement = statement.where(Ratings.averageRating>=rating_get).where(Ratings.averageRating<=rating_let)

                    if genre:
                        statement = statement.where(Movies.genres.contains(genre))


            elif genre and (not rating_get) and (not rating_let):
                statement = statement.where(Movies.genres.contains(genre))


            if sort:
                print(f"sorting by: {sort}")

                statement = statement.order_by(sort)
            try:
                results = session.exec(statement).all() 
            except:
                raise HTTPException(status_code = 500,
                    detail = "error raised : check column name")

        else:
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,
                detail = "one among genre or rating_get or rating_let is required") 
    return results

# get single movie
@app.get("/movies/{id}")
async def get_single_movie(id:int):
    """
    get single movie by id
    :param: id
    """
    with Session(engine) as session:
        movie = session.get(Movies, id)
        # rteurn error if no such category
        if not movie:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
            detail = f"movie with id {tconst} not found")
    return movie
    
# create movie
@app.post("/movies")
async def post_movie(movie: Movies):
    """ 
    post a new movie and add it to movies table
    """
    new_item = Movies(id = movie.id, tconst = movie.tconst, titleType = movie.titleType, primaryTitle = movie.primaryTitle,startYear= movie.startYear, runtimeMinutes= movie.runtimeMinutes,
            genres = movie.genres)
    print(new_item)
    with Session(engine) as session:
        statement = select(Movies).where(Movies.id==movie.id)
        if session.exec(statement).one_or_none():
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,
            detail = "movie already exists")
        session.add(new_item)
        session.commit()
        session.refresh(new_item)
    return new_item

# create ratings
@app.post("/ratings")
async def post_rating(rating: Ratings):
    """ 
    post a new ratingand add it to rating table
    """
    new_item = Ratings(tconst = rating.tconst, averageRating=rating.averageRating, numVotes = rating.numVotes)
    print(new_item)
    with Session(engine) as session:
        statement = select(Ratings).where(Ratings.tconst==rating.tconst)
        if session.exec(statement).one_or_none():
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,
            detail = f"item {rating.tconst} already exists")
        session.add(new_item)
        session.commit()
        session.refresh(new_item)
    return new_item


# update movie
@app.put("/movies", response_model = Movies)
async def update_movie(updated_item: Movies, id: int):
    """ update movie record """
    with Session(engine) as session:
        original_item = session.get(Movies, id)
        # Get dictionary so we can loop through fields
        item_dict = updated_item.dict(exclude_unset=True)
        print(item_dict)
        # Loop is an alternative to doing each field on a separate line
        for key,value in item_dict.items():
            setattr(original_item, key,value)
        # Loop doesn't do date last changed, so we do that here
        # original_movie.date_last_changed = datetime.utcnow()
        session.commit()
        session.refresh(original_item)
    return original_item


# delete id
@app.delete("/movies/{id}")
async def delete_item(id:int):
    """ delete movie by id"""
    with Session(engine) as session:
        current_item = session.get(Movies, id)
        session.delete(current_item)
        session.commit()
    return {f"Deleted: {id}"}
    
# region validators

async def is_tconst(tconst:str):
    
    with Session(engine) as session:
        print(session.get(Movies,tconst))
        if not session.get(Movies,tconst):
            return False
    return True

# endregion

# for debugging
if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=8000)
