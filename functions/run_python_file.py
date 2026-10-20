import os
import subprocess


def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    """
    working_directory is for human to limit agent scope
    """
    try:
        # Validate `file_path` is inside the `working_directory`
        abs_working_dir = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(abs_working_dir, file_path))
        is_valid_path = (
            os.path.commonpath([abs_working_dir, target_path]) == abs_working_dir
        )
        if not is_valid_path:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        # Validate the `file_path` exists
        if not os.path.isfile(target_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        # Validate the `file_path` is python file
        if not target_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        # Use a `subprocess` to run the file
        # Build a command
        command = ["python", target_path]
        if args:
            command.extend(args)
        # Run a command
        result = subprocess.run(
            command,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=30.0,
            check=False,
        )
        output: list[str] = []
        if result.returncode != 0:
            output.append(f"Process existed with code {result.returncode}")
        if not result.stdout and not result.stderr:
            output.append("No output produced")
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        return "\n".join(output)
    except Exception as e:  # noqa: BLE001
        return f"Error: executing Python file: {e}"
