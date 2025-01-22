import os
import random
import time
import datetime
import configparser
import uuid
import pyperclip
import platform
import ctypes
import cx_Oracle  # pip install cx-Oracle
import logging
from plsql_queries import CREATE_CLIENT_QUERY, CREATE_AGREEMENT_QUERY  # Импортируем запросы
import list_of_dict  # список фамилий, имен, отчеств

# Версия программы
program_version = 1.4

config = configparser.ConfigParser()
config.read(r'connection_parameters.ini')

id_group_card = config['AGREE_PARAM']['id_group_card']
AgreeType = config['AGREE_PARAM']['AgreeType']

data = configparser.ConfigParser()
data.read(r'data\data.data')

log_file_counter = data['SYSTEM_DATA']['log_file_counter']
log_file_date = data['SYSTEM_DATA']['log_file_date']
last_clid = data['SYSTEM_DATA']['last_clid']
fio_last_clid = data['SYSTEM_DATA']['fio_last_clid']

real_date = time.strftime('%Y%m%d')
computer_name = platform.node()

ctypes.windll.kernel32.SetConsoleTitleW(
    f"Создание клиентов и договоров на {config['CONN_PARAM']['schemaName']} @ {config['CONN_PARAM']['serverName']}")

if log_file_date == real_date:
    log_file_counter = str(int(log_file_counter) + 1)
else:
    log_file_counter = str(1)
    data.set('SYSTEM_DATA', 'log_file_date', f'{real_date}')

data.set('SYSTEM_DATA', 'log_file_counter', f'{log_file_counter}')
with open('data/data.data', 'w') as configfile:
    data.write(configfile)

# Определение имени лог-файла
log_file_name = f'{real_date}_{computer_name}_{log_file_counter.rjust(5, "0")}.txt'

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"log/{log_file_name}"),
        logging.StreamHandler()
    ]
)

sp10 = " " * 11

def execut_query_to_db(sql: str):
    """
    Выполняет SQL-запрос и возвращает результат.
    :param sql: строка, содержащая запрос
    :return: список строк
    """
    cursor = connection.cursor()
    cursor.execute(sql)
    fetch = cursor.fetchall()
    cursor.close()
    return fetch

def execut_query_to_db_no_fetch(sql):
    """
    Выполняет SQL-запрос без возврата результата.
    :param sql: строка, содержащая запрос
    :return: None
    """
    cursor = connection.cursor()
    cursor.execute(sql)
    cursor.close()

def unique_inn() -> int:
    """
    Функция возвращает уникальное значение ИНН.
    :return: int
    """
    while True:
        inn = random.randint(111111111111, 999999999999)
        sql = f'''
            select N31CLID from n31 where n31cinn = '{inn}'
            '''
        result = execut_query_to_db(sql)
        if not result:
            return inn

def unique_passport_data() -> list:
    """
    Функция возвращает уникальное значение серии и номера паспорта.
    :return: list
    """
    while True:
        pass_ser = random.randint(1111, 9999)
        pass_num = random.randint(111111, 999999)
        sql = f'''
                select N37CLID from n37 where N37DCTP = 1 and N37PSER = '{pass_ser}' and N37PNUM = '{pass_num}'
            '''
        result = execut_query_to_db(sql)
        if not result:
            return [pass_ser, pass_num]

def client_add() -> int:
    """
    Функция создает нового клиента с использованием сообщения MsgClientAddRq и
    возвращает CLID созданного клиента.
    :return: int
    """
    logging.info('Создается новый клиент...')

    guid = uuid.uuid4()
    NAMF = random.choice(list_of_dict.last_name_list)
    NAMI = random.choice(list_of_dict.list_of_names)
    NAMO = random.choice(list_of_dict.list_of_patronymic)

    pasportData = unique_passport_data()
    PNUM = pasportData[1]
    PSER = pasportData[0]

    BITH = f'{datetime.date(random.randint(1980, 2001), random.randint(1, 12), random.randint(1, 28))}'
    CINN = unique_inn()

    TVAL = str(random.randint(0, 999_99_99)).rjust(7, "0")

    plSql = CREATE_CLIENT_QUERY.format(guid=guid, NAMF=NAMF, NAMI=NAMI, NAMO=NAMO, BITH=BITH, CINN=CINN, PNUM=PNUM, PSER=PSER, TVAL=TVAL, computer_name=computer_name)
    execut_query_to_db_no_fetch(plSql)

    sql = f'''
        select N37CLID, N31NAMF, N31NAMI, N31NAMO from n37
        join n31 on N37CLID = N31CLID
        where N37DCTP = 1 and N37PSER = '{PSER}' and N37PNUM = '{PNUM}'
            '''
    try:
        result = execut_query_to_db(sql)
        clid = result[0][0]
        logging.info(f'Создан клиент - {result[0][1]} {result[0][2]} {result[0][3]}')
        logging.info(f'Паспорт гражданина РФ: серия - {PSER} номер - {PNUM}')
        logging.info(f'CLID = {clid}')

        global last_clid
        global fio_last_clid
        last_clid = clid
        fio_last_clid = return_fio_on_clid(last_clid)
        data.set('SYSTEM_DATA', 'last_clid', f'{last_clid}')
        data.set('SYSTEM_DATA', 'fio_last_clid', f'{fio_last_clid}')
        with open('data/data.data', 'w') as configfile:
            data.write(configfile)

        return clid
    except Exception as err:
        logging.error(f'Произошла ошибка, смотрите логи, пробуйте снова. guid сообщения - {guid}. Ошибка: {err}')

def agree_add(last_clid) -> list:
    """
    Создается договор для указанного клиента.
    :param last_clid: CLID
    :return list: список [AGID, P002]
    """
    logging.info('Создается новый договор...')
    guid = uuid.uuid4()
    pl_sql = CREATE_AGREEMENT_QUERY.format(guid=guid, last_clid=last_clid, AgreeType=AgreeType, id_group_card=id_group_card)
    execut_query_to_db_no_fetch(pl_sql)

    sql = f'''
        select N02DCID as AGID, B31P002 as P002 from i24
        join n02 on N02OPID = I24OPID
        left join b31 on B31AGID = N02DCID
        where I24RQID = '{guid}'
            '''
    try:
        result = execut_query_to_db(sql)
        AGID, P002 = result[0][0], result[0][1]
        if AGID:
            logging.info(f'Создан договор для {fio_last_clid}')
            logging.info(f'AGID = {AGID}')
            logging.info(f'Карта - {P002}')
            info_on_agid = [AGID, P002]

            # Запись данных в файл
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            write_to_file('agreements.txt', current_date, last_clid, AGID, P002)

            return info_on_agid
        else:
            logging.error('Договор не создан. Смотрите i24 + i25')
            logging.error(f'guid сообщения - {guid}')
    except Exception as err:
        logging.error('Договор не создан. Смотрите i24 + i25')
        logging.error(f'guid сообщения - {guid}')
        logging.error(f'Ошибка: {err}')

def write_to_file(file_name, date, clid, agid, card_number):
    """
    Записывает данные в файл.
    :param file_name: Имя файла
    :param date: Дата
    :param clid: CLID
    :param agid: AGID
    :param card_number: Номер карты
    :return: None
    """
    with open(file_name, 'a') as file:
        file.write(f'{date};{clid};{agid};{card_number}\n')

def opening_log_file():
    """
    Открытие текущего лог файла.
    :return: None
    """
    logging.info(f'Открыт файл "{log_file_name}"')
    os.startfile(f'log\\{log_file_name}')

def return_fio_on_clid(clid: str) -> str:
    """
    Получаем ФИО по ID клиента.
    :param clid: CLID
    :return: str
    """
    sql = f'''
        select (N31NAMF || ' '|| N31NAMI || ' '|| N31NAMO) as fio from n31 where N31CLID = {clid}
    '''
    try:
        return execut_query_to_db(sql)[0][0]
    except Exception as err:
        logging.error(f'Последний клиент с CLID = {last_clid} не найден в целевой БД')
        logging.error(f'Ошибка: {err}')
        return f'ERROR клиент отсутствует в целевой БД'

def return_name_id_group_card() -> str:
    """
    Функция возвращает текстовое значение группы типовых параметров карт.
    :return: str
    """
    try:
        return execut_query_to_db(f"select B30CGDS from b30 where B30CGCD = {id_group_card}")[0][0]
    except Exception as err:
        logging.error(f'Несуществующий ID группы типовых параметров карт ({id_group_card}) в ini файле')
        logging.error(f'Ошибка: {err}')
        return f'ERROR несуществующий ID группы'

def return_name_id_agree_type() -> str:
    """
    Функция возвращает текстовое наименование банковского продукта.
    :return: str
    """
    try:
        return execut_query_to_db(f'select T31BPRN from t31 where T31AGRC = {AgreeType}')[0][0]
    except Exception as err:
        logging.error(f'Несуществующий ID банковского продукта ({AgreeType}) в ini файле')
        logging.error(f'Ошибка: {err}')
        return f'ERROR несуществующий ID банковского продукта'

def console_interface():
    """
    Основной интерфейс программы.
    :return: None
    """
    while True:
        logging.info('1 - Создать нового клиента')
        logging.info(f'2 - Открыть договор для {fio_last_clid} CLID = {last_clid}')
        logging.info('9 - Открыть файл лога')
        logging.info('Any key - Выход из программы')
        choice = input('>>> ')
        if choice == '1':
            new_clid = client_add()
            if new_clid:
                logging.info('8 - Поместить CLID в буфер обмена')
                logging.info('Any key - Возврат к созданию клиентов и договоров')
                choice = input('>>> ')
            if choice == '8':
                pyperclip.copy(str(new_clid))
                logging.info('CLID помещен в буфер')
                continue
            else:
                continue
        if choice == '2':
            new_agid = agree_add(last_clid)
            if new_agid:
                logging.info('8 - Поместить AGID в буфер обмена')
                logging.info('7 - Поместить номер карты в буфер обмена')
                logging.info('Any key - Возврат к созданию клиентов и договоров')
                choice = input('>>> ')
            if choice == '8':
                pyperclip.copy(str(new_agid[0]))
                logging.info('AGID помещен в буфер')
                continue
            if choice == '7':
                pyperclip.copy(str(new_agid[1]))
                logging.info('Номер карты помещен в буфер')
                continue
            else:
                continue
        if choice == '9':
            opening_log_file()
        else:
            return

if __name__ == '__main__':
    connection = None
    try:
        schemaName = config['CONN_PARAM']['schemaName']
        password = config['CONN_PARAM']['password']
        serverName = config['CONN_PARAM']['serverName']
        connection = cx_Oracle.connect(
            schemaName,
            password,
            serverName,
            encoding='utf-8')
        logging.info(f'Подключено к {schemaName}@{serverName} (Oracle Database - {connection.version})')
        logging.info(f'Пишется файл лога - "{log_file_name}"')
        logging.info(f'Банковский продукт - "{return_name_id_agree_type()}" (ID = {AgreeType})')
        logging.info(f'Группа карт - "{return_name_id_group_card()}" (ID = {id_group_card})')
        logging.info(f'Последний клиент - {return_fio_on_clid(last_clid)} CLID = {last_clid}')
    except cx_Oracle.Error as error:
        logging.error(f'Ошибка подключения: {error}')
        input()
    else:
        console_interface()

        if connection:
            connection.close()

    logging.info('Исполнение программы завершено')
