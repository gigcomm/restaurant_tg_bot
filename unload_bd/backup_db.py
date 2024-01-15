import subprocess
import time
import schedule
import requests
import shutil
import os
from datetime import datetime
import asyncio


async def backup():
    password = '1'
    db_name = 'db_kurs'
    host = 'localhost'
    port = 5432
    user = 'postgres'
    os.environ['PGPASSWORD'] = "1"
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M")
    #print(current_datetime)

    command = f'"C:\\Program Files\\PostgreSQL\\16\\bin\\pg_dump.exe" -d {db_name} -h {host} -p {port} -U {user} -w -f \
                  "C:/Users/Игорь/YandexDisk/db_kurs_backapp/Yonder_backup_{current_datetime}.sql"'

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    output = stdout.decode(errors='ignore')
    errors = stderr.decode(errors='ignore')

    if errors:
        print(f'Произошла ошибка: {errors}')
    else:
        print('Backup успешно выполнен', current_datetime)


def run_backup():
    asyncio.run(backup())


def main():
    schedule.every(5).minutes.do(run_backup)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
