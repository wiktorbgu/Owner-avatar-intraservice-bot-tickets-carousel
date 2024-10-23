import keyring

# Intraservice
USER_BOT_LOGIN = 'intraservice_bot@company.ru'
USER_BOT_PASSWORD = keyring.get_password('py_intraservice_token', 'intraservice_bot')
URL_SERVICE = 'bv.intradesk.ru'

# Database
DB_USER = 'DJANGO'
DB_PASSWORD = keyring.get_password("py_utils_notify", "ORAUSER_DJANGO")

DB_TNS = '''(DESCRIPTION =
    (ADDRESS_LIST =
      (ADDRESS = (PROTOCOL = TCP)(HOST = srv-otp-notify-db)(PORT = 1521))
    )
    (CONNECT_DATA =
      (SERVICE_NAME = notifydb)
    )
  )'''
