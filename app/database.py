import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app.db")

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_session)]