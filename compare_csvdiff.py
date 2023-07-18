import os
import csv
import subprocess
import pandas as pd
import sys

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




def compare_csv_files(current_filename):
    no_archive_file = False
    header_matching = False
    # Extract the file name from the path
    current_file_folder_name = os.path.splitext(current_filename)[0]

    # Set the folder path for the CSV file in the processed folder
    processed_folder = os.path.join('processed', current_file_folder_name)
    if not os.path.exists(processed_folder):
        print(f"No processed folder found for '{current_filename}'")
        sys.exit(1)

    try:
        # Get the most recent timestamped CSV file in the processed folder
        processed_filenames = [f for f in os.listdir(processed_folder) if f.endswith('.csv')]
        if not processed_filenames:
            raise ValueError(f"No processed CSV files found in folder '{processed_folder}'")
        latest_processed_filename = max(processed_filenames)
        processed_filepath = os.path.join(processed_folder, latest_processed_filename)

    except (FileNotFoundError, ValueError) as e:
        print(str(e))
        sys.exit(1)

    # Assign a default value to archived_filepath
    archived_filepath = None

    try:
        # Get the folder path for the CSV file in the archived folder
        archived_folder = os.path.join('archived', current_file_folder_name.split("_")[0])
        # Get the most recent timestamped CSV file in the archived folder
        archived_filenames = [f for f in os.listdir(archived_folder) if f.endswith('.csv')]
        if not archived_filenames:
            print(f"No archived CSV files found in folder '{archived_folder}'")
            no_archive_file = True
        else:
            latest_archived_filename = max(archived_filenames)
            archived_filepath = os.path.join(archived_folder, latest_archived_filename)

    except (FileNotFoundError, ValueError) as e:
        print(str(e))
        no_archive_file = True

    if not archived_filepath:
        no_archive_file = True

    # Check if headers of both CSV files match
        # Check if headers of both CSV files match
    if archived_filepath is not None:
        with open(processed_filepath, 'r') as f1, open(archived_filepath, 'r') as f2:
            reader1 = csv.reader(f1)
            reader2 = csv.reader(f2)
            headers1 = next(reader1)
            headers2 = next(reader2)

            headers1_lower = [header.lower() for header in headers1]
            headers2_lower = [header.lower() for header in headers2]

            updated_column_names_1 = []

            for column_name in headers1_lower:
                updated_column_name = replace_ordinal_numbers(column_name)
                updated_column_names_1.append(updated_column_name)

            headers1_lower=updated_column_names_1

            updated_column_names_2 = []

            for column_name in headers2_lower:
                updated_column_name = replace_ordinal_numbers(column_name)
                updated_column_names_2.append(updated_column_name)

            headers1_lower=updated_column_names_2



            
            if headers1_lower == headers2_lower:
                print(f"Headers of both CSV files match.")
                print(headers1_lower)
                print(headers2_lower)
                headers_match = True
                header_matching = headers_match
            else:
                print(f"Headers of both CSV files do not match.")
                print(headers1_lower)
                print(headers2_lower)
                headers_match = False
                header_matching = headers_match


        if header_matching:
            # Compare the two CSV files using csv-diff
            diff_cmd = ['csv-diff', processed_folder, archived_filepath]
            diff_result = subprocess.run(diff_cmd, capture_output=True, text=True)
            if len(diff_result.stdout.strip()) == 0:
                print(f"The CSV file '{processed_folder}' is the same as the most recent archived CSV file '{latest_archived_filename}'.")
            else:
                print(f"The CSV file '{processed_folder}' differs from the most recent archived CSV file '{latest_archived_filename}':")
                print(diff_result.stdout)
        else:
            print('Headers are not matching so quitting')
            sys.exit(1)

    return no_archive_file, header_matching


