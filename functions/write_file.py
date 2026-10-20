import os


def write_file(working_directory: str, file_path: str, content: str) -> str:
    """
    `working_directory` is for human, `file_path` and `content` is for agent
    """
    try:
        # Validate `file_path` is inside `working_directory`
        abs_working_dir = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(abs_working_dir, file_path))
        is_valid_path = (
            os.path.commonpath([abs_working_dir, target_path]) == abs_working_dir
        )
        if not is_valid_path:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        # Validate `file_path` is not a directory
        if os.path.isdir(target_path):
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        # Make sure all parent directories exist in `file_path`
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        # Write `content` to `file_path`
        with open(target_path, "w") as f:
            _ = f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:  # noqa: BLE001
        return f'Error: writing to "{file_path}": {e}'
