from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, status
from sqlmodel import SQLModel, select

from app.database import SessionDep, engine
from app import models
from app.models import Hero, HeroCreate, HeroPublic, HeroUpdate, Team, TeamCreate, TeamPublic, Mission, MissionCreate, MissionPublic
from sqlalchemy.exc import IntegrityError
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/heroes", response_model=HeroPublic, status_code=status.HTTP_201_CREATED)
def create_hero(hero_in: HeroCreate, session: SessionDep):
    if hero_in.team_id is not None:
        team = session.get(Team, hero_in.team_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    hero = Hero.model_validate(hero_in)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero

@app.get("/heroes", response_model=list[HeroPublic])
def list_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    min_age : int |None = None,
    team_id : int | None = None,
    name:str |None = None,
):
    statement = select(Hero)
    if min_age is not None:
        statement = statement.where(Hero.age >= min_age)
    if team_id is not None:
        statement = statement.where(Hero.team_id == team_id)
    if name is not None:
        statement = statement.where(Hero.name == name)
    heroes = session.exec(statement.order_by(Hero.id).offset(offset).limit(limit)).all()
    return heroes

@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def get_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
    return hero

@app.patch("/heroes{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero_in: HeroUpdate, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
    if hero_in.team_id is not None:
        team = session.get(Team, hero_in.team_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    
    update_data = hero_in.dict(exclude_unset=True)
    hero.sqlmodel_update(update_data)

    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero

@app.delete("/heroes/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hero(hero_id:int, session:SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return None


#6.1 Team Endpoints voi loi 409 conflict
@app.post("/teams", response_model=TeamPublic,status_code=status.HTTP_201_CREATED)
def create_team(team_in:TeamCreate, session: SessionDep):
    team = Team.model_validate(team_in)
    session.add(team)
    try:
        session.commit()
        session.refresh(team)
        return team
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='Team name already exists')
@app.get("/teams", response_model=list[TeamPublic])
def list_teams(session: SessionDep):
    return session.exec(select(Team).order_by(Team.id)).all()


# Task 6.1: Lay danh sach heroes cua team thong qua relationship
@app.get("/teams/{team_id}/heroes", response_model=list[HeroPublic])
def get_team_heroes(team_id: int, session: SessionDep):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.heroes

# 7.2. Nhiem vu moi 
@app.post("/missions", response_model=MissionPublic, status_code=status.HTTP_201_CREATED)
def create_mission(mission_in: MissionCreate, session: SessionDep):
    mission = Mission.model_validate(mission_in)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


# 2. Gan hero vao mission
@app.post("/heroes/{hero_id}/missions/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def assign_hero_to_mission(hero_id: int, mission_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    mission = session.get(Mission, mission_id)
    if not hero or not mission:
        raise HTTPException(status_code=404, detail="Hero or Mission not found")
    
    # Nếu chưa được gán thì thêm vào danh sách, tránh gán trùng
    if mission not in hero.missions:
        hero.missions.append(mission)
        session.add(hero)
        session.commit()
    return None


# 3. Lấy danh sách nhiệm vụ của 1 hero (GET /heroes/{hero_id}/missions)
@app.get("/heroes/{hero_id}/missions", response_model=list[MissionPublic])
def get_hero_missions(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero.missions
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="[IP_ADDRESS]", port=8000)
