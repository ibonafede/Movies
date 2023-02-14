from typing import Optional

from sqlmodel import Field, SQLModel

class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    tconst: Optional[int] = Field(primary_key=True,default=None)

class Ratings(SQLModel, table=True):
    tconst: str = Field(primary_key=True,default=None)
    averageRating: float
    numVotes: int = Field(nullable=True)
    

class Movies(BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tconst: str = Field(default=None, foreign_key="ratings.tconst")
    titleType: Optional[str]
    primaryTitle: str = Field(min_length = 1, max_length = 150, index=True)
    startYear: Optional[int] 
    runtimeMinutes: Optional[float]
    genres:Optional[str]= Field(nullable=True)

# CategorizedVideos class is just for reading from joined tables
class MoviesAndRating(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    tconst: str = Field(default=None, primary_key=True)
    primaryTitle: str = Field(min_length = 1, max_length = 150, index=True)
    startYear: Optional[int] 
    runtimeMinutes: Optional[float]
    genres:Optional[str]= Field(nullable=True)
    averageRating: float = None