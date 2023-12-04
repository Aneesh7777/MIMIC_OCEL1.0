import pymysql

# database connection
db_connection = pymysql.connect(host="localhost", port=3306, user="root", passwd="", database="mimicdemo")
db_cursor = db_connection.cursor()
table_name='admissions'
id_type="hadm_id"



# s='select ' +  table_name + '.* from ' + table_name + ' join (values {0}) as to_join(' + id_type + ') ON ' + table_name + '.' + id_type + ' = to_join.' + id_type
s="select * from admissions "
import pandas as pd
db_cursor.execute(s)
adm=db_cursor.fetchall()
cols = list(map(lambda x: x[0], db_cursor.description))
d = pd.DataFrame(adm, columns=cols)
print(cols)
print(d.head)


# def extract_admissions_for_admission_ids(db_cursor: cursor,
#                                          hospital_admission_ids: List) -> pd.DataFrame:
#     """Extract admissions for a list of hospital admission ids"""
#     sql_id_list = prepare_id_list_for_sql(hospital_admission_ids)
#     sql_query = build_sql_query( "admissions", "hadm_id")
#     db_cursor.execute(sql_query.format(sql_id_list))
#     adm = db_cursor.fetchall()
#     cols = list(map(lambda x: x[0], db_cursor.description))
#     return pd.DataFrame(adm, columns=cols)
