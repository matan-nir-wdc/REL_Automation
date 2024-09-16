import os


def delete_files(root_folder):
    # Walk through every directory and subdirectory
    for dirpath, dirnames, filenames in os.walk(root_folder):
        # Check if 'FAST_SCAN.csv' is in the current directory
        if 'FAST_SCAN.csv' in filenames:
            file_path_csv = os.path.join(dirpath, 'FAST_SCAN.csv')
            try:
                # Remove the FAST_SCAN.csv file
                os.remove(file_path_csv)
                print(f"Deleted: {file_path_csv}")

                # Delete all .txt files in the same directory
                for filename in filenames:
                    if filename.endswith('.txt'):
                        file_path_txt = os.path.join(dirpath, filename)
                        os.remove(file_path_txt)
                        print(f"Deleted: {file_path_txt}")

            except Exception as e:
                print(f"Failed to delete {file_path_csv} or .txt files: {e}")


# Example usage
root_folder = '\\\\10.24.8.10\\tfnrel\\Logs\\Ophelia'  # Change this to your root directory
delete_files(root_folder)
