import os
import sys
import time

import requests

FN_USER_AGENTS = r'Data/user_agents.txt'  # путь к файлу со списком перебираемых агентов

BASE_URL = 'https://pentest.blackbox.team:444/index.php'
START_VERSION = 1  # начало перебора
END_VERSION = 150  # конец перебора

VALID_ANSWER = 'GOOD OK'  # валидный ответ от сервера
NOVALID_ANSWER = 'ACCESS DENIED'  # не валидный ответ от сервера
FN_VALID_RESULT = 'Data/valid_agents.txt'  # куда сохранять найденные валидные агенты
FN_NOVALID_RESULT = 'Data/novalid_agents.txt'  # куда сохранять найденные НЕвалидные агенты
FN_ERROR_RESULT = 'Data/errors_agents.txt'  # куда сохранять агенты с ошибками в запросе

IS_SHOW_RESPONSE = False  # показывать (True) или нет (False) ответ от сервера - нужно для отладки


def read_list(fn: str) -> list | None:
    try:
        with open(fn, 'r', encoding='utf-8') as file:
            my_list = [val.strip() for val in file if val and val.strip()]
        return my_list
    except Exception as e:
        print(f'Ошибка чтения файла "{fn}": {e}')


def save_to_file(fn: str, my_list: list):
    with open(fn, 'w', encoding='utf-8') as file:
        for val in my_list:
            if val:
                file.write(f'{val}\n')


def check_one_agent(my_agent: str, url: str) -> str | None:
    try:
        # возможно в headers нужно будет добавить еще какие-то параметры
        response = requests.get(url,
                                headers={
                                    "User-Agent": my_agent,
                                    "Accept": "*/*",
                                }).text
        if IS_SHOW_RESPONSE:
            print(f'{my_agent} -> {response}')
        return response
    except Exception as e:  # не известно какие ошибки могут быть в ответе, поэтому общий перехват
        print(f'Ошибка запроса: {e}')
        return None


def main():
    if not os.path.isfile(FN_USER_AGENTS):
        print(f'Не найден файл "{FN_USER_AGENTS}" со списком агентов для перебора!')
        sys.exit()
    agents = read_list(FN_USER_AGENTS)
    if not agents:
        print(f'Не удалось получить список агентов из файла "{FN_USER_AGENTS}"')
        sys.exit()

    valid_agents = []
    error_agents = []
    novalid_agents = []
    total_valids = 0
    for num, agent in enumerate(agents, start=1):  # цикл по списку агентов
        print(f'{"-" * 20}> Работаем с агентом "{agent}" [{num}/{len(agents)}]')
        for version in range(START_VERSION, END_VERSION + 1):  # цикл по версиям
            my_agent = f'{agent}/{float(version)}'
            print(f'Проверяем "{my_agent}"')

            response = check_one_agent(my_agent=my_agent, url=BASE_URL)
            if response and VALID_ANSWER in response:
                print(f'Найдено валидное значение для {my_agent}')
                valid_agents.append(my_agent)
                total_valids += 1
            elif response and NOVALID_ANSWER in response:
                novalid_agents.append(my_agent)
            else:
                error_agents.append(my_agent)
            # TODO: возможно нужна пауза для ограничения количества запросов в единицу времени к серверу: time.sleep(1)

    print(f'Количество найденных валидных агентов = {total_valids}')
    if valid_agents:
        save_to_file(fn=FN_VALID_RESULT, my_list=valid_agents)
    if novalid_agents:
        save_to_file(fn=FN_NOVALID_RESULT, my_list=novalid_agents)
    if error_agents:
        save_to_file(fn=FN_ERROR_RESULT, my_list=error_agents)


if __name__ == '__main__':
    start_time = time.perf_counter()
    main()
    print(f'Работа завершена. Затраченное время: {round(time.perf_counter() - start_time, 2)} сек')
