import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import numpy as np

database = r"relation.db"


def create_connection(db_file=':memory:'):
    connect_conn = None
    try:
        connect_conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return connect_conn


conn = create_connection(database)

with conn:
    print("Connected")
