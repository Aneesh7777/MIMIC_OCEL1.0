import pymysql

# database connection
connection = pymysql.connect(host="localhost", port=3306, user="root", passwd="", database="mimic")
cursor = connection.cursor()
# some other statements  with the help of cursor
connection.close()

