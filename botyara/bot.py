import telebot
import sqlalchemy as db

from telebot import types

from parsing import get_vacancies
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import exists, delete, select
from classes.User import User
from classes.Vacancy import Vacancy
from classes.Base import Base

bot = telebot.TeleBot('7230534726:AAE6PjCMj71A_D98hnG1ptBY0H4bhtoQ2Fc')
engine = db.create_engine('postgresql://postgres:xm6idbip@localhost/bot', echo=True)
metadata = db.MetaData()
request = []
filters = []


@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! '
                                      'С моей помощью ты можешь найти подходящую вакансию всего лишь в пару кликов. ')
    get_vacancy_title(message)


def get_vacancy_title(message):
    bot.send_message(message.chat.id, 'Кем ты хочешь работать?')
    vacancy_title = message.text
    request.append(vacancy_title)
    bot.register_next_step_handler(message, get_min_salary)


def get_min_salary(message):
    bot.send_message(message.chat.id, 'Введи минимальный размер зарплаты')
    if message.text.isdigit():
        min_salary = message.text
    else:
        min_salary = 0
    filters.append(int(min_salary))
    bot.register_next_step_handler(message, get_vacancy_number)


def get_vacancy_number(message):
    bot.send_message(message.chat.id, 'Сколько вариантов предложить?')
    request.append(message.text)
    bot.register_next_step_handler(message, parsing)


def parsing(message):
    with Session(autoflush=False, bind=engine) as session:

        vacancies = get_vacancies(request[0], int(message.text), 0)

        for i in vacancies:
            if not (i.salary.isdigit()):
                min_salary = ''
                for j in i.salary:
                    if j.isdigit():
                        min_salary += j
                if int(int(min_salary)) < filters[0]:
                    vacancies.remove(i)
            elif int(i.salary) < filters[0]:
                vacancies.remove(i)

        if not session.query(exists().where(User.tg_id == message.from_user.id)).scalar():
            user = User(
                tg_id=message.from_user.id,
                username=message.from_user.username
            )
            user.vacancies = vacancies
        else:
            user = session.query(User).filter_by(tg_id=message.from_user.id).one()
            user.vacancies.extend(vacancies)

        session.add(user)
        session.commit()

        for vacancy in vacancies:
            bot.send_message(message.chat.id,
                             f'{vacancy.title}. '
                             f'{vacancy.experience}. '
                             f'Зарплата: {vacancy.salary}. '
                             f'Город: {vacancy.city}. '
                             f'Станция метро: {vacancy.subway}. '
                             f'Компания: {vacancy.company}. '
                             f'Перейдите по данной ссылке, чтобы узнать подробности: {vacancy.link}')
        end(message)


def end(message):
    bot.send_message(message.chat.id, 'Поиск закончен')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    restart_button = types.KeyboardButton('Начать сначала')
    stop_button = types.KeyboardButton('Закончить работу')
    markup.add(restart_button, stop_button)

    if message.text == 'Начать сначала':
        bot.register_next_step_handler(message, get_vacancy_title)
    elif message.text == 'Закончить работу':
        bot.register_next_step_handler(message, stop)


@bot.message_handler(commands=['stop'])
def stop(message):
    bot.send_message(message.chat.id, 'Буду ждать вашего возвращения')

    with Session(autoflush=False, bind=engine) as session:
        session.query(Vacancy).filter_by(user_tg_id=message.chat.id).delete(synchronize_session=False)
        session.query(User).filter_by(tg_id=message.chat.id).delete(synchronize_session=False)

        session.commit()


bot.polling(none_stop=True)
