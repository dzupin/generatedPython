import os
import shutil
import subprocess
import argparse
import sys
from subprocess import CalledProcessError

input_file_path = '/QA/JenkinsPipelineJobs/git_repo_params.txt'

# Set default values for directory location and Git repository string
default_directory_location = '/QA/EZTRV116QA'    # path should match / be consistent with git repository name
#default_directory_location = '/QA/EZTRV116'    # path should match / be consistent with git repository name

default_git_repository_string = 'git@github.gwd.broadcom.net:EASYTAT01/EZTRV116QA.git'
#default_git_repository_string = 'git@github.gwd.broadcom.net:EASYTAT01/EZTRV116.git'

default_branch = 'master'  # Default branch name
#default_branch = 'coverity_20220120'  # Coverity baseline of  EZTRV116.git
#default_branch = 'Endevor_Fixes_Coverity_20200120'  # New branch for merged changes of  EZTRV116.git

referenced_directory_location = '/QA/EZTRV116QA'  # Should be constant because SHATU will assume this specific location

# To use default values from command line: python script.py
# To specify directory and repository : python script.py --directory /path/to/your/directory --repository https://github.com/username/repository.git


def clone_or_pull_code(directory, repo_url, branch):
    # Check if the .git directory exists within the specified directory
    git_dir = os.path.join(directory, '.git')
    if os.path.exists(git_dir):
        print(f"Pulling latest code from {directory} on branch {branch}")
        try:
            # Change the current working directory to the repository directory
            subprocess.run(['git', 'checkout', branch], cwd=directory, check=True)
            subprocess.run(['git', 'pull'], cwd=directory, check=True)
            return True
        except CalledProcessError as e:
            print(f"An error occurred while pulling the code: {e}")
            return False
    else:
        print(f"Cloning repository from {repo_url} to {directory} on branch {branch}")
        try:
            # Clone the repository if it does not exist or does not have a .git folder
            subprocess.run(['git', 'clone', '-b', branch, repo_url], cwd=os.path.dirname(directory), check=True)
            return True
        except CalledProcessError as e:
            print(f"An error occurred while cloning the repository: {e}")
            return False

# Read the values from the text file
try:
    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # Assign values to variables if they are defined in the text file
    for line in lines:
        if '=' in line:
            variable_name, value = line.strip().split('=', 1)
            variable_name = variable_name.strip()
            value = value.strip().strip("'")  # Remove single quotes if present

            # Assign the value to the corresponding variable if it exists
            if variable_name == 'default_directory_location':
                globals()[variable_name] = value
            elif variable_name == 'default_git_repository_string':
                globals()[variable_name] = value
            elif variable_name == 'default_branch':
                globals()[variable_name] = value
            elif variable_name == 'processed_directory_location':
                globals()[variable_name] = value

except FileNotFoundError:
    print(f"The input file {input_file_path} was not found.")
except Exception as e:
    print(f"An error occurred while reading the input file: {e}")



# Parse command-line arguments (needed only if command line parameters are specified))
parser = argparse.ArgumentParser(description='Clone or pull a Git repository.')
parser.add_argument('--directory', '-d', default=default_directory_location, help='The directory where the repository will be cloned or pulled. Default is ' + default_directory_location)
parser.add_argument('--repository', '-r', default=default_git_repository_string, help='The URL of the Git repository. Default is ' + default_git_repository_string)
parser.add_argument('--branch', '-b', default=default_branch, help='The branch to clone or pull from. Default is ' + default_branch)

args = parser.parse_args()

# Check if the default directory exists and delete it if it does (to allow different git repos use same directory structure)
if os.path.exists(referenced_directory_location) and os.path.isdir(referenced_directory_location):
    print(f"Deleting directory: {referenced_directory_location}")
    shutil.rmtree(referenced_directory_location)


# Call the function with the parsed arguments
if clone_or_pull_code(args.directory, args.repository, args.branch):
    print("Operation clone_or_pull_code completed successfully.")
else:
    print("Operation clone_or_pull_code failed.")
    sys.exit(1)


# Check if the directory exists and is a directory
if os.path.exists(default_directory_location) and os.path.isdir(default_directory_location):
    # Check if the source and destination are different
    if default_directory_location != referenced_directory_location:
        # Use the subprocess module to call the 'mv' command with the '-T' option
        try:
            subprocess.run(['mv', '-T', default_directory_location, referenced_directory_location], check=True)
            print(f"The directory has been renamed from {default_directory_location} to {referenced_directory_location}.")
        except subprocess.CalledProcessError as e:
            # Handle the error if the source and destination are the same
            if e.returncode == 1 and "same file" in str(e):
                print("Source and destination are the same. Skipping rename operation.")
            else:
                print(f"Error renaming directory: {e}")
    else:
        print("Source and destination are the same. Skipping rename operation.")
else:
    print(f"The directory {default_directory_location} does not exist or is not a directory.")