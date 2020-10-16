from datetime import datetime
import json
import time

import boto3
import mysql.connector
from botocore.config import Config as BotocoreConfig
from decouple import config

MYSQL_HOST = config('MYSQL_HOST')
MYSQL_DATABASE = config('MYSQL_DATABASE')
MYSQL_USER = config('MYSQL_USER')
MYSQL_ROOT_PASSWORD = config('MYSQL_ROOT_PASSWORD')
DYNAMODB_TABLE = config('DYNAMODB_TABLE')


def database_select_query(query):
    """
    Make a query in database and return a dict with column_names as key.
    """
    result = None
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        passwd=MYSQL_ROOT_PASSWORD,
        database=MYSQL_DATABASE
    )
    cursor = connection.cursor()
    cursor.execute(query)
    try:
        column_names = [column[0] for column in cursor.description]
        result = [dict(zip(column_names, row))
                  for row in cursor.fetchall()]
    except mysql.connector.Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
    return result


def ddb_batch_write(items):
    """
    Write items to AWS DynamoDB.
    """
    ts = time.time()
    timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    # Increaseed max attempts to 30. Default=10
    max_attempts = BotocoreConfig(
        retries=dict(total_max_attempts=30))
    client = boto3.client('dynamodb', config=max_attempts)
    print("{0}: Sending Batch write to AWS with {1} number of items.".format(timestamp, len(items[DYNAMODB_TABLE])))
    response = client.batch_write_item(RequestItems=items)
    #print(json.dumps(response, sort_keys=True, indent=4))
    if response.get('UnprocessedItems', None):
        print("UnprocessedItems: {0}".format(response.get('UnprocessedItems', None)))


def convert_sql2ddb(item):
    """
    Create a new item that can be sent to dynamodb.
    """
    student_remodel = {DYNAMODB_TABLE: {
        'PutRequest': {
            'Item': {
                'mail': {'S': str(item['mail'])},
                'firstname': {'S': str(item['firstname'])},
                'createdAt': {'N': str(int(item['created_at'].timestamp()))},
                'info': {'M': {
                    'phone': {'S': str(item['phone'])},
                    'randomInfoA': {'S': str(item['random_infoA'])},
                    'randomInfoB': {'S': str(item['random_infoB'])},
                    'randomInfoC': {'S': str(item['random_infoC'])},
                }
                }
            }
        }
    }}
    return student_remodel


def merge_ddb_items(items_to_merge) -> dict:
    """
    Add all items_to_merge in to one dict[DYNAMODB_TABLE] list. To match the batch write requirements.
    """
    student_list = {DYNAMODB_TABLE: []}
    for i in items_to_merge:
        student_list[DYNAMODB_TABLE].append(i[DYNAMODB_TABLE])
    return student_list


def get_batch_of_n_items(item, n):
    """
    Create list of chunks with n number of items in each.
    """
    items = list(item)
    batch = []
    while len(items) != 0:
        batch.append(items[0:n])
        del items[0:n]
    return batch


if __name__ == "__main__":
    DDB_BATCH_QUERY_SIZE = 25
    students_from_sql = database_select_query(query="SELECT * FROM student;")
    students = map(convert_sql2ddb, students_from_sql)
    start = datetime.now()
    number_of_students = 0
    for batch_of_students in get_batch_of_n_items(students, DDB_BATCH_QUERY_SIZE):
        ts = time.time()
        timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        ddb_compatible_batch_write = merge_ddb_items(batch_of_students)
        ddb_batch_write(ddb_compatible_batch_write)
        number_of_students += len(ddb_compatible_batch_write[DYNAMODB_TABLE])
        print("{0}: ({1}) students sent to AWS DynamoDB Batch write".format(timestamp, number_of_students))
        time.sleep(1)
    print("Time to complete batch write: {0}".format(datetime.now() - start))
