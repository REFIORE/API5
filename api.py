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


def get_head_hunter_vacancies(popular_languages):
    language_statistic = {}

    for language in popular_languages:
        vacansy_salaries = []
        moscow = 1
        period = 30
        for page in count(0):
            hh_url = 'https://api.hh.ru/vacancies'
            params = {'text': language, 'area': moscow, 'period': period, 'page': page}
            response = requests.get(hh_url, params=params)
            response.raise_for_status()

            vacansies = response.json()
            found_vacansy = vacansies['found']
            vacansies = vacansies['items']
            pages = vacansies['pages']
            if page >= pages - 1:
                break
            for vacansy in vacansies:
                salary = vacansy.get('salary')
                if salary and salary['currency'] == 'RUR':
                    predicted_salary = predict_rub_salary(vacansy['salary'].get('from'), vacansy['salary'].get('to'))
                    if predicted_salary:
                        vacansy_salaries.append(predicted_salary)
        average_salary = None
        if vacansy_salaries:
            average_salary = int(sum(vacansy_salaries) / len(vacansy_salaries))
        language_statistic[language] = {
            "vacancies_found": found_vacansy,
            "vacancies_processed": len(vacansy_salaries),
            "average_salary": average_salary
        }
    return language_statistic


def predict_rub_salary_sj(popular_languages, sj_token):
    language_statistic_sj = {}
    for language in popular_languages:
        salaries_vacansy_sj = []
        for page in count(0):
            sj_url = 'https://api.superjob.ru/2.0/vacancies/'
            params = {'town': 'Moscow', 'keyword': language, 'page': page}
            headers = {
                'X-Api-App-Id': sj_token
            }
            response = requests.get(sj_url, headers=headers, params=params)
            response.raise_for_status()
            
            vacansies = response.json()
            super_job_vacancies = vacansies['objects']
            total_vacansy = vacansies['total']
            if not super_job_vacancies:
                break
            for vacansy in super_job_vacancies:
                predicted_salary_sj = predict_rub_salary(vacansy['payment_from'], vacansy['payment_to'])
                if predicted_salary_sj:
                    salaries_vacansy_sj.append(predicted_salary_sj)
            average_salary = None
            if salaries_vacansy_sj:
                average_salary = int(sum(salaries_vacansy_sj) / len(salaries_vacansy_sj))
        language_statistic_sj[language] = {
            "vacancies_found": total_vacansy,
            "vacancies_processed": len(salaries_vacansy_sj),
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
    # print(table_language(get_head_hunter_vacancies(popular_languages)))
    print(table_language(predict_rub_salary_sj(popular_languages, sj_token)))


if __name__ == "__main__":
    main()
