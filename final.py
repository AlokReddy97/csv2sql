import os
import sys
import subprocess

def run_csv2sql_for_folder(folder_path):
    # Get a list of all files in the folder
    files = os.listdir(folder_path)

    # Loop through each file in the folder
    for file in files:
        # Check if the file has either the ".xls" or ".csv" extension
        if file.lower().endswith((".xls", ".xlsx", ".csv")):
            # Build the command to run the script for each file
            command = f"python3 csv2sql.py {os.path.join(folder_path, file)}"
            print(command)
            # Use subprocess to run the command
            subprocess.run(command, shell=True)

if __name__ == "__main__":
    # Check if the folder path is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python3 final.py folder_path")
        sys.exit(1)

    # Get the folder path from the command-line arguments
    folder_path = sys.argv[1]

    # Check if the provided path is a valid folder
    if not os.path.isdir(folder_path):
        print(f"Error: The provided path '{folder_path}' is not a valid folder.")
        sys.exit(1)

    # Call the function to run csv2sql.py for all files in the folder
    run_csv2sql_for_folder(folder_path)
