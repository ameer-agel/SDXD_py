import os
import pymysql


def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "sdxd-600d9b6-sdxd-0a92.h.aivencloud.com"),
        user=os.getenv("DB_USER", "avnadmin"),
        password=os.getenv("DB_PASSWORD", "AVNS_sdMBiUIUBAoE2JmHVqO"),
        database=os.getenv("DB_NAME", "SDXD"),
        port=int(os.getenv("DB_PORT", 26352)),
        cursorclass=pymysql.cursors.DictCursor,
    )