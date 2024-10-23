import requests, time, settings


class IntradeskToken:
    def __init__(self, login, password):
        self.token = None
        self.expires_at = None
        self.__payload = {'grant_type': 'password',
                          'scope': 'openid profile email custom.profile api offline_access',
                          'username': login,
                          'password': password,
                          'client_id': 'resourceowner',
                          'acr_values': f'tenant:{settings.url_service}'}

    def get_token(self):
        if self.token is None or self.expires_at < time.time():
            response = requests.post(
                'https://login.intradesk.ru/connect/token',
                data=self.__payload
            )
            response.raise_for_status()
            data = response.json()
            self.token = data['access_token']
            self.expires_at = time.time() + data['expires_in']
        return self.token


token = IntradeskToken(settings.user_bot_login, settings.user_bot_password)


def headers():
    return {'authorization': f'Bearer {token.get_token()}', 'content-type': 'application/json'}


# token.get_token()

class Intradesk:
    @staticmethod
    def get_user_id_by_name_search(user_name):
        '''Поиск пользователя по имени и/или фамилии, для получения его id и других данных'''
        params = dict(
            str=user_name,
            top=1000)
        response = requests.get('https://apigw.intradesk.ru/hints/api/Hints/executors', headers=headers(), params=params)
        response.raise_for_status()
        response.text
        return response.json()

    @staticmethod
    def get_all_employees():
        '''Получить список всех сотрудников в системе с их id и другими данными'''
        response = requests.get('https://apigw.intradesk.ru/settings/odata/Employees', headers=headers())
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_all_employee_groups():
        '''Получить список групп сотрудников в системе с их id и другими данными'''
        response = requests.get('https://apigw.intradesk.ru/settings/odata/v2/EmployeeGroups', headers=headers())
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_services():
        '''Получить список сервисов, их id и другие данные'''
        payload = {"chainName": "ShowServiceListChainV2"}
        response = requests.post('https://apigw.intradesk.ru/rules/api/rules', headers=headers(), json=payload)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_service_users(id_service):
        '''Получить пользователей сервиса, их id и другие данные'''
        response = requests.get(f'https://apigw.intradesk.ru/settings/api/serviceusers/{id_service}', headers=headers())
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_statuses():
        '''Получение списка статусов с их id и другими данными'''
        response = requests.get('https://apigw.intradesk.ru/settings/odata/statuses', headers=headers())
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_tasks(id_service):
        '''Получение списка свободных заявок для распределения'''
        response = requests.get(f"https://apigw.intradesk.ru/tasklist/odata/tasks?$orderby=createdat desc&$filter=service eq {id_service} and contains('_isnotfilled','executor')", headers=headers())
        response.raise_for_status()
        return response.json()

    @staticmethod
    def assign_task(id_task, id_intra_user):
        """Назначение заявки"""
        payload = {"number": id_task,
                   "blocks": {
                       "executor": '{"value":{"userid":%s}}' % id_intra_user
                   }
                   }
        response = requests.put('https://apigw.intradesk.ru/changes/tasks', headers=headers(), json=payload)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_task(tasknumber):
        '''Получение данных по заявке'''
        response = requests.get(f"https://apigw.intradesk.ru/tasklist/odata/tasks?$filter=tasknumber eq {tasknumber}", headers=headers())
        response.raise_for_status()
        return response.json()


import sql_code, oracledb, settings

SRV_OTP_NOTIFY_DB = {'user': settings.DB_USER, 'password': settings.DB_PASSWORD, 'dsn': settings.DB_TNS, 'min': 0, 'max': 4, 'increment': 1}
pool_db = oracledb.create_pool(**SRV_OTP_NOTIFY_DB)


class Database_utils:
    @staticmethod
    def select_users(service_id):
        with pool_db.acquire() as connection:
            with connection.cursor() as cur:
                cur.execute(sql_code.ACTIVE_SERVICE_USERS, service_id=service_id)
                columns = list(map(str.lower, [col[0] for col in cur.description]))  # все имена столбцов опускаем в нижний регистр, чтобы ниже выбирать по имени
                cur.rowfactory = lambda *args: dict(zip(columns, args))
                return cur.fetchall()

    @staticmethod
    def set_last_user(id_intra_user, service_id):
        with pool_db.acquire() as connection:
            connection.autocommit = True
            with connection.cursor() as cur:
                cur.execute(sql_code.SET_LAST_USER_SERVICE, service_id=service_id, last_user_id=id_intra_user)

    @staticmethod
    def select_services():
        with pool_db.acquire() as connection:
            with connection.cursor() as cur:
                cur.execute(sql_code.ACTIVE_SERVICES)
                columns = list(map(str.lower, [col[0] for col in cur.description]))  # все имена столбцов опускаем в нижний регистр, чтобы ниже выбирать по имени
                cur.rowfactory = lambda *args: dict(zip(columns, args))
                return cur.fetchall()


class User_utils:
    # @staticmethod
    def get_next_user_id(user_list, last_user_id):
        '''Эта функция возвращает следующий ид пользователя в списке пользователей.
         Если данный last_user_id является последним идентификатором пользователя в списке, эта функция возвращает первый идентификатор пользователя'''

        if last_user_id:
            # Фильтруем список пользователей, чтобы найти следующий идентификатор
            next_user = next((user["id"] for user in user_list if user["id"] > last_user_id), None)

            # Если следующего пользователя нет, то начинаем сначала
            if next_user is None:
                return user_list[0]["id"]
            else:
                return next_user
        else:
            return user_list[0]["id"]
