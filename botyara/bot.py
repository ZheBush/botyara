import telebot
import sqlalchemy as db

from parsing import get_vacancies
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists, delete
from classes.User import User

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

    vacancy_number = int(message.text)
    request.append(vacancy_number)
    vacancies = get_vacancies(request[0], request[1], 1)

    engine = db.create_engine('postgresql://postgres:xm6idbip@localhost/bot', echo=True)
    conn = engine.connect()
    metadata = db.MetaData()
    get_session = sessionmaker(bind=engine)
    session = get_session()

    if not session.query(exists().where(User.tg_id == message.from_user.id)).scalar():
        users = db.Table('users', metadata,
                         db.Column('tg_id', db.Integer, primary_key=True),
                         db.Column('username', db.Text))
        metadata.create_all(engine)

        user = users.insert().values([
            message.from_user.id,
            message.from_user.username])
    else:
        user = db.select(User.tg_id == message.from_user.id)

    user.vacancies = vacancies

    conn.execute(user)
    session.commit()

    # if not session.query(exists().where(User.tg_id == message.from_user.id)).scalar():
    #     user = User(
    #         tg_id = message.from_user.id,
    #         username = message.from_user.username
    #     )
    #
    # else:
    #     user = db.select(User.tg_id == message.from_user.id)
    #     # USERS = metadata.tables['users']
    #     # user = db.select(USERS).where(USERS.c.tg_id == message.from_user.id)
    #
    # user.vacancies = vacancies
    #
    # session.add(user)
    # session.commit()

    for vacancy in range(0, len(vacancies)):

        title = vacancies[vacancy]['title']
        exp = vacancies[vacancy]['experience']
        salary = vacancies[vacancy]['salary']
        city = vacancies[vacancy]['city']
        subway = vacancies[vacancy]['subway']
        company = vacancies[vacancy]['company']
        link = vacancies[vacancy]['link']

        bot.send_message(message.chat.id,
                         f'{title}. '
                         f'{exp}. '
                         f'Зарплата: {salary}. '
                         f'Город: {city}. '
                         f'Станция метро: {subway}. '
                         f'Компания: {company}. '
                         f'Перейдите по данной ссылке, чтобы узнать подробности: {link}')

    bot.send_message(message.chat.id, 'Поиск закончен. Введи команду "/start", чтобы начать заново')
    bot.register_next_step_handler(message, start)


bot.polling(none_stop=True)
