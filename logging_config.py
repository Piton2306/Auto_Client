import logging
import os

def setup_logging(log_file_date, log_file_counter, real_date, user_ip):
    log_file_name = f'{real_date}_{user_ip}_{log_file_counter.rjust(5, "0")}.txt'
    log_file_path = os.path.join('log', log_file_name)

    # Создаем логгер
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Удаляем все существующие обработчики
    if logger.hasHandlers():
        logger.handlers.clear()

    # Создаем обработчик для записи логов в файл
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Создаем обработчик для вывода логов в консоль
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    # Создаем форматтер для логов
    formatter = logging.Formatter('%(asctime)s,%(msecs)03d - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Добавляем обработчики в логгер
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return log_file_name, logger
