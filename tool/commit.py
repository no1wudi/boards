import litellm as lm
import subprocess
import sys
import os
import argparse

# Maximum total size of files to include in commit message analysis
MAX_FILE_SIZE_KB = 50

# Format prompts for different commit message styles
format_prompts = {
    "nuttx": """You are an experienced software engineer writing a commit message following the Apache NuttX RTOS format:
    <functional_context>: <topic>

    <description>

    === Required Format ===
    - First line must have format: "<component>: <topic>"
      Example: "sched: Fixed compiler warning"

    - Description (optional) must be separated from topic by blank line

    - Description can include bullet points for multiple items

    === Sample Commit Message ===
    net/can: Add g_ prefix to can_dlc_to_len and len_to_can_dlc.

    Add g_ prefix to can_dlc_to_len and len_to_can_dlc to
    follow NuttX coding style conventions for global symbols,
    improving code readability and maintainability.
    * Fixed naming convention for global symbols
    * Improved code consistency
    * Enhanced maintainability""",
    "conventional": """You are an experienced software engineer. Please write a commit message following the Conventional Commits format:
    <type>[optional scope]: <description>

    [optional body]

    [optional footer(s)]

    Types: feat, fix, docs, style, refactor, perf, test, chore, etc.

    === Sample Commit Message ===
    feat(auth): implement OAuth2 authentication

    - Add OAuth2 authentication flow using JWT tokens
    - Implement refresh token mechanism
    - Add user session management

    BREAKING CHANGE: Authentication header format has changed""",
    "rust": """You are an experienced Rust developer. Please write a commit message following the Rust project style:
    <one-line summary>

    <detailed description>

    === Sample Commit Message ===
    impl Debug for ParseError and fix error handling

    * Add Debug implementation for ParseError enum
    * Improve error propagation in parser module using `?` operator
    * Replace manual error conversions with From trait implementations
    * Add error tests to ensure correct error variants are returned

    This change makes error handling more idiomatic and improves debuggability
    when parsing fails.""",
    "pr": """You are an experienced software engineer writing a pull request description for Apache NuttX RTOS:

    === Required Format ===
    Summary:
    - Why change is necessary (fix, update, new feature)
    - What functional part of code is being changed
    - How change exactly works
    - Related issue/PR references if applicable

    Impact:
    - New feature added? YES/NO (describe if yes)
    - Impact on user? YES/NO (describe if yes)
    - Impact on build? YES/NO (describe if yes)
    - Impact on hardware? YES/NO (describe if yes)
    - Impact on documentation? YES/NO (describe if yes)
    - Impact on security? YES/NO (describe if yes)
    - Impact on compatibility? YES/NO (describe if yes)

    === Sample PR Description ===
    Summary:
    * Add support for new RISC-V SiFive board
    * Implements basic GPIO and UART drivers
    * Adds board configuration and documentation
    * Related to issue #1234

    Impact:
    * New feature added?: YES - Adds new board support
    * Impact on user?: NO
    * Impact on build?: YES - New board configs added to build system
    * Impact on hardware?: YES - New RISC-V board support
    * Impact on documentation?: YES - Added board documentation
    * Impact on security?: NO
    * Impact on compatibility?: NO""",
}


def parse_args():
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments with repo_path and model
    """
    parser = argparse.ArgumentParser(description="Rewrite git commit messages using AI")
    parser.add_argument("repo_path", help="Path to the git repository")
    parser.add_argument("--model", default="deepseek-r", help="LLM model to use")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output for debugging",
    )
    parser.add_argument(
        "--format",
        default="nuttx",
        choices=["nuttx", "common", "rust", "pr"],
        help="Commit message format style",
    )
    args = parser.parse_args()

    # Auto-detect model based on API endpoint
    if args.model == "deepseek":
        args.model = "openai/deepseek-chat"
    elif args.model == "deepseek-r":
        args.model = "openai/deepseek-reasoner"

    if args.model.startswith("openai/deepseek"):
        # Configure LLM
        # deepseek
        lm.api_base = "https://api.deepseek.com/v1"
        lm.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not lm.api_key:
            print("Error: DEEPSEEK_API_KEY environment variable is not set")
            sys.exit(1)
    else:
        # Other models
        lm.api_base = os.getenv("OPENAI_API_BASE")
        lm.api_key = os.getenv("OPENAI_API_KEY")

    return args


class Git:
    def __init__(self, repo_path):
        self.repo_path = self.get_repo_path(repo_path)

    def get_repo_path(self, path):
        """Validate and get absolute path to git repository.

        Args:
            path (str): Path to the repository

        Returns:
            str: Absolute path to the repository

        Raises:
            SystemExit: If path doesn't exist or isn't a git repository
        """
        repo_path = os.path.abspath(path)
        if not os.path.exists(repo_path):
            print(f"Error: Path does not exist: {repo_path}")
            sys.exit(1)
        if not os.path.exists(os.path.join(repo_path, ".git")):
            print(f"Error: Not a git repository: {repo_path}")
            sys.exit(1)
        return repo_path

    def check_repo_clean(self):
        """Check if git repository has uncommitted changes.

        Raises:
            SystemExit: If repository has uncommitted changes or status check fails
        """
        try:
            status = (
                subprocess.check_output(
                    ["git", "status", "--porcelain"], cwd=self.repo_path
                )
                .decode("utf-8")
                .strip()
            )

            if status:
                print(
                    "Error: Repository has uncommitted changes. Please commit or stash them first."
                )
                sys.exit(1)
        except subprocess.CalledProcessError:
            print("Error: Failed to check repository status")
            sys.exit(1)

    def get_branch_info(self):
        """Get current branch name and latest commit ID.

        Returns:
            tuple: (branch_name, commit_id) where:
                branch_name (str): Current branch name
                commit_id (str): Short commit hash

        Raises:
            SystemExit: If git command fails
        """
        try:
            branch_name = (
                subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.repo_path
                )
                .decode("utf-8")
                .strip()
            )

            commit_id = (
                subprocess.check_output(
                    ["git", "rev-parse", "--short", "HEAD"], cwd=self.repo_path
                )
                .decode("utf-8")
                .strip()
            )

            return branch_name, commit_id
        except subprocess.CalledProcessError:
            print("Error: Failed to get branch info")
            sys.exit(1)

    def get_modified_files(self):
        """Get list of files changed in the last commit.

        Returns:
            list: List of file paths that were modified

        Raises:
            SystemExit: If git command fails
        """
        try:
            output = (
                subprocess.check_output(
                    ["git", "diff", "HEAD~1", "HEAD", "--name-only"], cwd=self.repo_path
                )
                .decode("utf-8")
                .strip()
            )

            return [f for f in output.split("\n") if f]
        except subprocess.CalledProcessError:
            print("Error: Failed to get modified files")
            sys.exit(1)

    def get_file_contents(self, file_paths):
        """Get the contents of multiple files in the repository if they're not too large.

        Args:
            file_paths (list): List of relative paths to files in repository

        Returns:
            list: List of tuples (file_path, content) where content is empty string if file is too large

        Raises:
            SystemExit: If any file cannot be read
        """
        # First get sizes of all files
        file_sizes = []
        for file_path in file_paths:
            try:
                size = os.path.getsize(os.path.join(self.repo_path, file_path))
                file_sizes.append((file_path, size))
            except IOError:
                print(f"Warning: Failed to read file: {file_path}")
                # Remove file from file_paths list
                file_paths.remove(file_path)

        # Calculate total size
        total_size = sum(size for _, size in file_sizes)

        # If total size exceeds limit, remove largest files until under limit
        if total_size > MAX_FILE_SIZE_KB * 1024:
            # Sort by size descending
            file_sizes.sort(key=lambda x: x[1], reverse=True)

            while total_size > MAX_FILE_SIZE_KB * 1024 and file_sizes:
                removed_file, removed_size = file_sizes.pop(0)
                total_size -= removed_size
                print(
                    f"Omitting large file: {
                      removed_file} ({removed_size} bytes)"
                )

        # Now read remaining files
        results = []
        for file_path, size in file_sizes:
            try:
                with open(os.path.join(self.repo_path, file_path), "r") as f:
                    results.append((file_path, f.read()))
            except IOError:
                print(f"Warning: Failed to read file: {file_path}")

        return results

    def get_current_commit_message(self):
        """Get the most recent commit message from the repository.

        Returns:
            tuple: (title, message) where:
                title (str): First line of commit message
                message (str): Full commit message without signature lines

        Raises:
            SystemExit: If git command fails
        """
        try:
            message = (
                subprocess.check_output(
                    ["git", "log", "-1", "--pretty=%B"], cwd=self.repo_path
                )
                .decode("utf-8")
                .strip()
            )

            lines = [
                line
                for line in message.split("\n")
                if not line.lower().startswith("signed-off-by:")
            ]
            clean_message = "\n".join(lines).strip()

            title = clean_message.split("\n")[0]
            return title, clean_message
        except subprocess.CalledProcessError:
            print("Error: Failed to get commit message")
            sys.exit(1)

    def get_commit_diff(self):
        """Get diff of the last commit.

        Returns:
            str: Unified diff output showing changes in last commit

        Raises:
            SystemExit: If git command fails
        """
        try:
            return (
                subprocess.check_output(
                    ["git", "diff", "HEAD~1", "HEAD"], cwd=self.repo_path
                )
                .decode("utf-8")
                .strip()
            )
        except subprocess.CalledProcessError:
            print("Error: Failed to get commit diff")
            sys.exit(1)

    def update_commit_message(self, new_message):
        """Update the most recent commit with the new message.

        Args:
            new_message (str): New commit message to use

        Raises:
            SystemExit: If git command fails
        """
        try:
            subprocess.run(
                ["git", "commit", "--amend", "-s", "-m", new_message],
                check=True,
                cwd=self.repo_path,
            )
            print("Successfully updated commit message")
        except subprocess.CalledProcessError:
            print("Error: Failed to update commit message")
            sys.exit(1)


def rewrite_commit_message(
    title, original_message, model, git, modified_files, verbose=False, format="nuttx"
):
    """Use AI to rewrite a commit message while preserving the title.

    Args:
        title (str): Original commit title
        original_message (str): Full original commit message
        model (str): LLM model to use for rewriting
        git (Git): Git repository instance
        modified_files (list): List of modified file paths
        verbose (bool, optional): Whether to print debug info. Defaults to False.
        format (str, optional): Commit message format style. Defaults to 'nuttx'.

    Returns:
        str: Rewritten commit message with original title preserved
    """
    file_contents = []
    for file_path, content in git.get_file_contents(modified_files):
        if content:  # Only include files that weren't too large
            file_contents.append(f"=== {file_path} ===\n{content}\n")

    files_section = "\n".join(file_contents)
    diff = git.get_commit_diff()

    prompt = f"""{format_prompts[format]}

    === Code Changes ===
    {diff}

    === Modified Files ===
    {files_section}

    === Original commit message ===
    {original_message}

    Please return rewritten message body with origin title directly."""

    if verbose:
        print("\n=== Sending to LLM ===")
        print(f"Model: {model}")
        print(f"Prompt:\n{prompt}\n")

    response = lm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
        max_tokens=4000,
    )

    if verbose:
        print("=== LLM Response ===")
        print(f"Usage: {response.usage}")
        print(f"Finish Reason: {response.choices[0].finish_reason}")

    new_message = response.choices[0].message.content.strip()
    # Ensure original title is preserved
    return f"{new_message}"


def write_pr_message(
    title, original_message, model, git, modified_files, verbose=False
):
    """Use AI to write a PR description.

    Args:
        title (str): Original commit title
        original_message (str): Full original commit message
        model (str): LLM model to use for rewriting
        git (Git): Git repository instance
        modified_files (list): List of modified file paths
        verbose (bool, optional): Whether to print debug info. Defaults to False

    Returns:
        str: PR description
    """
    file_contents = []
    for file_path, content in git.get_file_contents(modified_files):
        if content:
            file_contents.append(f"=== {file_path} ===\n{content}\n")

    files_section = "\n".join(file_contents)
    diff = git.get_commit_diff()

    prompt = f"""{format_prompts["pr"]}

    === Code Changes ===
    {diff}

    === Modified Files ===
    {files_section}

    === Original commit message ===
    {original_message}

    Please write a pull request description based on the above changes."""

    if verbose:
        print("\n=== Sending to LLM ===")
        print(f"Model: {model}")
        print(f"Prompt:\n{prompt}\n")

    response = lm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
        max_tokens=4000,
    )

    if verbose:
        print("=== LLM Response ===")
        print(f"Usage: {response.usage}")
        print(f"Finish Reason: {response.choices[0].finish_reason}")

    return response.choices[0].message.content.strip()


def preview_changes(original_message, new_message):
    """Show diff between original and new message and prompt for confirmation.

    Args:
        original_message (str): Original commit message
        new_message (str): Proposed new commit message

    Returns:
        bool: True if user confirms changes, False if rejects

    Note:
        Displays the new message and prompts user for confirmation
    """

    # Then show the new proposed message
    print("\n=== New Commit Message ===")
    print(new_message)
    while True:
        response = input("\nDo you want to apply these changes? [Y/n]: ").lower()
        if response in ["y", "n", ""]:
            return response != "n"


if __name__ == "__main__":
    args = parse_args()
    git = Git(args.repo_path)
    git.check_repo_clean()

    branch_name, commit_id = git.get_branch_info()
    print(f"\n=== Branch Info ===\nBranch: {branch_name}\nCommit: {commit_id}")

    modified_files = git.get_modified_files()
    print(f"\n=== Modified Files ===\n{'\n'.join(modified_files)}")

    title, original_message = git.get_current_commit_message()
    print("\n=== Original Commit Message ===")
    print(original_message)
    print()

    if args.format == "pr":
        new_message = write_pr_message(
            title,
            original_message,
            args.model,
            git,
            modified_files,
            args.verbose,
        )
    else:
        new_message = rewrite_commit_message(
            title,
            original_message,
            args.model,
            git,
            modified_files,
            args.verbose,
            args.format,
        )

    if preview_changes(original_message, new_message):
        git.update_commit_message(new_message)
    else:
        print("Changes discarded")
