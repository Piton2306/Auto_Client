import time

import cx_Oracle  # pip install cx-Oracle
from flask import Flask, request, render_template, g, jsonify

import configparser
import ctypes
import datetime
import list_of_dict  # список фамилий, имен, отчеств
import logging
import os
import platform
import random
import uuid
from logging_config import setup_logging
from plsql_queries import CREATE_CLIENT_QUERY, CREATE_AGREEMENT_QUERY  # Импортируем запросы

app = Flask(__name__)

# Версия программы
program_version = 1.4

# Чтение конфигурационных файлов
config = configparser.ConfigParser()
config.read(r'connection_parameters.ini')

id_group_card = config['AGREE_PARAM']['id_group_card']
AgreeType = config['AGREE_PARAM']['agreetype']

data = configparser.ConfigParser()
data.read(r'data\data.data')

# Инициализация переменных, если они отсутствуют в файле конфигурации
if not data.has_section('SYSTEM_DATA'):
    data.add_section('SYSTEM_DATA')

if not data.has_option('SYSTEM_DATA', 'log_file_counter'):
    data.set('SYSTEM_DATA', 'log_file_counter', '0')

if not data.has_option('SYSTEM_DATA', 'log_file_date'):
    data.set('SYSTEM_DATA', 'log_file_date', '')

if not data.has_option('SYSTEM_DATA', 'last_clid'):
    data.set('SYSTEM_DATA', 'last_clid', '')

if not data.has_option('SYSTEM_DATA', 'fio_last_clid'):
    data.set('SYSTEM_DATA', 'fio_last_clid', '')

with open('data/data.data', 'w') as configfile:
    data.write(configfile)

log_file_counter = data['SYSTEM_DATA']['log_file_counter']
log_file_date = data['SYSTEM_DATA']['log_file_date']
last_clid = data['SYSTEM_DATA']['last_clid']
fio_last_clid = data['SYSTEM_DATA']['fio_last_clid']

real_date = time.strftime('%Y%m%d')
computer_name = platform.node()

ctypes.windll.kernel32.SetConsoleTitleW(
    f"Создание клиентов и договоров на {config['CONN_PARAM']['schemaname']} @ {config['CONN_PARAM']['servername']}")

if log_file_date == real_date:
    log_file_counter = str(int(log_file_counter) + 1)
else:
    log_file_counter = str(1)
    data.set('SYSTEM_DATA', 'log_file_date', f'{real_date}')

data.set('SYSTEM_DATA', 'log_file_counter', f'{log_file_counter}')
with open('data/data.data', 'w') as configfile:
    data.write(configfile)


@app.before_request
def before_request():
    g.user_ip = request.remote_addr
    g.log_file_name, g.logger = setup_logging(log_file_date, log_file_counter, real_date, g.user_ip)


@app.route('/')
def index():
    schemaName = config['CONN_PARAM']['schemaname']
    password = config['CONN_PARAM']['password']
    serverName = config['CONN_PARAM']['servername']
    id_group_card = config['AGREE_PARAM']['id_group_card']
    AgreeType = config['AGREE_PARAM']['agreetype']

    g.logger.info(f'Имя схемы: {schemaName}')
    g.logger.info(f'Имя сервера: {serverName}')
    g.logger.info(f'ID группы карт: {id_group_card}')
    g.logger.info(f'Тип соглашения: {AgreeType}')

    return render_template('index.html', schemaName=schemaName, password=password, serverName=serverName,
                           id_group_card=id_group_card, AgreeType=AgreeType, log_file_name=g.log_file_name,
                           default_schemaName=schemaName, default_password=password, default_serverName=serverName,
                           default_id_group_card=id_group_card, default_AgreeType=AgreeType)


@app.route('/create_client', methods=['POST'], endpoint='create_client_route')
def create_client():
    schemaName = request.form.get('schemaName')
    password = request.form.get('password')
    serverName = request.form.get('serverName')
    id_group_card = request.form.get('id_group_card')
    AgreeType = request.form.get('AgreeType')

    if not all([schemaName, password, serverName, id_group_card, AgreeType]):
        return 'Ошибка: Не все поля заполнены', 400

    # Логирование данных, полученных от клиента
    g.logger.info(
        f'Получены данные для создания клиента: имя схемы={schemaName}, пароль={password}, имя сервера={serverName}, ID группы карт={id_group_card}, тип соглашения={AgreeType}')

    # Подключение к базе данных с использованием новых параметров
    connection = cx_Oracle.connect(schemaName, password, serverName, encoding='utf-8')

    new_clid = client_add(connection, id_group_card, AgreeType)
    if new_clid:
        return f'Создан новый клиент с CLID = {new_clid}'
    else:
        return 'Ошибка при создании клиента', 500


@app.route('/create_agreement', methods=['POST'])
def create_agreement():
    clid = request.form.get('clid')
    id_group_card = request.form.get('id_group_card')
    AgreeType = request.form.get('AgreeType')
    schemaName = request.form.get('schemaName')
    password = request.form.get('password')
    serverName = request.form.get('serverName')

    # Логирование данных, полученных от клиента
    g.logger.info(
        f'Получены данные для создания договора: CLID={clid}, ID группы карт={id_group_card}, тип соглашения={AgreeType}, имя схемы={schemaName}, пароль={password}, имя сервера={serverName}')

    if not all([clid, id_group_card, AgreeType, schemaName, password, serverName]):
        return 'Ошибка: Не все поля заполнены', 400

    # Подключение к базе данных с использованием новых параметров
    connection = cx_Oracle.connect(schemaName, password, serverName, encoding='utf-8')

    new_agid = agree_add(connection, clid, id_group_card, AgreeType)
    if new_agid:
        # Получение данных клиента для отображения
        client_data = get_client_data(connection, clid)
        return render_template('agreement_created.html', agid=new_agid[0], card_number=new_agid[1],
                               client_data=client_data)
    else:
        return 'Ошибка при создании договора', 500


def get_client_data(connection, clid):
    """
    Получает данные клиента по CLID.
    :param connection: соединение с базой данных
    :param clid: CLID клиента
    :return: словарь с данными клиента
    """
    sql = f'''
        select N31NAMF, N31NAMI, N31NAMO, N37PSER, N37PNUM from n31
        join n37 on N31CLID = N37CLID
        where N31CLID = {clid}
    '''
    result = execut_query_to_db(connection, sql)
    if result:
        return {
            'last_name': result[0][0],
            'first_name': result[0][1],
            'middle_name': result[0][2],
            'passport_series': result[0][3],
            'passport_number': result[0][4]
        }
    else:
        return None


def get_log_content(log_file_name):
    """
    Получает содержимое лог-файла.
    :param log_file_name: Имя лог-файла
    :return: Содержимое лог-файла
    """
    log_file_path = os.path.join('log', log_file_name)
    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='replace') as log_file:
            return log_file.read()
    except Exception as e:
        return f"Ошибка при чтении файла лога: {e}"


@app.route('/open_log')
def open_log():
    opening_log_file()
    return 'Файл лога открыт'


@app.route('/view_log')
def view_log():
    log_file_path = os.path.join('log', g.log_file_name)
    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='replace') as log_file:
            log_content = log_file.read()
        return render_template('view_log.html', log_content=log_content)
    except Exception as e:
        return f"Ошибка при чтении файла лога: {e}"


@app.route('/update_config', methods=['POST'], endpoint='update_config_route')
def update_config():
    schemaName = request.form.get('schemaName')
    password = request.form.get('password')
    serverName = request.form.get('serverName')
    id_group_card = request.form.get('id_group_card')
    AgreeType = request.form.get('AgreeType')

    if not all([schemaName, password, serverName, id_group_card, AgreeType]):
        return 'Ошибка: Не все поля заполнены', 400

    # Логирование данных, полученных от клиента
    g.logger.info(
        f'Получены данные для обновления конфигурации: имя схемы={schemaName}, пароль={password}, имя сервера={serverName}, ID группы карт={id_group_card}, тип соглашения={AgreeType}')

    return jsonify(success=True)


def execut_query_to_db(connection, sql: str):
    """
    Выполняет SQL-запрос и возвращает результат.
    :param connection: соединение с базой данных
    :param sql: строка, содержащая запрос
    :return: список строк
    """
    cursor = connection.cursor()
    cursor.execute(sql)
    fetch = cursor.fetchall()
    cursor.close()
    return fetch


def execut_query_to_db_no_fetch(connection, sql):
    """
    Выполняет SQL-запрос без возврата результата.
    :param connection: соединение с базой данных
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
        result = execut_query_to_db(connection, sql)
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
        result = execut_query_to_db(connection, sql)
        if not result:
            return [pass_ser, pass_num]


def client_add(connection, id_group_card, AgreeType) -> int:
    """
    Функция создает нового клиента с использованием сообщения MsgClientAddRq и
    возвращает CLID созданного клиента.
    :param connection: соединение с базой данных
    :param id_group_card: ID группы карт
    :param AgreeType: Тип соглашения
    :return: int
    """
    g.logger.info('Создается новый клиент...')

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

    plSql = CREATE_CLIENT_QUERY.format(guid=guid, NAMF=NAMF, NAMI=NAMI, NAMO=NAMO, BITH=BITH, CINN=CINN, PNUM=PNUM,
                                       PSER=PSER, TVAL=TVAL, computer_name=computer_name)
    execut_query_to_db_no_fetch(connection, plSql)

    sql = f'''
        select N37CLID, N31NAMF, N31NAMI, N31NAMO from n37
        join n31 on N37CLID = N31CLID
        where N37DCTP = 1 and N37PSER = '{PSER}' and N37PNUM = '{PNUM}'
            '''
    try:
        result = execut_query_to_db(connection, sql)
        clid = result[0][0]
        g.logger.info(f'Создан клиент - {result[0][1]} {result[0][2]} {result[0][3]}')
        g.logger.info(f'Паспорт гражданина РФ: серия - {PSER} номер - {PNUM}')
        g.logger.info(f'CLID = {clid}')

        global last_clid
        global fio_last_clid
        last_clid = clid
        fio_last_clid = return_fio_on_clid(connection, last_clid)
        data.set('SYSTEM_DATA', 'last_clid', f'{last_clid}')
        data.set('SYSTEM_DATA', 'fio_last_clid', f'{fio_last_clid}')
        with open('data/data.data', 'w') as configfile:
            data.write(configfile)

        return clid
    except Exception as err:
        g.logger.error(f'Произошла ошибка, смотрите логи, пробуйте снова. guid сообщения - {guid}. Ошибка: {err}')


def agree_add(connection, clid, id_group_card, AgreeType) -> list:
    """
    Создается договор для указанного клиента.
    :param connection: соединение с базой данных
    :param clid: CLID
    :param id_group_card: ID группы карт
    :param AgreeType: Тип соглашения
    :return list: список [AGID, P002]
    """
    g.logger.info('Создается новый договор...')
    guid = uuid.uuid4()
    pl_sql = CREATE_AGREEMENT_QUERY.format(guid=guid, last_clid=clid, AgreeType=AgreeType, id_group_card=id_group_card)
    execut_query_to_db_no_fetch(connection, pl_sql)

    sql = f'''
        select N02DCID as AGID, B31P002 as P002 from i24
        join n02 on N02OPID = I24OPID
        left join b31 on B31AGID = N02DCID
        where I24RQID = '{guid}'
            '''
    try:
        result = execut_query_to_db(connection, sql)
        AGID, P002 = result[0][0], result[0][1]
        if AGID:
            g.logger.info(f'Создан договор для {return_fio_on_clid(connection, clid)}')
            g.logger.info(f'AGID = {AGID}')
            g.logger.info(f'Карта - {P002}')
            info_on_agid = [AGID, P002]

            # Запись данных в файл
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            write_to_file('agreements.txt', current_date, clid, AGID, P002)

            # Обновление переменной last_clid и fio_last_clid
            global last_clid
            global fio_last_clid
            last_clid = clid
            fio_last_clid = return_fio_on_clid(connection, last_clid)
            data.set('SYSTEM_DATA', 'last_clid', f'{last_clid}')
            data.set('SYSTEM_DATA', 'fio_last_clid', f'{fio_last_clid}')
            with open('data/data.data', 'w') as configfile:
                data.write(configfile)

            return info_on_agid
        else:
            g.logger.error('Договор не создан. Смотрите i24 + i25')
            g.logger.error(f'guid сообщения - {guid}')
    except Exception as err:
        g.logger.error('Договор не создан. Смотрите i24 + i25')
        g.logger.error(f'guid сообщения - {guid}')
        g.logger.error(f'Ошибка: {err}')


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
    g.logger.info(f'Открыт файл "{g.log_file_name}"')
    os.startfile(f'log\\{g.log_file_name}')


def return_fio_on_clid(connection, clid: str) -> str:
    """
    Получаем ФИО по ID клиента.
    :param connection: соединение с базой данных
    :param clid: CLID
    :return: str
    """
    sql = f'''
        select (N31NAMF || ' '|| N31NAMI || ' '|| N31NAMO) as fio from n31 where N31CLID = {clid}
    '''
    try:
        result = execut_query_to_db(connection, sql)
        if result:
            return result[0][0]
        else:
            g.logger.error(f'Клиент с CLID = {clid} не найден в целевой БД')
            return f'ERROR клиент отсутствует в целевой БД'
    except Exception as err:
        g.logger.error(f'Ошибка при получении ФИО по ID клиента {clid}: {err}')
        return f'ERROR ошибка при получении ФИО'


def return_name_id_group_card(connection) -> str:
    """
    Функция возвращает текстовое значение группы типовых параметров карт.
    :param connection: соединение с базой данных
    :return: str
    """
    try:
        return execut_query_to_db(connection, f"select B30CGDS from b30 where B30CGCD = {id_group_card}")[0][0]
    except Exception as err:
        g.logger.error(f'Несуществующий ID группы типовых параметров карт ({id_group_card}) в ini файле')
        g.logger.error(f'Ошибка: {err}')
        return f'ERROR несуществующий ID группы'


def return_name_id_agree_type(connection) -> str:
    """
    Функция возвращает текстовое наименование банковского продукта.
    :param connection: соединение с базой данных
    :return: str
    """
    try:
        return execut_query_to_db(connection, f'select T31BPRN from t31 where T31AGRC = {AgreeType}')[0][0]
    except Exception as err:
        g.logger.error(f'Несуществующий ID банковского продукта ({AgreeType}) в ini файле')
        g.logger.error(f'Ошибка: {err}')
        return f'ERROR несуществующий ID банковского продукта'


if __name__ == '__main__':
    with app.app_context():
        connection = None
        try:
            schemaName = config['CONN_PARAM']['schemaname']
            password = config['CONN_PARAM']['password']
            serverName = config['CONN_PARAM']['servername']
            connection = cx_Oracle.connect(
                schemaName,
                password,
                serverName,
                encoding='utf-8')
            logging.info(f'Подключено к {schemaName}@{serverName} (Oracle Database - {connection.version})')
            with app.app_context():
                g.user_ip = '127.0.0.1'  # Используем локальный IP для инициализации
                g.log_file_name, g.logger = setup_logging(log_file_date, log_file_counter, real_date, g.user_ip)
                g.logger.info(f'Пишется файл лога - "{g.log_file_name}"')
                g.logger.info(f'Банковский продукт - "{return_name_id_agree_type(connection)}" (ID = {AgreeType})')
                g.logger.info(f'Группа карт - "{return_name_id_group_card(connection)}" (ID = {id_group_card})')
                g.logger.info(f'Последний клиент - {return_fio_on_clid(connection, last_clid)} CLID = {last_clid}')
        except cx_Oracle.Error as error:
            logging.error(f'Ошибка подключения: {error}')
        else:
            app.run(host='0.0.0.0', port=5000)

        logging.info('Исполнение программы завершено')
