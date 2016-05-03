#!/usr/bin/python3.4
# -*-coding:Utf-8 -*

import maxminddb

class maxmindDB:
    _db_connection = None

    def __init__(self, params):
        self._db_connection = maxminddb.open_database(params)

    def query(self, params):
        return self._db_connection.get(params)

    def __del__(self):
        self._db_connection.close()
