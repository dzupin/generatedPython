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
INPUT_FILE_PATH = '/QA/pipelineAutomation/git_repo_params.txt'
REFERENCED_DIRECTORY = '/QA/EZTRV116QA'  # Fixed location expected by SHATU

# Default configuration values
DEFAULT_CONFIG = {
    'directory_location': '/QA/EZTRV116QA',
    'git_repository': 'git@github.gwd.broadcom.net:EASYTAT01/EZTRV116QA.git',
    'branch': 'master',
    'overwrite_existing_directory': 'false',
    'debug': 'true'
}


def run_command(command, cwd=None, check=True, debug=True):
    """
    Run a command and print it for visibility if debug is enabled.

    Args:
        command (list): Command to run as a list of strings
        cwd (str): Current working directory
        check (bool): Whether to check return code
        debug (bool): Whether to print command execution details

    Returns:
        subprocess.CompletedProcess: Result of the command
    """
    cmd_str = ' '.join(command)
    working_dir = f" (in {cwd})" if cwd else ""

    if debug:
        print(f"Executing: {cmd_str}{working_dir}")

    return subprocess.run(command, cwd=cwd, check=check, capture_output=True, text=True)


def print_all_branches(directory, debug=True):
    """
    Print all branches in the repository if debug is enabled.

    Args:
        directory (str): Repository directory
        debug (bool): Whether to print branch information

    Returns:
        bool: True if operation succeeded, False otherwise
    """
    try:
        if debug:
            print("\nListing all branches in the repository:")
            print("-" * 50)

            # List local branches
            local_result = run_command(['git', 'branch'], cwd=directory, debug=debug)
            print("Local branches:")
            for branch in local_result.stdout.strip().split('\n'):
                if branch.strip():
                    print(f"  {branch.strip()}")

            # List remote branches
            remote_result = run_command(['git', 'branch', '-r'], cwd=directory, debug=debug)
            print("\nRemote branches:")
            for branch in remote_result.stdout.strip().split('\n'):
                if branch.strip():
                    print(f"  {branch.strip()}")

            print("-" * 50)
        return True
    except CalledProcessError as e:
        if debug:
            print(f"Error listing branches: {e}")
        return False


def clone_or_pull_code(directory, repo_url, branch, debug=True):
    """
    Clone a Git repository or pull latest changes if it already exists.

    Args:
        directory (str): Target directory for the repository
        repo_url (str): URL of the Git repository
        branch (str): Branch name to checkout
        debug (bool): Whether to print detailed information

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
        if debug:
            print(f"Pulling latest code from {directory} on branch {branch}")
        else:
            print(f"Updating repository on branch {branch}")

        try:
            # Checkout the specified branch
            run_command(['git', 'checkout', branch], cwd=directory, debug=debug)

            # Pull the latest changes
            run_command(['git', 'pull'], cwd=directory, debug=debug)

            # Show current status if debug is enabled
            if debug:
                run_command(['git', 'status'], cwd=directory, debug=debug)

            # Print all branches if debug is enabled
            print_all_branches(directory, debug=debug)

            return True
        except CalledProcessError as e:
            print(f"Error pulling code: {e}")
            return False
    else:
        if debug:
            print(f"Cloning repository from {repo_url} to {directory} on branch {branch}")
        else:
            print(f"Cloning repository on branch {branch}")

        try:
            # Create parent directory if it doesn't exist
            parent_dir = os.path.dirname(directory)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
                if debug:
                    print(f"Created parent directory: {parent_dir}")

            # Use the directory name as the target for git clone
            repo_name = os.path.basename(directory)

            # Clone the repository
            run_command(['git', 'clone', '-b', branch, repo_url, repo_name], cwd=parent_dir, debug=debug)

            # Show clone result if debug is enabled
            if os.path.exists(directory):
                if debug:
                    run_command(['git', 'status'], cwd=directory, debug=debug)

                # Print all branches if debug is enabled
                print_all_branches(directory, debug=debug)

                return True
        except CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            return False


def load_config_from_file(file_path, debug=True):
    """
    Load configuration from a file.

    Args:
        file_path (str): Path to the configuration file
        debug (bool): Whether to print detailed information

    Returns:
        dict: Configuration values
    """
    config = DEFAULT_CONFIG.copy()

    try:
        if debug:
            print(f"Attempting to load configuration from: {file_path}")
        with open(file_path, 'r') as file:
            file_content = file.read()

            for line in file_content.splitlines():
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
                    elif key == 'debug':
                        config['debug'] = value

        if debug:
            print(f"Loaded configuration: {config}")
        return config
    except FileNotFoundError:
        if debug:
            print(f"Config file not found: {file_path}")
            print("Using default configuration values")
        return config
    except Exception as e:
        if debug:
            print(f"Error reading config file: {e}")
            print("Using default configuration values")
        return config


def rename_directory(source, destination, debug=True):
    """
    Rename a directory if source and destination are different to assure cloned code to be in pre-determined location

    Args:
        source (str): Source directory path. Determined by git clone or by git update operations
        destination (str): Destination directory path a.k.a REFERENCED_DIRECTORY that is hard-coded in external routines
        debug (bool): Whether to print detailed information

    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(source) or not os.path.isdir(source):
        print(f"Directory does not exist: {source}")
        return False

    if source == destination:
        if debug:
            print("Directory name of cloned repo matches expected directory name. Skipping rename.")
        return True

    # If destination exists, remove it first (if we got this far, we're in forced mode)
    if os.path.exists(destination):
        if debug:
            print(f"Removing existing destination directory: {destination}")
        shutil.rmtree(destination)
        if debug:
            print(f"Removed directory: {destination}")

    try:
        # Make sure parent directory exists
        parent_dir = os.path.dirname(destination)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            if debug:
                print(f"Created parent directory: {parent_dir}")

        # Move the directory
        if debug:
            print(f"Moving directory from {source} to {destination}")
        shutil.move(source, destination)
        if debug:
            print(f"Directory renamed: {source} → {destination}")

        # Verify the move
        if os.path.exists(destination):
            if debug:
                print(f"Verified: {destination} exists")
            return True
    except Exception as e:
        print(f"Error renaming directory: {e}")
        return False


def main():
    """Main function to execute the script logic."""
    # Load configuration from file
    config = load_config_from_file(INPUT_FILE_PATH, debug=True)  # Always load with debug for initial setup

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Clone or pull a Git repository.')
    parser.add_argument('--directory', default=config['directory_location'],
                        help=f'Target directory (default: {config["directory_location"]})')
    parser.add_argument('--repository', '-r', default=config['git_repository'],
                        help=f'Git repository URL (default: {config["git_repository"]})')
    parser.add_argument('--branch', '-b', default=config['branch'],
                        help=f'Git branch (default: {config["branch"]})')
    parser.add_argument('--forced', '-f', default=config['overwrite_existing_directory'],
                        help=f'Force delete existing directory (default: {config["overwrite_existing_directory"]})')
    parser.add_argument('--debug', '-d', default=config['debug'],
                        help=f'Enable debug output (default: {config["debug"]})')
    args = parser.parse_args()

    # Convert debug string to boolean
    debug_mode = args.debug.lower() == 'true'

    if debug_mode:
        print("=" * 80)
        print("Git Repository Management Script")
        print("=" * 80)

        print("\nScript Configuration:")
        print(f"- Using directory: {args.directory}")
        print(f"- Using repository: {args.repository}")
        print(f"- Using branch: {args.branch}")
        print(f"- Forced mode: {args.forced}")
        print(f"- Debug mode: {args.debug}")
        print(f"- Referenced directory: {REFERENCED_DIRECTORY}")
        print("-" * 80)
    else:
        print("Git Repository Management Script - Summary Mode")

    # Check and clean directories if forced flag is set to true
    if args.forced.lower() == 'true':
        # Clean both the target directory and referenced directory if they exist
        for dir_path in [args.directory, REFERENCED_DIRECTORY]:
            if os.path.exists(dir_path):
                if debug_mode:
                    print(f"Forced mode: Deleting existing directory: {dir_path}")
                    print(f"Deleted directory: {dir_path}")
                else:
                    print(f"Removing existing directory: {dir_path}")
                shutil.rmtree(dir_path)

    # Clone or pull the repository
    if debug_mode:
        print("\nPerforming Git Operations:")
        print("-" * 80)

    if not clone_or_pull_code(args.directory, args.repository, args.branch, debug=debug_mode):
        print("\n❌ Git operation failed")
        sys.exit(1)
    else:
        print("\n✅ Git operation completed successfully")

    # Rename directory if needed
    if debug_mode:
        print("\nDirectory Management:")
        print("-" * 80)

    if not rename_directory(args.directory, REFERENCED_DIRECTORY, debug=debug_mode):
        print("\n❌ Directory rename operation failed")
        sys.exit(1)
    else:
        if debug_mode:
            print("\n✅ Script completed successfully")
            print("=" * 80)
        else:
            print("✅ All operations completed successfully")


if __name__ == "__main__":
    main()
