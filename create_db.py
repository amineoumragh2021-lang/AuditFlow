import pymysql
conn = pymysql.connect(host="127.0.0.1", user="root", password="", port=3306)
conn.autocommit(True)
cur = conn.cursor()
name = "audit_pfa_db_copy"
cur.execute("CREATE DATABASE IF NOT EXISTS `%s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" % name)
print("CREATED", name)
cur.close()
conn.close()
