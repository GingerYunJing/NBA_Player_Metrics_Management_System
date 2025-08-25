import os
import pandas as pd
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import argparse

# MySQL connection details
username = 'root'
host = 'localhost'
port = '3306'  # Default MySQL port

# Paths for data shards
data_paths = {
    'nba_0': [
        ('all_draft_picks', 'for_import_data/0/all_draft_picks.csv'),
        ('current_players', 'for_import_data/0/current_players.csv'),
        ('all_players_season_stats_2023_2024', 'for_import_data/0/all_players_season_stats_2023_2024.csv'),
        ('player_info', 'for_import_data/0/player_info.csv')
    ],
    'nba_1': [
        ('all_draft_picks', 'for_import_data/1/all_draft_picks.csv'),
        ('current_players', 'for_import_data/1/current_players.csv'),
        ('all_players_season_stats_2023_2024', 'for_import_data/1/all_players_season_stats_2023_2024.csv'),
        ('player_info', 'for_import_data/1/player_info.csv')
    ]
}

def create_databases():
    """Create databases if they do not exist."""
    try:
        engine = sqlalchemy.create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/')
        connection = engine.raw_connection()
        cur = connection.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS nba_0;")
        cur.execute("CREATE DATABASE IF NOT EXISTS nba_1;")
        print("Databases nba_0 and nba_1 created successfully.")
    except SQLAlchemyError as e:
        print(f"Failed to create databases: {e}")

def get_engine(db_name):
    """Create and return SQLAlchemy engine for the given database."""
    return sqlalchemy.create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}')

def execute_sql_file(file_path, db_name):
    """Execute SQL commands from a file in the given database."""
    engine = get_engine(db_name)
    try:
        connection = engine.raw_connection()
        try:
            cursor = connection.cursor()
            with open(file_path, 'r') as file:
                schema_sql = file.read()
            commands = schema_sql.split(';')
            for command in commands:
                if command.strip():
                    cursor.execute(command.strip())  # Execute command directly
            connection.commit()  # Commit the transaction
            print(f"SQL file executed successfully in database {db_name}.")
        finally:
            cursor.close()
    except SQLAlchemyError as e:
        print(f"An error occurred executing SQL in database {db_name}: {e}")
    finally:
        connection.close()


def import_data(db_name, table_name, file_path, engine):
    """Import data from CSV file to specified table in the database."""
    try:
        data = pd.read_csv(file_path, delimiter=';')  # Ensure delimiter matches your CSV format
        data.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"Data from {file_path} imported into {table_name} in {db_name}.")
    except IntegrityError as e:
        print(f"Duplicate entry error during data import for {db_name}: {e}")
    except SQLAlchemyError as e:
        print(f"An error occurred during data import for {db_name}: {e}")

def main():
    parser = argparse.ArgumentParser(description='insert initial data into MySQL databases')
    parser.add_argument('password', type=str, help='password for MySQL root user')
    args = parser.parse_args()
    global password
    password = args.password
    
    create_databases()  # Ensure databases are created first
    for db, paths in data_paths.items():
        execute_sql_file('schema.sql', db)
        engine = get_engine(db)
        for table_name, file_path in paths:
            import_data(db, table_name, file_path, engine)
    print("All operations completed.")

if __name__ == "__main__":
    main()
