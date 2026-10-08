from sqlmodel import Session, SQLModel, select
from app.database import engine
from app.models import Hero, Mission, Team


def seed_data():
    # 1. Dam bao bang da ton tai
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # 2. Ktra neu da co du lieu team thi dung
        existing_team = session.exec(select(Team)).first()
        if existing_team:
            print("Database already seeded. Skipping.")
            return

        # 3. Tao 2 Teams
        avengers = Team(name="Avengers", headquarters="New York")
        xmen = Team(name="X-Men", headquarters="Westchester")

        # 4. Tao 2 Missions
        sokovia = Mission(title="Battle of Sokovia")
        thanos = Mission(title="Infinity War")

        # 5. Tao it nhat 5 Heroes va gan relationship bang doi tuong
        heroes = [
            Hero(
                name="Tony",
                age=45,
                secret_name="Iron Man",
                team=avengers,
                missions=[sokovia, thanos],
            ),
            Hero(
                name="Natasha",
                age=35,
                secret_name="Black Widow",
                team=avengers,
                missions=[sokovia],
            ),
            Hero(
                name="Logan",
                age=150,
                secret_name="Wolverine",
                team=xmen,
                missions=[],
            ),
            Hero(
                name="Peter",
                age=16,
                secret_name="Spider-Man",
                team=avengers,
                missions=[thanos],
            ),
            Hero(
                name="Charles",
                age=60,
                secret_name="Professor X",
                team=xmen,
                missions=[],
            ),
        ]

        # 6. Thêm danh sách vào session và commit
        session.add_all(heroes)
        session.commit()
        print("Database seeded successfully with initial data!")


if __name__ == "__main__":
    seed_data()