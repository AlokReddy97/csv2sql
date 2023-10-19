import os
import datetime
import csv
import sys
import pandas as pd 
import os
import os
import re

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
        if file_extension in ['.xls']:
            with open(filename, 'rb') as file:
                df_list = pd.read_html(file, skiprows=[0], header=0)
                df = pd.DataFrame(df_list[0])
                print(df)
        elif file_extension in ['.xlsx']:
            df = pd.read_excel(filename)
        elif file_extension == '.csv':
            # Try reading with multiple encodings
            encodings_to_try = ['utf-8','ISO-8859-1']
            for encoding in encodings_to_try:
                try:
                    df = pd.read_csv(filename, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"Error: Failed to read the file with all supported encodings.")
                df = pd.DataFrame()  # Return an empty DataFrame in case of error
        else:
            print(f"Error: Unsupported file format '{file_extension}'.")
            return
    except Exception as e:
        print(f"Error: {str(e)}")
        df = pd.DataFrame()  # Return an empty DataFrame in case of error
    
    # Create the output CSV filename
    output_filename = f"{os.path.splitext(filename)[0]}.csv"
    
    # Save the DataFrame to CSV with headers and without the index
    df.to_csv(output_filename, index=False)
    
    print(f"File '{filename}' converted to CSV and saved as '{output_filename}'.")

    return output_filename


filename = sys.argv[1]

convert_to_csv(filename)
