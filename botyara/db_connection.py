import sqlalchemy as db

from parsing import get_vacancies

vacancies_array = get_vacancies("доставка", 10, 1)

engine = db.create_engine('postgresql://postgres:xm6idbip@localhost/postgres', echo=True)
conn = engine.connect()
metadata = db.MetaData()

vacancies = db.Table('vacancies', metadata,
                     db.Column('id', db.Integer, primary_key=True),
                     db.Column('title', db.Text),
                     db.Column('experience', db.Text),
                     db.Column('salary', db.Text),
                     db.Column('city', db.Text),
                     db.Column('subway', db.Text),
                     db.Column('company', db.Text),
                     db.Column('link', db.Text))

metadata.create_all(engine)

vacancies_query = vacancies.insert().values(vacancies_array)

# for i in reversed(metadata.sorted_tables):
#     engine.execute(i.delete())

conn.execute(vacancies_query)
