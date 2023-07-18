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




def insert_data_into_table(cur, conn, filename, headers, data_types, table_name):
    # Convert column names to lower case
    headers_lower = [header.lower() for header in headers]

    with open(filename, "r", newline="") as csvfile:
        csvreader = csv.reader(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)
        next(csvreader)  # Skip the header row
        rows_to_insert = []

        for row in csvreader:
            if len(row) > len(headers):
                row = row[:len(headers)]
            values = []

            for i, value in enumerate(row):
                if data_types[i] == "INTEGER":
                    if value.strip() == '':
                        print(f"Empty string found for INTEGER data type at index {i}. Inserting 0 instead.")
                        values.append(0)
                    else:
                        values.append(int(value))
                elif data_types[i] == "DECIMAL":
                    values.append(Decimal(value.replace("$", "").replace(",", "")))
                else:
                    values.append(value.replace("(", "").replace(")", ""))

            rows_to_insert.append(tuple(values))

        insert_query = sql.SQL("INSERT INTO {table} ({columns}) VALUES %s ON CONFLICT DO NOTHING;").format(
            table=sql.Identifier(table_name),
            columns=sql.SQL(', ').join(map(sql.Identifier, headers_lower))
        )
        print("------------------------------------------------------------------------------------------------")
        confirm = input("Do you want to insert all rows? Press 1 to confirm, any other key to skip: come---on ")
        if confirm == "1":
            try:
                # print(insert_query)
                execute_values(cur, insert_query, rows_to_insert, page_size=1000)
                total_rows_inserted = len(rows_to_insert)  # Get the total number of rows inserted
                print("CSV data inserted successfully!")
                print(f"Total rows inserted: {total_rows_inserted}")
                
                # Get current timestamp
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

                # Create archived folder if it doesn't exist
                if not os.path.exists('archived'):
                    os.makedirs('archived')

                # Create a folder with the name of the CSV file in the archived folder if it doesn't exist
                foldername = os.path.splitext(os.path.basename(filename))[0]
                foldername = foldername.split('_')[0]
                if not os.path.exists(f'archived/{foldername}'):
                    os.makedirs(f'archived/{foldername}')

                # Write the SQL table to a CSV file in the archived folder
                with open(f'archived/{foldername}/{table_name}_{timestamp}.csv', 'w') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow(headers_lower)  # Write lower case column names
                    cur.execute(f"SELECT * FROM {table_name}")
                    rows = cur.fetchall()
                    for row in rows:
                        csvwriter.writerow(row)

                print(f"CSV file saved in archived/{foldername}/{table_name}_{timestamp}.csv")

                # Print an error message if the CSV file is not archived properly
                if not os.path.exists(f'archived/{foldername}/{table_name}_{timestamp}.csv'):
                    print("Error: CSV file not archived properly")

            except Exception as e:
                print("Error occurred while inserting CSV data into the table:", e)
                print(cur.statusmessage)
        else:
            print("Aborted Insertion")
            return False

        # Commit the changes and close the cursor and connection
        conn.commit()
        cur.close()
        conn.close()



def update_records(cur, conn, table_name, pk_columns, csv_file_path, data_types=None):
    # Open CSV file
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        # Initialize counters for rows updated and inserted
        rows_updated = 0
        rows_inserted = 0
        conflicting_records = []

        # Get header row
        headers = next(csv_reader)

        updated_column_names = []
        for column_name in headers:
            updated_column_name = replace_ordinal_numbers(column_name)
            updated_column_names.append(updated_column_name)
        headers=updated_column_names        

        # Loop through each row in the CSV file
        for row in csv_reader:
            # Build SQL query to update record based on primary key columns
            query = sql.SQL("INSERT INTO {table} ({columns}) VALUES ({values}) ON CONFLICT ({conflict_columns}) DO NOTHING RETURNING *;").format(
                table=sql.Identifier(table_name),
                columns=sql.SQL(', ').join(map(sql.Identifier, headers)),
                values=sql.SQL(', ').join([sql.Placeholder()] * len(headers)),
                conflict_columns=sql.SQL(', ').join(map(sql.Identifier, pk_columns))
            )

            # Prepare the values with appropriate data types
            values = []
            for i, value in enumerate(row):
                column = headers[i]
                if data_types and column in data_types and data_types[column] is not None:
                    # If data type is specified, cast the value accordingly
                    values.append(sql.SQL("%s::{}").format(sql.Identifier(data_types[column])).as_string(cur) % value)
                else:
                    # Otherwise, use the value as is
                    values.append(value)

            try:
                cur.execute(query, values)
                if cur.rowcount == 0:
                    conflicting_records.append(row)
                else:
                    rows_inserted += 1
            except psycopg2.IntegrityError:
                conflicting_records.append(row)
            else:
                rows_updated += 1

        print(f"{rows_updated} rows updated and {rows_inserted} rows inserted.")

        if conflicting_records:
            print(f"{len(conflicting_records)} conflicting records:")
            for record in conflicting_records:
                print(record)


            print(f"{len(conflicting_records)} conflicting records:")
            # Ask for confirmation before pushing conflicting records
            confirmation = input("Do you want to push the conflicting records to the database? (yes/no): ")
            if confirmation.lower() == "yes":
                # Push conflicting records to the database
                for record in conflicting_records:
                    try:
                        cur.execute(query, record)
                        rows_inserted += 1
                    except psycopg2.IntegrityError:
                        print(f"Failed to insert conflicting record: {record}")
                    else:
                        rows_updated += 1
                print("Conflicting records inserted.")
            else:
                print("Conflicting records not pushed to the database.")

    # Commit changes
    conn.commit()

    # Get current timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Create archived folder if it doesn't exist
    if not os.path.exists('archived'):
        os.makedirs('archived')

    # Create a folder with the name of the CSV file in the archived folder if it doesn't exist
    foldername = os.path.splitext(os.path.basename(csv_file_path))[0]
    if not os.path.exists(f'archived/{foldername}'):
        os.makedirs(f'archived/{foldername}')

    # Write the SQL table to a CSV file in the archived folder
    with open(f'archived/{foldername}/{table_name}_{timestamp}.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        for row in rows:
            csvwriter.writerow(row)

    print(f"CSV file saved in archived/{foldername}/{table_name}_{timestamp}.csv from update_records.")

    # Close cursor and connection
    cur.close()
    conn.close()






