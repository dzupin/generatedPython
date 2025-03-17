#!/usr/bin/env python3
"""
Git Repository Management Script

This script clones or pulls code from a Git repository based on configuration
parameters from a file or command line arguments.
"""

import os
import shutil
import subprocess
import argparse
import sys
from subprocess import CalledProcessError

# Configuration constants
INPUT_FILE_PATH = '/QA/generatedPython/git_repo_params.txt'
REFERENCED_DIRECTORY = '/QA/EZTRV116QA'  # Fixed location expected by SHATU

# Default configuration values
DEFAULT_CONFIG = {
    'directory_location': '/QA/EZTRV116QA',
    'git_repository': 'git@github.gwd.broadcom.net:EASYTAT01/EZTRV116QA.git',
    'branch': 'master',
    'overwrite_existing_directory': 'false'
}


def clone_or_pull_code(directory, repo_url, branch):
    """
    Clone a Git repository or pull latest changes if it already exists.

    Args:
        directory (str): Target directory for the repository
        repo_url (str): URL of the Git repository
        branch (str): Branch name to checkout

    Returns:
        bool: True if operation succeeded, False otherwise
    """
    git_dir = os.path.join(directory, '.git')

    # Check if directory exists but is not a git repository
    if os.path.exists(directory) and not os.path.exists(git_dir):
        print(f"Directory exists but is not a git repository: {directory}")
        print("Please use --forced=true to overwrite or specify a different directory")
        return False

    if os.path.exists(git_dir):
        print(f"Pulling latest code from {directory} on branch {branch}")
        try:
            subprocess.run(['git', 'checkout', branch], cwd=directory, check=True)
            subprocess.run(['git', 'pull'], cwd=directory, check=True)
            return True
        except CalledProcessError as e:
            print(f"Error pulling code: {e}")
            return False
    else:
        print(f"Cloning repository from {repo_url} to {directory} on branch {branch}")
        try:
            # Create parent directory if it doesn't exist
            parent_dir = os.path.dirname(directory)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            # Use the directory name as the target for git clone
            repo_name = os.path.basename(directory)
            subprocess.run(['git', 'clone', '-b', branch, repo_url, repo_name],
                           cwd=parent_dir, check=True)
            return True
        except CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            return False


def load_config_from_file(file_path):
    """
    Load configuration from a file.

    Args:
        file_path (str): Path to the configuration file

    Returns:
        dict: Configuration values
    """
    config = DEFAULT_CONFIG.copy()

    try:
        with open(file_path, 'r') as file:
            for line in file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    key = key.strip()
                    value = value.strip().strip("'")

                    # Map file variables to our config dict
                    if key == 'default_directory_location':
                        config['directory_location'] = value
                    elif key == 'default_git_repository_string':
                        config['git_repository'] = value
                    elif key == 'default_branch':
                        config['branch'] = value
                    elif key == 'overwrite_existing_directory':
                        config['overwrite_existing_directory'] = value

        print(f"Loaded configuration: {config}")
        return config
    except FileNotFoundError:
        print(f"Config file not found: {file_path}")
        return config
    except Exception as e:
        print(f"Error reading config file: {e}")
        return config


def rename_directory(source, destination):
    """
    Rename a directory if source and destination are different.

    Args:
        source (str): Source directory path
        destination (str): Destination directory path

    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(source) or not os.path.isdir(source):
        print(f"Directory does not exist: {source}")
        return False

    if source == destination:
        print("Source and destination are the same. Skipping rename.")
        return True

    # If destination exists, remove it first (if we got this far, we're in forced mode)
    if os.path.exists(destination):
        print(f"Removing existing destination directory: {destination}")
        shutil.rmtree(destination)

    try:
        # Make sure parent directory exists
        parent_dir = os.path.dirname(destination)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Move the directory
        shutil.move(source, destination)
        print(f"Directory renamed: {source} → {destination}")
        return True
    except Exception as e:
        print(f"Error renaming directory: {e}")
        return False


def main():
    """Main function to execute the script logic."""
    # Load configuration from file
    config = load_config_from_file(INPUT_FILE_PATH)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Clone or pull a Git repository.')
    parser.add_argument('--directory', '-d', default=config['directory_location'],
                        help=f'Target directory (default: {config["directory_location"]})')
    parser.add_argument('--repository', '-r', default=config['git_repository'],
                        help=f'Git repository URL (default: {config["git_repository"]})')
    parser.add_argument('--branch', '-b', default=config['branch'],
                        help=f'Git branch (default: {config["branch"]})')
    parser.add_argument('--forced', '-f', default=config['overwrite_existing_directory'],
                        help=f'Force delete existing directory (default: {config["overwrite_existing_directory"]})')

    args = parser.parse_args()

    print(f"Using directory: {args.directory}")
    print(f"Using repository: {args.repository}")
    print(f"Using branch: {args.branch}")
    print(f"Forced mode: {args.forced}")

    # Check and clean directories if forced flag is set to true
    if args.forced.lower() == 'true':
        # Clean both the target directory and referenced directory if they exist
        for dir_path in [args.directory, REFERENCED_DIRECTORY]:
            if os.path.exists(dir_path):
                print(f"Forced mode: Deleting existing directory: {dir_path}")
                shutil.rmtree(dir_path)

    # Clone or pull the repository
    if not clone_or_pull_code(args.directory, args.repository, args.branch):
        print("Git operation failed")
        sys.exit(1)
    else:
        print("Git operation completed successfully")

    # Rename directory if needed
    if not rename_directory(args.directory, REFERENCED_DIRECTORY):
        print("Directory rename operation failed")
        sys.exit(1)
    else:
        print("Script completed successfully")


if __name__ == "__main__":
    main()
