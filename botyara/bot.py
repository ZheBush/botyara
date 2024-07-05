import telebot
import sqlalchemy as db
import codecs
import json

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
request = {
    'title': '',
    'number': 3,
    'country': 0,
    'area': 0
}
filters = {
    'min_salary': 1,
}


@bot.message_handler(content_types = ['text'])
def start(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! '
                                      'С моей помощью ты можешь найти подходящую вакансию всего лишь в пару кликов. '
                                      'Кем ты хочешь работать?')
    bot.register_next_step_handler(message, get_vacancy_title)


def get_vacancy_title(message):
    vacancy_title = message.text
    request['title'] = vacancy_title
    bot.send_message(message.chat.id, 'Введи минимальный размер зарплаты')
    bot.register_next_step_handler(message, get_min_salary)


def get_min_salary(message):
    if message.text.isdigit():
        min_salary = message.text
    else:
        min_salary = 1
    filters['min_salary'] = min_salary
    bot.send_message(message.chat.id, 'В какой стране найти работу?')
    bot.register_next_step_handler(message, get_vacancy_country)


def get_vacancy_country(message):
    file = codecs.open('./docs/areas.json', 'r', 'utf_8_sig')
    data = json.loads(file.read())
    country = message.text
    for c in range(0, len(data)):
        if data[c]['name'] == country:
            request['country'] = c
            break
    file.close()
    bot.send_message(message.chat.id, 'В каком населённом пункте из выбранной страны вы хотите работать?')
    bot.register_next_step_handler(message, get_vacancy_locality)


def get_vacancy_locality(message):
    file = codecs.open('./docs/areas.json', 'r', 'utf_8_sig')
    data = json.loads(file.read())
    locality = message.text
    for i in data[request['country']]['areas']:
        for j in i['areas']:
            if locality == j['name']:
                request['area'] = j['id']
                break
    bot.send_message(message.chat.id, 'Сколько вариантов предложить?')
    bot.register_next_step_handler(message, parsing)


def parsing(message):
    number_of_vacancies = int(message.text)

    with Session(autoflush=False, bind=engine) as session:

        vacancies = get_vacancies(request['title'], number_of_vacancies, request['area'])

        for i in vacancies:
            if not (i.salary.isdigit()):
                min_salary = ''
                for j in i.salary:
                    if j.isdigit():
                        min_salary += j
                if int(min_salary) < int(filters['min_salary']):
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
                             f'Компания: {vacancy.company}. '
                             f'Перейдите по данной ссылке, чтобы узнать подробности: {vacancy.link}')

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        restart_button = types.KeyboardButton('Начать сначала')
        stop_button = types.KeyboardButton('Закончить работу')
        markup.add(restart_button, stop_button)

        bot.send_message(message.chat.id, 'Поиск закончен', reply_markup=markup)
        bot.register_next_step_handler(message, end)


def end(message):
    if message.text == 'Начать сначала':
        start(message)
    elif message.text == 'Закончить работу':
        stop(message)


def stop(message):
    bot.send_message(message.chat.id, 'Буду ждать вашего возвращения')

    with Session(autoflush=False, bind=engine) as session:
        session.query(Vacancy).filter_by(user_tg_id=message.chat.id).delete(synchronize_session=False)
        session.query(User).filter_by(tg_id=message.chat.id).delete(synchronize_session=False)

        session.commit()


bot.polling(none_stop=True)
