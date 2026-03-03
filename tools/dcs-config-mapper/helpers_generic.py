# Constants
DEBUG = False
NO_ACTION = False


def print_debug(value):  
    """"
    Prints debug messages if DEBUG is enabled.

        Args:
            value (str): The value to be printed if DEBUG is enabled

        Returns:
            None
    """
    DEBUG and print(value)  


def get_abs_pathnames(filename, path):
    """"
    Ensure file exists and return absolute path

        Args:
            filename (str): The name of the file to be checked
            path (str, optional): The path to the directory where the file is expected to be located.
                If not provided, the current script directory is used.

        Returns:
            file_path_abs (str): The absolute path of the file
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if (path):
        file_path_abs = os.path.join(path, filename)
    else:
        file_path_abs = os.path.join(current_dir, filename)

    print_debug(f"File exists: {file_path_abs}")

    return file_path_abs



def delete_files_by_extension(folder_path, target_extension):
    """
    Deletes all files with a specific extension within the specified folder.
    
        Example Usage
            delete_files_by_extension('/path/to/your/folder', '.log')
                OR
            delete_files_by_extension('/path/to/your/folder', 'temp')

        Args:
            folder_path (str): The path to the folder from which files will be deleted.
            target_extension (str): The file extension of files to be deleted (e.g., '.log', '.tmp').   

        Returns:
            None
    """
    # Ensure the extension starts with a dot for consistent comparison (e.g., '.txt')
    if not target_extension.startswith('.'):
        target_extension = '.' + target_extension
        
    # Validate the path
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory or does not exist.")
        return
    
    deleted_count = 0
    
    # Get a list of all items in the directory
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Check if the item is a file AND has the target extension
        if os.path.isfile(file_path):
            # Use os.path.splitext() to reliably get the extension
            _, ext = os.path.splitext(filename)
            
            if ext.lower() == target_extension.lower():
                try:
                    # 4. Delete the file
                    os.remove(file_path)
                    print_debug(f"Deleted file: {filename}")
                    deleted_count += 1
                except OSError as e:
                    print(f"Error deleting file {filename}: {e}")

    print(f"\nFinished. Deleted {deleted_count} file(s) with extension '{target_extension}'.")



def copy_files_by_extension(source_folder: str, target_folder: str, extension: str):
    """
    Copies all files with a specified extension from a source folder to a target folder.

    The extension should be provided without the leading dot (e.g., 'txt', 'pdf').

        Args:
            source_folder (str): The path to the folder containing the files to be copied.
            target_folder (str): The path to the destination folder.
            extension (str): The file extension (e.g., 'log', 'jpg').

        Returns:
            copied_count (int): The number of files successfully copied.
    """
    # Ensure the destination folder exists; create it if necessary
    os.makedirs(target_folder, exist_ok=True)
    
    # Add a leading dot to the extension for matching
    pattern = f".{extension.lstrip('.')}"
    
    print(f"Starting copy process for files with extension '{pattern}'...")
    
    copied_count = 0
    
    # Iterate through all items in the source folder
    for filename in os.listdir(source_folder):
        source_path = os.path.join(source_folder, filename)
        
        # Check if the item is a file AND matches the extension
        if os.path.isfile(source_path) and filename.endswith(pattern):
            
            # Define the full path for the destination file
            target_path = os.path.join(target_folder, filename)
            
            shutil.copy2(source_path, target_path)
            copied_count += 1
            print_debug(f"  -> Copied: {filename}")

    print(f"\nCopy process finished. Total files copied: {copied_count}")

    return copied_count

# --- Example Usage ---
# Setting up dummy directories and files for testing
# os.makedirs('source_data', exist_ok=True)
# os.makedirs('destination_archive', exist_ok=True)
# with open('source_data/doc1.txt', 'w') as f: f.write("Text 1")
# with open('source_data/logA.log', 'w') as f: f.write("Log 1")
# with open('source_data/doc2.txt', 'w') as f: f.write("Text 2")
# with open('source_data/ignore.ini', 'w') as f: f.write("Config")
# with open('source_data/logB.log', 'w') as f: f.write("Log 2")

# Example: Copying all '.log' files
# copy_files_by_extension('source_data', 'destination_archive', 'log')