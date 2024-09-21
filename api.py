from itertools import count
from terminaltables import AsciiTable
from dotenv import load_dotenv
import os
import requests


def predict_rub_salary(salary_from=None, salary_to=None):
    if salary_from and salary_to:
        average_salary = int((salary_from + salary_to) / 2)
    elif salary_from:
        average_salary = salary_from * 1.2
    elif salary_to:
        average_salary = salary_to * 0.8
    else:
        average_salary = None
    return average_salary


def head_hunter(popular_languages):
    language_statistic = {}

    for language in popular_languages:
        processis_vacansy = 0
        salaries_vacansy = []
        for page in count(0):
            hh_url = 'https://api.hh.ru/vacancies'
            params = {'text': language, 'area': 1, 'period': 30, 'page': page}
            response = requests.get(hh_url, params=params)
            response.raise_for_status()

            found_vacansy = response.json()['found']
            vacansies = response.json()['items']
            pages = response.json()['pages']
            if page >= pages - 1:
                break
            for vacansy in vacansies:
                salary = vacansy.get('salary')
                if salary and salary['currency'] == 'RUR':
                    predicted_salary = predict_rub_salary(vacansy['salary'].get('from'), vacansy['salary'].get('to'))
                    if predicted_salary:
                        processis_vacansy += 1
                        salaries_vacansy.append(predicted_salary)
        average_salary = None
        if salaries_vacansy:
            average_salary = int(sum(salaries_vacansy) / len(salaries_vacansy))
        language_statistic[language] = {
            "vacancies_found": found_vacansy,
            "vacancies_processed": processis_vacansy,
            "average_salary": average_salary
        }
    return language_statistic


def predict_rub_salary_sj(popular_languages, sj_token):
    language_statistic_sj = {}
    for language in popular_languages:
        processis_vacansy_sj = 0
        salaries_vacansy_sj = []
        sj_url = 'https://api.superjob.ru/2.0/vacancies/'
        params = {'town': 'Moscow', 'keyword': language}
        headers = {
            'X-Api-App-Id': sj_token
        }
        response = requests.get(sj_url, headers=headers, params=params)
        response.raise_for_status()
        super_job_vacansy = response.json()['objects']
        total_vacansy = response.json()['total']
        for vacansy in super_job_vacansy:
            predicted_salary_sj = predict_rub_salary(vacansy['payment_from'], vacansy['payment_to'])
            if predicted_salary_sj:
                processis_vacansy_sj += 1
                salaries_vacansy_sj.append(predicted_salary_sj)
            average_salary = None
            if salaries_vacansy_sj:
                average_salary = int(sum(salaries_vacansy_sj) / len(salaries_vacansy_sj))
            language_statistic_sj[language] = {
                "vacancies_found": total_vacansy,
                "vacancies_processed": processis_vacansy_sj,
                "average_salary": average_salary
            }
    return language_statistic_sj


def table_language(statistic):
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],
    ]
    for language, vacansy in statistic.items():
        table_data.append([language, vacansy["vacancies_found"], vacansy["vacancies_processed"], vacansy["average_salary"]])
    table = AsciiTable(table_data)
    return table.table


def main():
    load_dotenv()
    sj_token = os.environ['SJ_TOKEN']
    popular_languages = [
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'C',
        'Shell',
        'TypeScript',
    ]
    print(table_language(head_hunter(popular_languages)))
    print(table_language(predict_rub_salary_sj(popular_languages, sj_token)))


if __name__ == "__main__":
    main()
