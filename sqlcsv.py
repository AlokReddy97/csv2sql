import csv
import psycopg2
from decimal import Decimal
import sys 
import datetime
import os
import re

import csv
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values


def get_column_data_types(headers, csvreader):
    data_types = [None for i in range(len(headers))]  # default data type is None
    row_count = 0
    for row in csvreader:
        # print("bbbsbsbbs--------------------------")
        # print(len(row))
        for i, value in enumerate(row):
            if data_types[i] == "TEXT":
                continue  # Skip further processing for "TEXT" data type
            try:
                int(value)
                if float(value).is_integer():
                    data_types[i] = "INTEGER"
                else:
                    data_types[i] = "DECIMAL"
            except (ValueError, TypeError):
                try:
                    float(value.replace("$", "").replace(",", ""))
                    data_types[i] = "DECIMAL"
                except (ValueError, TypeError):
                    data_types[i] = "TEXT"
        row_count += 1
        # print(row_count)
        if row_count > 100:  # check 3 to 4 rows after headers
            print("brokeeen")
            break
        else:
            continue
        if len(row) != len(headers):
            print("chill;")
            continue
    for i in range(len(data_types)):
        if data_types[i] is None:
            data_types[i] = "TEXT"
            # print("444")
    return data_types


def print_column_data_types(headers, data_types):
    print("------------------------------------")
    print("Column # | Column Name | Data Type")
    print("-------- + ------------+ ----------")
    for i, header in enumerate(headers):
        print("{:<8} | {:<12} | {}".format(i+1, header, data_types[i]))
    print("------------------------------------")

def get_primary_key_columns(headers):
    pk_columns = []
    num_pk_columns = int(input("Please enter the number of columns in the primary key: "))
    for i in range(num_pk_columns):
        pk_column = input("Please enter the number of primary key column {} (1-{}): ".format(i+1, len(headers)))
        pk_columns.append(headers[int(pk_column) - 1])
    return pk_columns



def get_primary_key_columns1(cur, conn, table_name):
    """
    Get the primary key column names for a given table.

    Args:
        cur (psycopg2.extensions.cursor): Database cursor object
        conn (psycopg2.extensions.connection): Database connection object
        table_name (str): Name of the table

    Returns:
        pk_columns (list of str): List of primary key column names
    """
    pk_columns = []
    try:
        # Execute the query to get primary key column names
        cur.execute(f"SELECT column_name FROM information_schema.key_column_usage WHERE table_name = '{table_name}' AND constraint_name LIKE '%_pkey'")

        # Fetch the results
        results = cur.fetchall()

        # Extract the column names from the results
        pk_columns = [result[0] for result in results]

    except Exception as e:
        print(f"Error: {e}")

    # Return the list of primary key column names
    return pk_columns

import re

# def replace_ordinal_numbers(column_name):
#     # Replace ordinal numbers
#     ordinal_mapping = {
#         "1st": "first",
#         "2nd": "second",
#         "3rd": "third",
#         "4th": "fourth",
#         "5th": "fifth",
#         "6th": "sixth",
#         "7th": "seventh",
#         "8th": "eighth",
#         "9th": "ninth"
#     }

#     # Check if the first character is a digit and then replace numbers without ordinal indicators
#     if column_name[0].isdigit():
#         column_name = re.sub(r'^(\d+)([a-zA-Z]+)', lambda m: {**{"1": "first", "2": "second", "3": "third", "4": "fourth", "5": "fifth", "6": "sixth", "7": "seventh", "8": "eighth", "9": "ninth"}, **ordinal_mapping}[m.group(1)] + m.group(2), column_name)
#     else:
#         # Check if the first three letters match an ordinal mapping and replace them
#         first_three_letters = column_name[:3]
#         if first_three_letters in ordinal_mapping:
#             column_name = ordinal_mapping[first_three_letters] + column_name[3:]

#     return column_name

def replace_ordinal_numbers(column_name):
    # Replace ordinal numbers
    ordinal_mapping = {
        "1st": "first",
        "2nd": "second",
        "3rd": "third",
        "4th": "fourth",
        "5th": "fifth",
        "6th": "sixth",
        "7th": "seventh",
        "8th": "eighth",
        "9th": "ninth"
    }

    # Check if the first three letters match an ordinal mapping and replace them
    first_three_letters = column_name[:3]
    if first_three_letters in ordinal_mapping:
        column_name = ordinal_mapping[first_three_letters] + column_name[3:]
    else:
        # Check if the first character is a digit and then replace numbers without ordinal indicators
        if column_name[0].isdigit():
            column_name = re.sub(r'^(\d+)([a-zA-Z]+)', lambda m: {**{"1": "first", "2": "second", "3": "third", "4": "fourth", "5": "fifth", "6": "sixth", "7": "seventh", "8": "eighth", "9": "ninth"}, **ordinal_mapping}[m.group(1)] + m.group(2), column_name)

    return column_name



# def create_table(filename, no_archive_file=False):
    current_file_folder_name = os.path.splitext(filename)[0]

    # Set the folder path for the CSV file in the processed folder
    processed_folder = os.path.join('processed', current_file_folder_name)
    print(f"Processed folder '{processed_folder}'")
    if not os.path.exists(processed_folder):
        print(f"No processed folder found for '{filename}'")
        return

    try:
        # Get the most recent timestamped CSV file in the processed folder
        processed_filenames = [f for f in os.listdir(processed_folder) if f.endswith('.csv')]
        
        print("Most recently processed csv files")
        print(processed_filenames)
        print("------------------------------------------------------------------------------------------------")
        if not processed_filenames:
            raise ValueError(f"No processed CSV files found in folder '{processed_folder}'")
        latest_processed_filename = max(processed_filenames, key=lambda f: os.path.getmtime(os.path.join(processed_folder, f)))
        processed_filepath = os.path.join(processed_folder, latest_processed_filename)
        print(processed_filepath)
        # conn = psycopg2.connect(database="db1", user="alok", password="reddy", host="localhost", port="5433")
        conn = psycopg2.connect(database="meddb", user="alok", password="reddy", host="localhost", port="5432")
        cur = conn.cursor()

        if no_archive_file and processed_filepath is not None:
            with open(processed_filepath, "r") as csvfile:
                csvreader = csv.reader(csvfile,quoting=csv.QUOTE_ALL, quotechar='"')
                headers = next(csvreader)
                # print(headers)
                headers = [s.strip().replace("'", "") for s in headers]
                headers = [s.strip().replace("/", "") for s in headers]
                headers = [s.strip().replace("-", "") for s in headers]

                # # Example usage with a list of column names
                # column_names = ["2ndconcen", "1school", "3rdcolumn", "4thcolumn", "5concen4", "othercolumn"]
                updated_column_names = []

                for column_name in headers:
                    updated_column_name = replace_ordinal_numbers(column_name)
                    updated_column_names.append(updated_column_name)

                headers=updated_column_names



                # headers = [re.sub(r'[^A-Za-z]', '', s.strip().replace("'", "")) for s in headers]
                # Dictionary to keep track of repeated headers
                from collections import defaultdict
                
                # Dictionary to keep track of repeated headers
                header_counts = defaultdict(int)

                # print(processed_headers)
                # print("----processed ones------")
                # print(processed_headers)
                # print("-------originals ones---")
                # print(headers)
                # headers = processed_headers
                table_name = os.path.splitext(latest_processed_filename)[0]
                table_name = table_name.split('_')[0]
                print("Table NAME :")
                print(table_name)
                # print("Alok test 2323")
                # Determine the data types of each column
                data_types = get_column_data_types(headers, csvreader)
                # print("after the get column data types")
                # print(data_types)
                # Print the data types
                print_column_data_types(headers, data_types)

                # Determine the primary key columns
                pk_columns = get_primary_key_columns(headers)

                pk_constraint = ", ".join(pk_columns)
                create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([header.replace('(', '').replace(')', '') + ' ' + data_types[i] for i, header in enumerate(headers)])}, PRIMARY KEY ({pk_constraint}));"
                print("------------------------------------------------------------------------------------------------")
                print(f"Create Table Query: {create_table_query}")
                print("------------------------------------------------------------------------------------------------")
                confirm = input("Do you want to create the table? Press 1 to confirm, any other key to abort: ")
                if confirm == "1":
                    try:
                        cur.execute(create_table_query)
                        print("Table created successfully! hahaha")
                        conn.commit()
                        print(cur.statusmessage)
                        insert_data_into_table(cur, conn, processed_filepath, headers, data_types, table_name)
                        return True
                    except Exception as e:
                        print("Error occurred while creating table:", e)
                        print(cur.statusmessage)
                        return False
                else:
                    print("Aborted creation")
                    return False
        else:
            print("Archive file is not empty. Table updation is done")
            with open(processed_filepath, "r") as csvfile:
                csvreader = csv.reader(csvfile)
                headers = next(csvreader)
                table_name = os.path.splitext(latest_processed_filename)[0]
                table_name = table_name.split('_')[0]

                # print(table_name)
                # Determine the primary key columns
                pk_columns = get_primary_key_columns1(cur, conn, table_name)
                print("The primary columns are :")
                print(pk_columns)
                update_records(cur, conn, table_name, pk_columns, processed_filepath, data_types=None)
                return False
    except Exception as e:
        print(f"Error occurred: {e}")
        return False


import pandas as pd
from sqlalchemy import create_engine

def create_table(filename, no_archive_file=False):
    current_file_folder_name = os.path.splitext(filename)[0]

    # Set the folder path for the CSV file in the processed folder
    processed_folder = os.path.join('processed', current_file_folder_name)
    print(f"Processed folder '{processed_folder}'")
    if not os.path.exists(processed_folder):
        print(f"No processed folder found for '{filename}'")
        return

    try:
        # Get the most recent timestamped CSV file in the processed folder
        processed_filenames = [f for f in os.listdir(processed_folder) if f.endswith('.csv')]
        
        print("Most recently processed csv files")
        print(processed_filenames)
        print("------------------------------------------------------------------------------------------------")
        if not processed_filenames:
            raise ValueError(f"No processed CSV files found in folder '{processed_folder}'")
        latest_processed_filename = max(processed_filenames, key=lambda f: os.path.getmtime(os.path.join(processed_folder, f)))
        processed_filepath = os.path.join(processed_folder, latest_processed_filename)
        print(processed_filepath)

        # conn = psycopg2.connect(database="db1", user="alok", password="reddy", host="localhost", port="5433")
        conn = psycopg2.connect(database="meddb", user="alok", password="reddy", host="localhost", port="5432")
        cur = conn.cursor()
        if no_archive_file and processed_filepath is not None:
            with open(processed_filepath, "r") as csvfile:
                csvreader = csv.reader(csvfile,quoting=csv.QUOTE_ALL, quotechar='"')
                headers = next(csvreader)
                headers = [s.strip().replace("'", "") for s in headers]
                headers = [s.strip().replace("/", "") for s in headers]
                headers = [s.strip().replace("-", "") for s in headers]

                updated_column_names = [replace_ordinal_numbers(column_name) for column_name in headers]
                headers = updated_column_names
                data_types = get_column_data_types(headers, csvreader)
                # Load CSV data into DataFrame
                print("iiiiiiiiiiiiiiiiiiiiiiiiiiii")
                print_column_data_types(headers, data_types)
                df = pd.read_csv(processed_filepath)
                table_name = os.path.splitext(latest_processed_filename)[0]
                table_name = table_name.split('_')[0]
                print(headers)
                # Determine the primary key columns
                pk_columns = get_primary_key_columns(headers)

                # # Create the table using df.to_sql
                # engine = create_engine('postgresql://alok:reddy@localhost:5432/meddb')
                # df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

                print(f"Table '{table_name}' creation in progress")

                # Insert data into the newly created table
                insert_data_into_table(processed_filepath,headers, data_types, table_name,pk_columns)

                return True
        else:
            print("Archive file is not empty. Table updation is done")
            with open(processed_filepath, "r") as csvfile:
                csvreader = csv.reader(csvfile)
                headers = next(csvreader)
                headers = [s.strip().replace("'", "") for s in headers]
                headers = [s.strip().replace("/", "") for s in headers]
                headers = [s.strip().replace("-", "") for s in headers]

                updated_column_names = [replace_ordinal_numbers(column_name) for column_name in headers]
                headers = updated_column_names


                table_name = os.path.splitext(latest_processed_filename)[0]
                table_name = table_name.split('_')[0]
                

                print(table_name)
                # Determine the primary key columns
                pk_columns = get_primary_key_columns1(cur, conn, table_name)
                print("The primary columns are :")
                print(pk_columns)
                update_records(table_name, pk_columns, processed_filepath,headers)
                return False
    except Exception as e:
        print(f"Error occurred: {e}")
        return False


def insert_data_into_table(filename, headers, data_types, table_name, pk_columns):
    # Convert column names to lower case
    print("----------------- IN INSERT FUNCTION -----------------")
    headers_lower = [header.lower() for header in headers]

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(filename, quotechar='"', quoting=csv.QUOTE_ALL)

    # Convert data types as needed
    for i, header in enumerate(headers):
        if data_types[i] == "INTEGER":
            df[header] = pd.to_numeric(df[header], errors="coerce")
        elif data_types[i] == "DECIMAL":
            df[header] = df[header].replace({"$": "", ",": ""}, regex=True).astype(float)
    
    # Replace ordinal numbers in column names
    df.columns = [replace_ordinal_numbers(col) for col in df.columns]

    # Set the primary key columns if provided
    if pk_columns:
        df.set_index(pk_columns, inplace=True)

    # Replace null values with empty strings
    df.fillna('', inplace=True)

    # Create a database connection using SQLAlchemy
    engine = create_engine("postgresql://alok:reddy@localhost:5432/meddb")

    # Convert DataFrame to SQL table using pandas with if_exists='replace' or 'append'
    df.to_sql(table_name, engine, if_exists='replace' if pk_columns else 'append', index=True if pk_columns else False)

    # Add the primary key if pk_columns are provided
    if pk_columns:
        with engine.connect() as con:
            print("creating primary key")
            con.execute(f'ALTER TABLE "{table_name}" ADD PRIMARY KEY ({", ".join(pk_columns)});')

    # Get the number of rows inserted
    rows_inserted = len(df)

    # Print the total number of rows inserted
    print(f"CSV data inserted successfully!")
    print(f"Total rows inserted: {rows_inserted}")
    
    # Archive the CSV file
    archive_csv_file(filename, table_name, headers_lower)


import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.dialects.postgresql import insert

def update_records(table_name, pk_columns, csv_file_path, headers):
    print("----------------- IN UPDATE FUNCTION -----------------")
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file_path)

    # Convert DataFrame columns to lowercase
    df.columns = df.columns.str.lower()

    # Replace ordinal numbers in column names
    df.columns = [replace_ordinal_numbers(col) for col in df.columns]
    # print(df)
    # Create a database connection using SQLAlchemy
    engine = create_engine("postgresql://alok:reddy@localhost:5432/meddb")

    # Define the table object using SQLAlchemy
    metadata = MetaData()
    table = Table(table_name, metadata, *[
        Column(col, String) for col in df.columns
    ])

    # Define the insert statement using the table object
    stmt = insert(table).values(df.to_dict(orient='records'))

    # print(stmt)
    # Specify the conflict resolution for duplicate primary keys
    on_conflict = stmt.on_conflict_do_nothing(index_elements=pk_columns)

    try:
        # Execute the insert statement with conflict resolution
        engine.execute(on_conflict)
            # Archive the CSV file
        archive_csv_file(csv_file_path, table_name, headers)
    except Exception as e:
        print(f"Error occurred: {e}")
        



def archive_csv_file(csv_file_path, table_name, headers_lower):
    # Get current timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Create archived folder if it doesn't exist
    if not os.path.exists('archived'):
        os.makedirs('archived')

    # Create a folder with the name of the CSV file in the archived folder if it doesn't exist
    foldername = os.path.splitext(os.path.basename(csv_file_path))[0]
    foldername = foldername.split('_')[0]
    if not os.path.exists(f'archived/{foldername}'):
        os.makedirs(f'archived/{foldername}')

    # Write the SQL table to a CSV file in the archived folder
    engine = create_engine("postgresql://alok:reddy@localhost:5432/meddb")
    with open(f'archived/{foldername}/{table_name}_{timestamp}.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers_lower)  # Write lower case column names
        with engine.begin() as conn:
            result = conn.execute(f"SELECT * FROM {table_name}")
            for row in result:
                csvwriter.writerow(row)

    print(f"CSV file saved in archived/{foldername}/{table_name}_{timestamp}.csv")





