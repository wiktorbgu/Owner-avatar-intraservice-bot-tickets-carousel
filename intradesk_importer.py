import re, oracledb, settings
from classes import Intradesk

connection = oracledb.connect(user=settings.DB_USER, password=settings.DB_PASSWORD, dsn=settings.DB_TNS)
connection.autocommit = True


def bulk_insert(sql, data):
    '''Функция очищает таблицу для загрузки методом truncate и загружает в неё данные методом bulk insert'''
    # предохранитель от пустых данных
    if len(data) > 0:
        table_name = re.search(r'insert into (?P<table>.*) \(.*\(', sql).groupdict()['table']
        with connection.cursor() as cursor:
            cursor.execute(f'truncate table {table_name}')
            cursor.executemany(sql, data)


def select_field_data(dict_list, dict_keys):
    '''Функция возвращает список словарей только с указанными полями в словарях очищая все остальные'''
    new_list = []
    for original_dict in dict_list:
        new_dict = {}
        for key in dict_keys:
            new_dict[key] = original_dict.get(key, None)
        new_list.append(new_dict)
    return new_list


def get_user_group_binds(users):
    '''Функция выбирает привязки пользователя по ключу groups и создает список привязок для загрузки в БД'''
    dict_keys = ['id', 'userGroupId', 'userId']
    new_list = []
    for original_dict in users:
        if original_dict['groups']:
            for bind_dict in original_dict['groups']:
                new_dict = {}
                for key in dict_keys:
                    new_dict[key] = bind_dict.get(key, None)
                new_list.append(new_dict)
    return new_list


def get_service_usergroup_binds(service_list):
    '''Функция собирает привязки сервисов к группам пользвателей по поданному в неё списку сервисов'''
    service_usergroup_binds = []
    for service in service_list:
        service_users = intra.get_service_users(service['id'])['employeesUserGroups']
        if service_users:
            for usergroup_bind in service_users:
                new_dict = {}
                new_dict['service_id'] = service['id']
                new_dict['usergroup_id'] = usergroup_bind['id']
                service_usergroup_binds.append(new_dict)
    return service_usergroup_binds


intra = Intradesk
######### data load in db #########
# services
services = intra.get_services()['r_servicelist']['services']
services_load = select_field_data(services, ['id', 'name', 'fullname', 'description'])
sql_services = 'insert into desk_services_load (id, name, fullname, description) values (:id, :name, :fullname, :description)'
bulk_insert(sql_services, services_load)
# users
users = intra.get_all_employees()['value']
users_load = select_field_data(users, ['id', 'name', 'firstName', 'lastName', 'middleName', 'email', 'userName'])
sql_users = "insert into DESK_USERS_LOAD (id, name, firstname, lastname, middleName, email, username) values (:id, :name, :firstname, :lastname, :middlename, :email, :username)"
bulk_insert(sql_users, users_load)
# user groups
user_groups = intra.get_all_employee_groups()['value']
user_groups_load = select_field_data(user_groups, ['id', 'name', 'description'])
sql_user_groups = 'insert into DESK_USERGROUPS_LOAD (ID, NAME, DESCRIPTION) VALUES (:id, :name, :description)'
bulk_insert(sql_user_groups, user_groups_load)
# user group binds - грузим сразу в боевую таблицу - не для предзагрузки
user_group_binds_load = get_user_group_binds(users)
sql_user_group_binds = 'insert into DESK_USER_GROUP_BINDS (id, usergroupid, userid) VALUES (:id, :usergroupid, :userid)'
bulk_insert(sql_user_group_binds, user_group_binds_load)
# service usergroup binds - грузим сразу в боевую таблицу - не для предзагрузки
service_usergroup_binds = get_service_usergroup_binds(services)
sql_service_usergroup_binds = 'insert into DESK_SERVICE_USERGROUP_BINDS (service_id, usergroup_id) VALUES (:service_id, :usergroup_id)'
bulk_insert(sql_service_usergroup_binds, service_usergroup_binds)
####
# ВЫЗОВ ПРОЦЕДУРЫ MERGE
with connection.cursor() as cursor:
    cursor.callproc('desk_merge_data_load')
###
connection.close()
print('Finish!')
