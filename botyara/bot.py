import telebot
import sqlalchemy as db

from parsing import get_vacancies
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import exists, delete, select
from classes.User import User
from classes.Base import Base

bot = telebot.TeleBot('7230534726:AAE6PjCMj71A_D98hnG1ptBY0H4bhtoQ2Fc')

request = []

@bot.message_handler(commands=['start'])
def start(message):

    # session.delete(session.query(User).filter(User.username == 'BushkovEvgeniy').one())
    # session.commit()

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! '
                                      'С моей помощью ты можешь найти подходящую вакансию всего лишь в пару кликов. '
                                      'Кем ты хочешь работать?')
    bot.register_next_step_handler(message, get_vacancy_title)


def get_vacancy_title(message):
    vacancy_title = message.text
    bot.send_message(message.chat.id, 'Отлично, напиши, сколько вариантов предложить')
    request.append(vacancy_title)
    bot.register_next_step_handler(message, get_vacancy_number)


def get_vacancy_number(message):
    bot.send_message(message.chat.id, 'Подожди пару секунд')

    engine = db.create_engine('postgresql://postgres:xm6idbip@localhost/bot', echo=True)
    conn = engine.connect()
    metadata = db.MetaData()

    users = db.Table('users', metadata,
                     db.Column('tg_id', db.Integer, primary_key=True),
                     db.Column('username', db.String))
    Base.metadata.create_all(engine)

    with Session(autoflush = False, bind = engine) as session:

        vacancies = get_vacancies(request[0], int(message.text), 1)

        if not session.query(exists().where(User.tg_id == message.from_user.id)).scalar():
            # user = users.insert().values([
            #     message.from_user.id,
            #     message.from_user.username])
            user = User(
                tg_id = message.from_user.id,
                username = message.from_user.username
            )
            user.vacancies = vacancies
        else:
            user = session.query(User).filter_by(tg_id = message.from_user.id).one()
            # query = session.query(User.tg_id)
            # result = query.all()
            # for row in result:
            #     if row == message.from_user.id:
            #         user = row
            #         break
            user.vacancies.extend(vacancies)

        session.add(user)
        session.commit()
        # session.expunge_all()

        for vacancy in vacancies:

            bot.send_message(message.chat.id,
                             f'{vacancy.title}. '
                             f'{vacancy.experience}. '
                             f'Зарплата: {vacancy.salary}. '
                             f'Город: {vacancy.city}. '
                             f'Станция метро: {vacancy.subway}. '
                             f'Компания: {vacancy.company}. '
                             f'Перейдите по данной ссылке, чтобы узнать подробности: {vacancy.link}')

        bot.send_message(message.chat.id, 'Поиск закончен. Введи команду "/start", чтобы начать заново')
        bot.register_next_step_handler(message, start)


bot.polling(none_stop=True)
