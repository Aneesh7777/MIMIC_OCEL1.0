import pandas as pd
from sqlalchemy import create_engine

# Define MySQL database connection parameters
db_username = 'your_username'
db_password = 'your_password'
db_host = 'localhost'
db_port = '3306'
db_name = 'your_database_name'

# Create a SQLAlchemy engine to connect to the MySQL database
engine = create_engine(f'mysql+mysqlconnector://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')

# CSV file path
csv_file_path = 'your_csv_file.csv'

# Chunk size for reading CSV file
chunk_size = 1000

# Function to upload CSV in chunks to MySQL
def upload_csv_to_mysql(csv_file_path, engine, chunk_size):
    for chunk in pd.read_csv(csv_file_path, chunksize=chunk_size):
        # Adjust table_name based on your MySQL table name
        chunk.to_sql(name='your_table_name', con=engine, if_exists='append', index=False)

# Upload CSV to MySQL
upload_csv_to_mysql(csv_file_path, engine, chunk_size)
