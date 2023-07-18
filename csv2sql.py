import os
import datetime
import csv
import sys
import pandas as pd 
import os
import os
import re

def trimcsv(filename, num_lines):
    # Read the input file and skip the specified number of lines
    with open(filename, 'r') as f:
        lines = f.readlines()[num_lines:]

    # Write the remaining lines to the output file
    with open(filename, 'w') as f:
        f.writelines(lines)

    print(f"{num_lines} lines removed from {filename}.")


def remove_duplicates(file_name):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_name)

    # Find duplicate rows
    duplicate_rows = df[df.duplicated()]

    if not duplicate_rows.empty:
        print("Duplicate rows found:")
        print(duplicate_rows)
        print("------------------------------------------------------------------------------------------------")
        # Ask for user confirmation before deleting duplicate rows
        confirm = input("Do you want to delete these duplicate rows? Press 1 to confirm, any other key to skip: ")
        if confirm == "1":
            # Remove duplicate rows
            df.drop_duplicates(inplace=True)

            # Write the modified DataFrame back to the CSV file
            df.to_csv(file_name, index=False)

            print("Duplicate rows removed and file updated successfully.")
        else:
            print("Duplicate rows were not deleted. Proceeding without removing duplicates.")
    else:
        print("No duplicate rows found. File remains unchanged.")



def increment_duplicate_columns(csv_filename):
    # Check if file exists
    if not os.path.isfile(csv_filename):
        print(f"Error: File '{csv_filename}' does not exist")
        return

    # Read the CSV file
    rows = []
    with open(csv_filename, 'r') as file:
        csv_reader = csv.reader(file)
        rows = [row for row in csv_reader]

    # Get the header row
    header_row = rows[0]

    # print("header row is "+str(header_row))
    # Count the occurrences of each processed column name
    header_counts = {}
    processed_headers = []
    for header in header_row:
        processed_header = re.sub(r'[^A-Za-z0-9]', '', header.strip().replace("'", ""))
        # print(processed_header)
        if processed_header in header_counts:
            header_counts[processed_header] += 1
            processed_header = processed_header + str(header_counts[processed_header])
        else:
            header_counts[processed_header] = 1
        processed_headers.append(processed_header)

    # print("------------")
    # print(processed_headers)
    print("------------------------------------------------------------------------------------------------")
    # Modify column names for duplicates
    for i, header in enumerate(header_row):
        header_row[i] = processed_headers[i]

    # rows[0]=header_row

    with open(csv_filename, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(rows)
    # Write the modified data back to the CSV file
    # with open(csv_filename, 'w', newline='') as file:
    #     csv_writer = csv.writer(file)
    #     csv_writer.writerows(rows)

def filter_csv_rows(filename, output_filename, threshold):
    skipped_rows = []
    filtered_rows = []

    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        for i, row in enumerate(csv_reader):
            non_null_count = sum(field != '' for field in row)
            non_null_percentage = non_null_count / len(row)
            if non_null_percentage >= threshold:
                filtered_rows.append(row)
            else:
                skipped_rows.append((i + 1, len(row), non_null_percentage, row))

    if skipped_rows:
        print("Skipped rows:")
        for row_info in skipped_rows:
            row_index, num_fields, percentage, row_data = row_info
            print(f"Row {row_index}: Fields: {num_fields}, Non-null fields percentage: {percentage:.2%}")
            print(f"Row data: {row_data}")

        confirm = input("Do you want to skip all these rows? Press 1 to confirm, any other key to exit without saving: ")
        if confirm == "1":
            print("Saving filtered rows...")
            with open(output_filename, 'w', newline='') as output_file:
                csv_writer = csv.writer(output_file)
                csv_writer.writerows(filtered_rows)
            print(f"Filtered rows saved to {output_filename}")
        else:
            print("Exiting without saving...")
            sys.exit()

def process_csv_file(filename, n=4):
    # Check if file exists
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' does not exist")
        return
    
    # Open the file
    with open(filename, 'r') as file:
        # Initialize variables to store the maximum column count and the rows with that count
        max_columns = 0
        max_rows = []

        # Iterate over each line in the file
        for line in file:
            # Count the number of commas in the line
            comma_count = line.count(',')
            # If the number of commas is greater than the current maximum column count,
            # update the maximum column count and reset the rows with that count
            if comma_count > max_columns:
                max_columns = comma_count
                max_rows = [line]
            # If the number of commas is equal to the current maximum column count,
            # add the row to the list of rows with that count
            elif comma_count == max_columns:
                max_rows.append(line)

    # Get current timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # Create processed folder if it doesn't exist
    if not os.path.exists('processed'):
        os.makedirs('processed')

    # Create a folder with the name of the CSV file in the processed folder if it doesn't exist
    foldername = os.path.splitext(filename)[0]
    if not os.path.exists(f'processed/{foldername}'):
        os.makedirs(f'processed/{foldername}')

    processed_filename = f'processed/{foldername}/{os.path.splitext(filename)[0]}_{timestamp}.csv'

    with open(processed_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        with open(filename, 'r') as file1:
            reader = csv.reader(file1)
            for row in reader:
                comma_count = len(row) - 1  # Count the commas based on the number of elements in the row
                if n <= comma_count <= max_columns:
                    # Strip extra spaces and double quotes from each value and write to the new CSV file
                    cleaned_row = [value.strip().strip('"') for value in row]
                    writer.writerow(cleaned_row)

    with open(processed_filename, 'r') as file:
        csv_reader = csv.reader(file)
        rows = [row for row in csv_reader]
    
    with open(processed_filename, 'w') as file:
        csv_writer = csv.writer(file)
        if rows: # check if rows list is not empty
            # Modify the first row by removing extra spaces and $ symbol
            first_row = [col.replace(' ', '').strip('"').replace('$', '').replace('(', '').replace('.','').replace('?','').replace(')', '').replace("'","").lower() for col in rows[0]]
            # print("Alok first row")
            # print(first_row)
            csv_writer.writerow(first_row)
            # Write the remaining rows back to the file
            for row in rows[1:]:
                csv_writer.writerow(row)
        else:
            print(f"Error: File '{processed_filename}' is empty.")
            sys.exit(1)

    increment_duplicate_columns(processed_filename)

    #remove duplicate rows
    remove_duplicates(processed_filename)
    # Print confirmation message
    print(f"CSV file '{filename}' processed successfully and saved as '{processed_filename}'.")
    print("------------------------------------------------------------------------------------------------")

if len(sys.argv) < 2:
    print("Error: Please provide the CSV filename as an argument.")
    sys.exit(1)

filename = sys.argv[1]
n = 5  # Default value for n if not provided in sys arguments
num_lines = 0  # Default value for num_lines if not provided in sys arguments
# print(type(filename))
if len(sys.argv) >= 3:
    n = int(sys.argv[2])

if len(sys.argv) >= 4:
    num_lines = int(sys.argv[3])

def convert_to_csv(filename):
    # Check if the file exists
    filename = filename.lower()
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' does not exist")
        return
    
    # Check if the file extension is XLS, XLSX, or CSV
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension not in ['.xls', '.xlsx', '.csv']:
        print(f"Error: Invalid file format. Only XLS, XLSX, and CSV files are supported.")
        return
    
    # Read the file based on its extension
    try:
        if file_extension in ['.xls', '.xlsx']:
            with open(filename, 'rb') as file:
                df_list = pd.read_html(file, skiprows=[0])
                df = pd.DataFrame(df_list[0])
        elif file_extension == '.csv':
            df = pd.read_csv(filename)
        else:
            print(f"Error: Unsupported file format '{file_extension}'.")
            return
    except Exception as e:
        print(f"Error: Failed to read the file. {str(e)}")
        return
    
    # Create the output CSV filename
    output_filename = f"{os.path.splitext(filename)[0]}.csv"
    
    # Save the DataFrame to CSV
    df.to_csv(output_filename, index=False)
    
    print(f"File '{filename}' converted to CSV and saved as '{output_filename}'.")

    return output_filename


filename=convert_to_csv(filename)

# filename = 'hr.csv'  # Replace with the actual filename
# output_filename = 'filtered_rows.csv'  # Replace with the desired output filename
threshold = 0.03  # Threshold for non-null fields percentage

filter_csv_rows(filename, filename, threshold)

# Process the specified CSV file
# trimcsv(filename, num_lines)

print(f"Updated file saved as {filename}.")

# # Print the first 5 lines from the updated CSV file
# with open(filename, 'r') as f:
#     lines = f.readlines()

# print("First 5 lines from the updated CSV file:")
# for line in lines[:5]:
#     print(line.strip())

# Process the specified CSV file
process_csv_file(filename, n)
#n is no of commas we are considering 

# from compare_csv_diff import compare_csv_files
from compare_csvdiff import compare_csv_files

# headers_match = compare_csv_files(filename)

no_archive_file, header_matching = compare_csv_files(filename)

print("There is no Archive file :",no_archive_file)
print("The headers of both archive file and processed file are matching:",header_matching)
print("------------------------------------------------------------------------------------------------")
from sqlcsv import create_table

# create_table(filename, no_archive_file=False)

# if no_archive_file:
create_table(filename,no_archive_file)
    

