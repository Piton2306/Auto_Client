@echo off
REM Запуск виртуального окружения
call venv\Scripts\activate

REM Запуск Flask-приложения
python app.py

REM Деактивация виртуального окружения после завершения работы приложения
call venv\Scripts\deactivate