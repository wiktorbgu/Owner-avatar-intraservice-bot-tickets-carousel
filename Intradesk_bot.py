import logging, time
from classes import Intradesk, Database_utils, User_utils

logging.basicConfig(format='%(asctime)s %(message)s', filename='logfile.log', level=logging.INFO)
logger = logging.getLogger(__name__)
intra = Intradesk
db_utils = Database_utils
users_utils = User_utils

while (True):
    try:
        # выбираем активные сервисы и проходимся по каждому
        for service in db_utils.select_services():
            service_id = service['id']
            print(f'Выбираем сервис {service_id}')
            # выбираем активных пользователей
            users = db_utils.select_users(service_id)
            # может быть так, что сервис активен - а пользователи на нем нет.
            if users:
                last_user_id = users[0]['last_user_id']
                print(f'last_user_id {last_user_id}')
                # выргужаем бесхозные заявки по сервису
                tasklist = intra.get_tasks(service_id)
                # проходимся по всем выбранным заявкам и раскидываем согласно очереди
                for r, row in enumerate(tasklist['value']):
                    next_user_id = users_utils.get_next_user_id(users, last_user_id)
                    print(f"Сервис {service_id} Назначаем заявку {row['tasknumber']} юзеру {next_user_id}")
                    logger.info(f"Назначаем заявку {row['tasknumber']} юзеру {next_user_id} - {row}")
                    # назначаем заявку
                    logger.info(intra.assign_task(row['tasknumber'], next_user_id))
                    # фиксируем в базе и локально
                    last_user_id = next_user_id
                    db_utils.set_last_user(last_user_id, service_id)
                    print(f'Пишем в базу last_user_id: {last_user_id}')
            else:
                print(f'На сервисе {service_id} нет активных пользователей.')
                logger.info(f'На сервисе {service_id} нет активных пользователей.')
    except Exception as error:
        logger.exception(error)
    finally:
        print('--- Перекур на минутку ---')
        time.sleep(60)
