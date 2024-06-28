import telebot
from bs4 import BeautifulSoup
import json
import requests

bot = telebot.TeleBot('7285881707:AAGReJHIgnzuy361KAIpbsroeKqnTEXtVbw')


def get_vacancies(title, page, area):
    url = "https://hh.ru/search/vacancy"
    params = {
        "text": title,
        "area": area,
        "per_page": 10,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36",
    }

    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    heading = soup.find_all('span', class_='vacancy-name--c1Lay3KouCl7XasYakLk serp-item__title-link')
    work_exp = soup.find_all('span', attrs={
        'class': 'label--rWRLMsbliNlu_OMkM_D3 label_light-gray--naceJW1Byb6XTGCkZtUM',
        'data-qa': 'vacancy-serp__vacancy-work-experience'
    })
    salary = soup.find_all('span', class_='fake-magritte-primary-text--Hdw8FvkOzzOcoR4xXWni '
                                          'compensation-text--kTJ0_rp54B2vNeZ3CTt2 '
                                          'separate-line-on-xs--mtby5gO4J0ixtqzW38wh')

    for p in range(0, page):
        data = {
            'heading': heading[p].text,
            'work experience': work_exp[p].text,
            'salary': salary[p].text
        }
        json_obj = json.dumps(data, indent = 3, ensure_ascii=False)
        print(json_obj)


get_vacancies("backend разработчик", 3, 1)
