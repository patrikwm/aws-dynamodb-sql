import random
import time
from datetime import datetime

import mysql.connector
import names
from decouple import config

MYSQL_HOST = config('MYSQL_HOST')
MYSQL_DATABASE = config('MYSQL_DATABASE')
MYSQL_USER = config('MYSQL_USER')
MYSQL_ROOT_PASSWORD = config('MYSQL_ROOT_PASSWORD')


def insert_to_sql(query, values=None):
    result = None
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        passwd=MYSQL_ROOT_PASSWORD,
        database=MYSQL_DATABASE
    )
    cursor = connection.cursor()
    try:
        if values:
            cursor.executemany(query, values)
        else:
            cursor.execute(query)
        connection.commit()
    except mysql.connector.Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
    return result


def generate_phone_number() -> str:
    phone_number = "+1"
    for columns in range(9):
        phone_number = phone_number + str(random.randint(0, 9))
    return phone_number


if __name__ == "__main__":
    NUMBER_OF_STUDENTS = 1000
    insert_to_sql(query="drop table student;")
    CREATE_MYSQL_TABLE = """CREATE TABLE student (
                            id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
                            firstname VARCHAR(255), 
                            lastname VARCHAR(255), 
                            mail VARCHAR(255), 
                            phone VARCHAR(255),
                            created_at DATETIME,
                            random_infoA VARCHAR(255),
                            random_infoB VARCHAR(255),
                            random_infoC VARCHAR(255)
                            );
                        """
    insert_to_sql(query=CREATE_MYSQL_TABLE)
    sql = """INSERT INTO student
                (firstname, lastname, mail, phone, created_at, random_infoA, random_infoB, random_infoC) 
                VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s)"""
    students = []
    for i in range(NUMBER_OF_STUDENTS):
        ts = time.time()
        timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        student = (names.get_first_name(),
                   names.get_last_name(),
                   "{0}.{1}@{1}{2}.com".format(names.get_first_name(), names.get_last_name(), i).lower(),
                   generate_phone_number(),
                   timestamp,
                   "infoA{0}".format(i),
                   "infoB{0}".format(i),
                   "infoC{0}".format(i)
                   )
        students.append(student)
        if ((i+1) % 500) == 0:
            print("{0}: Writing to {1} entries to sql.".format(timestamp, i+1))
            insert_to_sql(query=sql, values=students)
            students.clear()
    print("{0}: Done!.".format(timestamp))
