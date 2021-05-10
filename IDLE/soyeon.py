"""SQL interface module. Read, Write, and Update routines."""
import mysql.connector
import pandas as pd
from mysql.connector import Error
import minnie

def pull(file,cursor):
    query = minnie.ez_read(file)
    try:
        cursor.execute(query)
        #print('Executed Query')
        result = cursor.fetchall()
    except Exception as e:
        print(repr(e))
    return result

def opn(host_name, user_name, user_password, db_name):
    """Here is an example use: cnx = soyeon.opn("127.0.0.1", "root", "J@Y@Hr0m", "<@@@DATABASE@@@>").
    
    Follow this with:
    cursor = cnx.cursor()
    
    Sandwich your sql queries with a mandatory:
    cnx.commit()
    cursor.close()
    cnx.close()
    
    Don't forget about the power of frequent commits."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection