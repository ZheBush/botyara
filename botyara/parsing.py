import requests

from bs4 import BeautifulSoup
from classes.Vacancy import Vacancy


def get_vacancies(title, number, area):
    url = "https://hh.ru/search/vacancy"
    params = {
        "text": title,
        "area": area,
        "per_page": 1,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36",
    }

    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find_all('span', class_='vacancy-name--c1Lay3KouCl7XasYakLk serp-item__title-link')
    work_exp = soup.find_all('span', attrs={
        'class': 'label--rWRLMsbliNlu_OMkM_D3 label_light-gray--naceJW1Byb6XTGCkZtUM',
        'data-qa': 'vacancy-serp__vacancy-work-experience'
    })
    salary = soup.find_all('span', class_='fake-magritte-primary-text--Hdw8FvkOzzOcoR4xXWni '
                                          'compensation-text--kTJ0_rp54B2vNeZ3CTt2 '
                                          'separate-line-on-xs--mtby5gO4J0ixtqzW38wh')
    city = soup.find_all('span', attrs={
        'class': 'bloko-text',
        'data-qa': 'vacancy-serp__vacancy-address'
    })
    company = soup.find_all('span', class_='company-info-text--vgvZouLtf8jwBmaD1xgp')
    link = soup.find_all('a', attrs={
        'class': 'bloko-link',
        'target': '_blank'
    }, href=True)

    array = []

    for p in range(0, number):
        vacancy = Vacancy(
            title=title[p].text.replace(' ', ' ').replace(' ', ' '),
            experience=work_exp[p].text.replace(' ', ' ').replace(' ', ' '),
            salary=salary[p].text.replace(' ', ' ').replace(' ', ' '),
            city=city[p].text.replace(' ', ' ').replace(' ', ' '),
            company=company[p].text.replace(' ', ' ').replace(' ', ' '),
            link=link[p]['href']
        )
        array.append(vacancy)

    return array


get_vacancies('доставка', 3, 1)
