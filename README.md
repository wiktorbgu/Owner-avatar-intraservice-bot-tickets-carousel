## Intraservice бот автоматического распределения заявок по карусели на БД Oracle

Для начала работы нужно создать пользователя бота в интрасервисе и пользователя DJANGO в БД.  
* В БД залить структуру из `DB_create_objects/backup.sql`  
* Если необходимо выдать права стороннему пользователю БД для управления сервисом, выполните файл `manual_user_grants.sql` с его именем пользователя `USER_NAME`.   
* Выполнить установку пакетов ```pip install -r requirements.txt```
* Внести настройки в файл `settings.py`
* Залить данные из интрасервиса в БД `intradesk_importer.py` (и в будущем периодически выполнять им же обновление данных в БД из интрасервиса)
- #### Добавить пароли в хранилище
  + keyring.set_password("py_utils_notify", "ORAUSER_DJANGO", 'ПАРОЛЬ ПОЛЬЗОВАТЕЛЯ БАЗЫ ДАННЫХ DJANGO')
  * keyring.set_password('py_intraservice_token', 'intraservice_bot', 'ПАРОЛЬ ПОЛЬЗОВАТЕЛЯ ИНТРАДЕСКА intraservice_bot')

### Принцип действия:

#### Управление сервисом в intradesk:  
Группы пользователей  
https://company.intradesk.ru/employees/employeegroups  
Сотрудники  
https://company.intradesk.ru/employees/employeeusers  

Сотрудники раскиданы по группам, в которых они будут участвовать в карусели

Сервисы = очереди заявок на выполнение  
https://company.intradesk.ru/settings/services  
В каждом сервисе привязываем группу пользователей - кого будем вертеть на карусели


#### По БАЗЕ:
По-умолчанию все новоприбывшие данные из интры в базу - это новые сервисы и новые пользователи - **НЕ АКТИВНЫ** .  
Если были изменены названия старых объектов в интре - они обновятся при импорте и в БД.

* Карусель выбирает активные сервисы  
* И в каждом активном сервисе выбирает активных пользователей

P.S. Если сервис активен и на нем нет пользователей. Лучше его выключить, чтобы не брать его в итерацию.

#### Управление сервисом в БД:
— активировать сервисы для каруселивирования  
```select t.*, t.rowid from DJANGO.DESK_SERVICES t```  
— активировать юзеров для того же самого  
```select t.*, t.rowid from DJANGO.DESK_USERS t```  
Так же есть возможность ставить даты отпуска пользователям в столбцы ```off_start_date``` и ```off_end_date```

— посмотреть в целом картину по сервису или по юзерам и сервисам которые сейчас попадут в карусель  
```
select * from DJANGO.DESK_USERS_ALL_INFO t
where t.enabled = 1
and ((trunc(sysdate) < t.off_start_date or trunc(sysdate) > t.off_end_date) or (t.off_start_date is null or t.off_end_date is null))
and t.service_id = 54836
--and t.service_id = 71599
--and t.usergroup_id = 130608
order by t.id
```

В БД все объекты относящиеся к сервису карусели начинаются на "DESK_"