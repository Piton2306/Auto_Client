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

import list_of_dict  # список фамилий, имен, отчеств

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

ctypes.windll.kernel32.SetConsoleTitleW(f"Создание клиентов и договоров на {config['CONN_PARAM']['schemaName']} @ "
                                        f"{config['CONN_PARAM']['serverName']}")

if log_file_date == real_date:
    log_file_counter = str(int(log_file_counter) + 1)
    data.set('SYSTEM_DATA', 'log_file_counter', f'{log_file_counter}')
    with open('data/data.data', 'w') as configfile:
        data.write(configfile)
else:
    log_file_counter = str(1)
    data.set('SYSTEM_DATA', 'log_file_counter', f'{log_file_counter}')
    data.set('SYSTEM_DATA', 'log_file_date', f'{real_date}')
    with open('data/data.data', 'w') as configfile:
        data.write(configfile)
log_file_name = f'{real_date}_{computer_name}_{log_file_counter.rjust(5, "0")}.txt'

sp10 = " " * 11


def execut_query_to_db(sql: str):
    """
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
    для PL/SQL
    :param sql: строка, содержащая запрос
    :return: None
    """
    cursor = connection.cursor()
    cursor.execute(sql)
    cursor.close()


def unique_inn() -> int:
    """
    Функция возвращает уникальное значение ИНН
    :return: int
    """
    # print('unique_inn_START')
    while True:
        inn = random.randint(111111111111, 999999999999)
        # inn = '456456555556'  # Существующий ИНН для отладки
        sql = f'''
            select N31CLID from n31 where n31cinn = '{inn}'
            '''
        result = execut_query_to_db(sql)
        if result:
            pass
        else:
            # print(f'Сгенеренный уникальный ИНН - {inn}')
            # print('unique_inn_END')
            return inn


def unique_passport_data() -> list:
    """
    Функция возвращает уникальное значение серии и номера паспорта
    в виде списка из двух элементов в формате [СЕРИЯ, НОМЕР]
    :return: list
    """
    # print('unique_passport_data_START')
    while True:
        pass_data = []
        pass_ser = random.randint(1111, 9999)
        pass_num = random.randint(111111, 999999)
        # pass_ser = '4545'  # для отладки
        # pass_num = '456545'  # для отладки
        sql = f'''
                select N37CLID from n37 where N37DCTP = 1 and N37PSER = '{pass_ser}' and N37PNUM = '{pass_num}'
            '''
        result = execut_query_to_db(sql)
        if result:
            pass
        else:
            # print('unique_passport_data_END')
            pass_data.insert(0, pass_ser)
            pass_data.insert(1, pass_num)
            return pass_data


def client_add() -> int:
    """
    Функция создает нового клиента с использованием сообщения MsgClientAddRq и
    возвращает CLID созданного клиента
    :return:
    """
    print_and_log(f'{time.strftime("%H:%M:%S")}   Создается новый клиент . . . \n')

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

    plSql = f'''
    declare
    A           CLOB;
    B           CLOB;
    pserrdesc   varchar2(1000);
    TEXT CLOB:= '
    <MsgClientAddRq>
        <RqUID>{guid}</RqUID>
        <PersonForm>
            <PersonName>
                <NAMF>{NAMF}</NAMF>
                <NAMI>{NAMI}</NAMI>
                <NAMO>{NAMO}</NAMO>
            </PersonName>
    
            <PersonCommonInfo>
                <TSEX>мужской</TSEX>
                <BITH>{BITH}</BITH>
                <CINN>{CINN}</CINN>
                <TAGO>1</TAGO>
                <CNTR internal_id="643"/>
                <LBIR>Москва</LBIR>
                <WORK>ПСИТ PYTHON {computer_name}</WORK>
            </PersonCommonInfo>
    
            <IdentityPaper out_of_date="false" internal_id="0" deleted="false">
                <DCTP internal_id="1"/>
                <PNUM>{PNUM}</PNUM>
                <PSER>{PSER}</PSER>
                <PORG>ОВД Пресненского района 55</PORG>
                <DEPC>133-456</DEPC>
                <PDAT>2016-08-13</PDAT>
                <CNTR internal_id="643"></CNTR>
                <PDEX>2031-08-13</PDEX>
            </IdentityPaper>
            <PersonAddress>
                <PersonAddressType internal_id="1"></PersonAddressType>
                    <AddressParams>
                        <CNTR internal_id="643"></CNTR>
                        <INDX>123456</INDX>
                        
                        <SITY>Москва</SITY>
                        <TSIT>город</TSIT>
                        <PNNM>Москва</PNNM>
                        
                        <STNM>Живописная</STNM>
                        <STTP>улица</STTP>
                        <HOUS>8</HOUS>
                        <BLDN>1</BLDN>
                        <COMP>2</COMP>
                        <APRT>12</APRT>
                        
                    </AddressParams>
            </PersonAddress>
    
            <ContactInfo>
                <ContactType internal_id="21805"></ContactType>
                <TVAL>+9(905){TVAL}</TVAL>
                <TCOM>Комментарий не звонить</TCOM>
            </ContactInfo>
    
        </PersonForm>
    
    </MsgClientAddRq>
    ';
    begin
            B:=RRAM_HANDLER.UniMessHandler(TEXT,'DBO3CARDR',to_char(null),null,null,1, pserrdesc);
    end;
'''
    execut_query_to_db_no_fetch(plSql)

    sql = f'''
        select N37CLID, N31NAMF, N31NAMI, N31NAMO from n37
        join n31 on N37CLID = N31CLID
        where N37DCTP = 1 and N37PSER = '{PSER}' and N37PNUM = '{PNUM}'
            '''
    try:
        result = execut_query_to_db(sql)
        clid = result[0][0]
        print_and_log(f'{time.strftime("%H:%M:%S")}   Создан клиент - {result[0][1]} {result[0][2]} {result[0][3]}'
                      f'\n{sp10}Паспорт гражданина РФ: серия - {PSER} номер - {PNUM}'
                      f'\n{sp10}CLID = {clid}\n')

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
        print_and_log(f'{time.strftime("%H:%M:%S")} E Произошла ошибка, смотрите логи, пробуйте снова\n'
                      f'{sp10}guid сообщения - {guid}\n'
                      f'{sp10}Ошибка: {err}')


def agree_add(last_clid) -> list:
    """
    Создается договор для указанного клиента
    :param last_clid: CLID
    :return list: список [AGID, P002]
    """
    print_and_log(f'{time.strftime("%H:%M:%S")}   Создается новый договор . . . \n')
    guid = uuid.uuid4()
    pl_sql = f'''
    declare
    B           CLOB;
    pserrdesc   varchar2(1000);
    TEXT CLOB:= '
    <MsgAgreeAddRq actual_at_once="true">
        <RqUID>{guid}</RqUID>
        <ClientId>{last_clid}</ClientId>  
        <AgreeRequest>
            <AgreeType internal_id="{AgreeType}"></AgreeType>
            <AgreeSum>100</AgreeSum>
            <AgreeCardInfo>
                <NotInstantCard>
                    <MainParameters>
                        <GroupCardId internal_id="{id_group_card}"></GroupCardId>
                    </MainParameters>
                </NotInstantCard>
            </AgreeCardInfo>  
        </AgreeRequest>
    </MsgAgreeAddRq>
    ';
    begin
                B:=RRAM_HANDLER.UniMessHandler(TEXT,'DBO3CARDR',to_char(null),null,null,1, pserrdesc);
    end;
                '''
    execut_query_to_db_no_fetch(pl_sql)

    sql = f'''
        select N02DCID as AGID, B31P002 as P002 from i24
        join n02 on N02OPID = I24OPID
        left join b31 on B31AGID = N02DCID
        where I24RQID = '{guid}'
            '''
    # result = execut_query_to_db(sql)
    # AGID, P002 = result[0][0], result[0][1]
    # if AGID:
    #     print_and_log(f'{time.strftime("%H:%M:%S")}  Создан договор для {fio_last_clid}'
    #                   f'\n{sp10}AGID  = {AGID} '
    #                   f'\n{sp10}Карта - {P002}')
    #     info_on_agid = [AGID, P002]
    #     return info_on_agid
    # else:
    #     print_and_log(f'{time.strftime("%H:%M:%S")}  Произошла ошибка'
    #                   f'\n{sp10}Договор не создан'
    #                   f'\n{sp10}Cмотрите i24 + i25'
    #                   f'\n{sp10}guid сообщения - {guid}')

    try:
        result = execut_query_to_db(sql)
        AGID, P002 = result[0][0], result[0][1]
        if AGID:
            print_and_log(f'{time.strftime("%H:%M:%S")}   Создан договор для {fio_last_clid}'
                          f'\n{sp10}AGID  = {AGID} '
                          f'\n{sp10}Карта - {P002}')
            info_on_agid = [AGID, P002]
            return info_on_agid
        else:
            print_and_log(f'{time.strftime("%H:%M:%S")} E Произошла ошибка'
                          f'\n{sp10}Договор не создан'
                          f'\n{sp10}Cмотрите i24 + i25'
                          f'\n{sp10}guid сообщения - {guid}')
    except Exception as err:
        print_and_log(f'{time.strftime("%H:%M:%S")} E Произошла ошибка'
                      f'\n{sp10}Договор не создан'
                      f'\n{sp10}Cмотрите i24 + i25'
                      f'\n{sp10}guid сообщения - {guid}'
                      f'\n{sp10}Ошибка: {err}')
    # try:
    #     result = execut_query_to_db(sql)
    #     AGID, P002 = result[0][0], result[0][1]
    #
    #     print_and_log(f'{time.strftime("%H:%M:%S")}  Создан договор для {fio_last_clid}'
    #                   f'\n{sp10}AGID  = {AGID} '
    #                   f'\n{sp10}Карта - {P002}')
    #     info_on_agid = [AGID, P002]
    #     return info_on_agid
    # except Exception as err:
    #     print_and_log(f'{time.strftime("%H:%M:%S")}  Произошла ошибка, смотрите логи, пробуйте снова\n'
    #                   f'{sp10}guid сообщения - {guid}\n'
    #                   f'{sp10}Ошибка: {err}')


def print_and_log(text: str):
    """
    Печать на экран и в лог файл
    :param text:
    :return:
    """
    print(text)
    text = text + '\n'
    with open(f"log\\{log_file_name}", "a") as f:
        f.write(text)


def opening_log_file():
    """
    Открытие текущего лог файла
    :return:
    """
    print_and_log(f'{time.strftime("%H:%M:%S")}   Открыт файл "{log_file_name}"')
    os.startfile(f'log\\{log_file_name}')


def return_fio_on_clid(clid: str) -> str:
    """
    Получаем ФИО по ID клиента
    :param clid:
    :return: str
    """
    sql = f'''
        select (N31NAMF || ' '|| N31NAMI || ' '|| N31NAMO) as fio from n31 where N31CLID = {clid}
    '''
    try:
        return execut_query_to_db(sql)[0][0]
    except Exception as err:
        print_and_log(f'\n\n{sp10}ERROR return_fio_on_clid()'
                      f'\n{sp10}last_clid = {last_clid}'
                      f'\n{sp10}Последний клиент с CLID = {last_clid} не найден в целевой БД'
                      f'\n{sp10}Ошибка: {err}\n\n')
        return f'ERROR клиент отсутствует в целевой БД'


def return_name_id_group_card() -> str:
    """
    Функция возвращает текстовое значение группы типовых параметров карт
    на основе параметра id_group_card из ini файла
    :return: str
    """
    try:
        return execut_query_to_db(f"select B30CGDS from b30 where B30CGCD = {id_group_card}")[0][0]
    except Exception as err:
        print_and_log(f'\n\n{sp10}ERROR return_name_id_group_card()'
                      f'\n{sp10}id_group_card = {id_group_card}'
                      f'\n{sp10}Несуществующий ID группы типовых параметров карт ({id_group_card}) в ini файле'
                      f'\n{sp10}Ошибка: {err}\n\n')
        return f'ERROR несуществующий ID группы'


def return_name_id_agree_type() -> str:
    """
    Функция возвращает текстовое наименование банковского продукта
    на основе параметра AgreeType из ini файла
    :return: -> str
    """
    try:
        return execut_query_to_db(f'select T31BPRN from t31 where T31AGRC = {AgreeType}')[0][0]
    except Exception as err:
        print_and_log(f'\n\n{sp10}ERROR return_name_id_agree_type()'
                      f'\n{sp10}AgreeType = {AgreeType}'
                      f'\n{sp10}Несуществующий ID банковского продукта ({AgreeType}) в ini файле'
                      f'\n{sp10}Ошибка: {err}\n\n')
        return f'ERROR несуществующий ID банковского продукта'


def console_interface():
    """
    Основной интерфейс программы
    :return:
    """
    while True:
        print_and_log(f'\n{time.strftime("%H:%M:%S")}   1 - Создать нового клиента'
                      f'\n{sp10}2 - Открыть договор для {fio_last_clid} CLID = {last_clid}'
                      f'\n{sp10}9 - Открыть файл лога'
                      f'\n{sp10}Any key - Выход из программы')
        choice = input(f'{sp10}>>> ')
        if choice == '1':
            new_clid = client_add()
            if new_clid:
                print_and_log(f'{sp10}8 - Поместить CLID в буфер обмена'
                              f'\n{sp10}Any key - Возврат к созданию клиентов и договоров')
                choice = input(f'{sp10}>>> ')
            if choice == '8':
                pyperclip.copy(str(new_clid))
                print_and_log(f'{time.strftime("%H:%M:%S")}   CLID помещен в буфер')
                continue
            else:
                continue
        if choice == '2':
            new_agid = agree_add(last_clid)
            if new_agid:
                print_and_log(f'\n{sp10}8 - Поместить AGID в буфер обмена'
                              f'\n{sp10}7 - Поместить номер карты в буфер обмена'
                              f'\n{sp10}Any key - Возврат к созданию клиентов и договоров')
                choice = input(f'{sp10}>>> ')
            if choice == '8':
                pyperclip.copy(str(new_agid[0]))
                print_and_log(f'{time.strftime("%H:%M:%S")}   AGID помещен в буфер')
                continue
            if choice == '7':
                pyperclip.copy(str(new_agid[1]))
                print_and_log(f'{time.strftime("%H:%M:%S")}   Номер карты помещен в буфер')
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
        # print(f'{time.strftime("%H:%M:%S")} - Версия oracle сервера -', connection.version,
        #       f'\n{" " * 11}Схема - {schemaName}@{serverName}', '\n')
        print_and_log(f'{time.strftime("%H:%M:%S")}   creation_client (program version - {program_version})'
                      f'\n{sp10}Подключено к {schemaName}@{serverName} '
                      f'(Oracle Database - {connection.version})'
                      f'\n{sp10}Пишется файл лога - "{log_file_name}"'
                      f'\n{sp10}Банковский продукт - "{return_name_id_agree_type()}" (ID = {AgreeType})'
                      f'\n{sp10}Группа карт - "{return_name_id_group_card()}" (ID = {id_group_card})'
                      f'\n{sp10}Последний клиент - {return_fio_on_clid(last_clid)} CLID = {last_clid}')
    except cx_Oracle.Error as error:
        # print(f'{time.strftime("%H:%M:%S")} -', error)
        print_and_log(f'{time.strftime("%H:%M:%S")} E {error}')
        input()
    else:

        console_interface()

        if connection:
            connection.close()

    print_and_log(f'\n{time.strftime("%H:%M:%S")}   Исполнение программы завершено')
    # input('Нажмите Enter для выхода')  # для консоли
