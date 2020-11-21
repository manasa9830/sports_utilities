from decimal import Decimal
import pymysql
from flask import jsonify
import base64

def query(querystr, return_json=True):
    connection= pymysql.connect(
                                host='database-1.cf7kegqq7k9u.us-east-2.rds.amazonaws.com',
                                user='admin',
                                password='manasamotepalli',
                                db='sports_utilities',
        cursorclass=pymysql.cursors.DictCursor

    )
    connection.begin()
    cursor=connection.cursor()
    cursor.execute(querystr)
    result= encode(cursor.fetchall())
    connection.commit()
    cursor.close()
    connection.close()
    if return_json:
        return jsonify(result)
    else:
        return result

def getBase64Str(value):
    return base64.b64encode(value).decode('utf-8')

def encode(data):
    for row in data:
        for key,value in row.items():
            if isinstance(value, Decimal):
                row[key]=str(value)
            elif isinstance(value, bytes):
                row[key] = getBase64Str(value)
    return data
