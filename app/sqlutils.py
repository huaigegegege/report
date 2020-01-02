import pyodbc
from app.models import *

class SqlUtils(object):
    """description of class"""
    
    _driver='DRIVER={ODBC Driver 13 for SQL Server};SERVER=mmpreport-sql-prod-cnn.database.chinacloudapi.cn;DATABASE=cn-impc-prod;UID=telemetry_ro;PWD=1)$HGzlwq'

    @classmethod
    def _connection(cls):
        return pyodbc.connect(cls._driver)
    
    @classmethod
    def query(cls, sql):
        conn = cls._connection()
        cur = conn.cursor()
        cur.execute(sql)
        res_list = cur.fetchall()
        cur.close()
        conn.close()
        return res_list

    @classmethod
    def all_publisher(cls):
        list_publisherid=[]
        list_public_publisherid=[]
        for ch in publisher.objects.all():
            list_publisherid.append(ch.publisher_id)
            list_public_publisherid.append(ch.public_publisher_id)
        return {
            'publisher_id':list_publisherid,
            'public_publisher_id':list_public_publisherid
        }
