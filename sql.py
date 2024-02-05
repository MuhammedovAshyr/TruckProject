import pyodbc as odbc

DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = 'DESKTOP'
DATABASE_NAME = 'testDB'

connection_string = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trust_Connection=yes;
    uid=;
    pwd=;
"""

conn = odbc.connect(connection_string)
print(conn)

cursor = conn.cursor()

sql = """select * from Invoices"""
# sql = """select CONVERT(DATE, [Дата и время]) from Invoices"""

cursor.execute(sql)
for i in cursor:
    print(i)
