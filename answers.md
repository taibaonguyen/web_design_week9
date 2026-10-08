# Week 9 Lab Answers

**❓ Question 1. For each of the four statements, which constraint blocked it (PRIMARY KEY, UNIQUE, NOT NULL, FOREIGN KEY) and why?**
1. `INSERT INTO team (name, headquarters) VALUES ('Avengers', 'Los Angeles');` -> Blocked by **UNIQUE** constraint on `team.name`, because 'Avengers' already exists.
2. `INSERT INTO hero (name, team_id) VALUES ('Ghost', 99);` -> Blocked by **FOREIGN KEY** constraint on `hero.team_id`, because team with id 99 does not exist in the `team` table.
3. `INSERT INTO hero (age) VALUES (30);` -> Blocked by **NOT NULL** constraint on `hero.name`, because we did not provide a name.
4. `DELETE FROM team WHERE id = 1;` -> Blocked by **FOREIGN KEY** constraint, because there are heroes in the `hero` table referencing `team_id = 1`.

**❓ Question 2. The relationship team → hero is one-to-many. Why is the foreign key on hero and not on team?**
Because a hero belongs to one team (so it can have a single `team_id` column), but a team can have many heroes. If the foreign key were on `team`, a team could only reference one hero. To have multiple heroes, we would need multiple columns or rows which breaks normalization. Putting the FK on the "many" side allows an unlimited number of heroes to reference the same team.

**❓ Question 3. Heroes can go on many missions and a mission has many heroes (many-to-many). Sketch the tables you need (names, columns, PK, FK). Hint: you need a link table.**
- `hero`: `id` (PK), `name`, `age`, `team_id` (FK)
- `mission`: `id` (PK), `title`
- `heromissionlink`: `hero_id` (FK), `mission_id` (FK), and the composite PK is (`hero_id`, `mission_id`).

**❓ Question 4. Why read the URL from an environment variable instead of writing it in database.py? Give two reasons.**
1. **Security**: Hardcoding credentials (like passwords) in source code can expose them when the code is committed to a repository.
2. **Portability**: Different environments (development, testing, production) need different database URLs. Using environment variables allows you to change the URL without changing the code.

**❓ Question 5. Why is id typed int | None with default=None, when every row in the database has an id?**
Before the object is inserted into the database, its `id` is not yet known because the database itself generates it. Thus, it needs to be `None` temporarily in the Python object until it gets saved.

**❓ Question 6. Which attributes of Hero become columns, and which one does not? What is back_populates for?**
- Columns: `id`, `name`, `age`, `secret_name`, `team_id`.
- Non-column: `team` (the relationship attribute) does not become a database column.
- `back_populates` tells SQLModel/SQLAlchemy to populate this relationship automatically based on the corresponding relationship defined on the other side (e.g., `Team.heroes`).

**❓ Question 7. Compare the CREATE TABLE hero printed by SQLAlchemy with the one you wrote by hand in Part 1. List the differences (types, NOT NULL, indexes, constraints).**
- **Types**: String might not have explicit lengths.
- **NOT NULL**: SQLModel makes optional fields nullable, required fields `NOT NULL`.
- **Indexes**: SQLAlchemy creates explicit indexes like `CREATE INDEX ix_hero_name ON hero (name)`.
- **Constraints**: SQLAlchemy might explicitly name the foreign key constraint.

**❓ Question 8. Stop and restart the server. Is CREATE TABLE printed again? Why? What does create_all do when a table already exists?**
No, it is not printed again. `create_all` checks if tables exist in the database first. It only creates tables that don't exist yet, leaving existing tables untouched.

**❓ Question 9. create_all only knows about models that have been imported. Which line in main.py makes sure Hero and Team are registered?**
The import line `from app.models import Hero, Team` (or `from app.models import ...`) in `main.py` registers the models.

**❓ Question 10. Comment out session.commit() in create_hero and create a hero. What does the response look like, and is the row in the database (SELECT * FROM hero;)? Put the line back. What does add() do on its own, and why do we need refresh()?**
- The response will likely show an `id` of `null` and the row will **not** be in the database.
- `add()` simply adds the object to the session's staging area (pending state) but does not execute the INSERT query.
- `refresh()` fetches the latest state (like the auto-generated `id`) from the database back into the Python object.

**❓ Question 11. Which SQL statement does echo=True print for PATCH with body {"age": 17}? Does it update every column or only age? Why?**
It prints an `UPDATE` statement that updates **only** the `age` column. This is because we use `exclude_unset=True` when dumping the incoming data, which means only fields actually provided by the client are passed to `sqlmodel_update()`.

**❓ Question 12. Look at the JSON returned by GET /heroes/{id}. Is secret_name there? Which line of code is responsible?**
No, `secret_name` is not in the JSON. The line `response_model=HeroPublic` in the endpoint decorator is responsible, because the `HeroPublic` model excludes the `secret_name` field.

**❓ Question 13. Call GET /heroes?min_age=18&team_id=1 and copy the SELECT printed by echo=True. Where do the values 18 and 1 appear? Why is this safe against SQL injection?**
The values appear at the end of the log output as parameters (e.g., passed as a tuple/dictionary), but in the query itself, they are represented by placeholders like `%(age_1)s` or `$1`. This is safe because the database driver treats them strictly as data values, neutralizing any potentially malicious SQL syntax.

**❓ Question 14. Why filter in the database instead of [h for h in session.exec(select(Hero)).all() if h.age >= 18]?**
Filtering in Python (the list comprehension) would fetch *every single row* from the database into memory first, which is terribly slow and consumes too much memory for large datasets. Filtering in the database using `where()` only retrieves and transmits the rows that match the condition.

**❓ Question 15. On restart, create_all did create mission and heromissionlink. In Part 4 it did nothing for hero. What is the rule?**
The rule is that `create_all` safely ignores tables that already exist. Since `mission` and `heromissionlink` were newly added to our models and didn't exist in the database yet, they were created. `hero` already existed, so it was skipped.

**❓ Question 16. You never set team_id in the seed script. Read the echo=True output: in which order were the INSERTs executed, and how did hero.team_id get its value?**
The `INSERT` into `team` ran first. SQLAlchemy automatically fetched the generated team `id`, and assigned it to `hero.team_id` before running the `INSERT` into `hero`. This happens because we assigned the object relationships directly (e.g., `team.heroes.append(hero)`).

**❓ Question 17. Is there a power column? Now call GET /heroes. What happens and why? Why is "drop all tables and run create_all again" not an acceptable fix in production?**
No, there is no `power` column because `create_all` doesn't alter existing tables. Calling `GET /heroes` causes a 500 error because the ORM expects a `power` column that doesn't exist. Dropping all tables is unacceptable in production because it would destroy all existing user data!

**❓ Question 18. Copy the bodies of upgrade() and downgrade(). What does each one do?**
- `upgrade()`: Adds the new column. Example: `op.add_column('hero', sa.Column('power', sqlmodel.sql.sqltypes.AutoString(), nullable=True))`
- `downgrade()`: Removes the column. Example: `op.drop_column('hero', 'power')`

**❓ Question 19. Where does Alembic store "which revision this database is at"? (Hint: \dt.) Why should the migrations/ folder be committed to Git?**
Alembic stores the current revision in a special table called `alembic_version`. The `migrations/` folder must be committed to Git so that all developers and deployment servers share the exact same sequence of database changes.

**❓ Question 20. Rename secret_name to alias in the model and run revision --autogenerate (do not apply it). What did Alembic generate? Why is that dangerous for existing data, and how would you fix the script? Afterwards, delete that revision file and undo the rename.**
Alembic generated a script that drops `secret_name` and adds a new `alias` column (`op.drop_column('hero', 'secret_name')` followed by `op.add_column('hero', sa.Column('alias', ...))`). This is dangerous because dropping the column destroys all existing `secret_name` data! To fix it, you should manually edit the migration to use `op.alter_column('hero', 'secret_name', new_column_name='alias')`.
