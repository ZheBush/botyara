import telebot
import sqlalchemy as db

from parsing import get_vacancies

bot = telebot.TeleBot('7230534726:AAE6PjCMj71A_D98hnG1ptBY0H4bhtoQ2Fc')

request = []
@bot.message_handler(commands=['start'])
def start(message):

    engine = db.create_engine('postgresql://postgres:xm6idbip@localhost/users_test', echo=True)
    conn = engine.connect()
    metadata = db.MetaData()

    users = db.Table('users_test', metadata,
                     db.Column('tg_id', db.Integer, primary_key = True),
                     db.Column('username', db.Text))
    metadata.create_all(engine)

    new_user = users.insert().values([
        message.from_user.id,
        message.from_user.username])

    conn.execute(new_user)

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

    for i in range(0, len(vacancies)):
        title = vacancies[i]['title']
        exp = vacancies[i]['experience']
        salary = vacancies[i]['salary']
        city = vacancies[i]['city']
        subway = vacancies[i]['subway']
        company = vacancies[i]['company']
        link = vacancies[i]['link']
        bot.send_message(message.chat.id,
                         f'{title}. '
                         f'{exp}. '
                         f'Зарплата: {salary}. '
                         f'Город: {city}. '
                         f'Станция метро: {subway}. '
                         f'Компания: {company}. '
                         f'Перейдите по данной ссылке, чтобы узнать подробности: {link}')

    bot.send_message(message.chat.id, 'Поиск закончен. Введи коман  ду "/start", чтобы начать заново')
    bot.register_next_step_handler(message, start)


bot.polling(none_stop=True)
