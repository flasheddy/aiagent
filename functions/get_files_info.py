import os


def get_files_info(working_directory: str, directory: str = ".")-> str:
    """
        `working_directory` is specified by human, `directory` is for agent
        so agent can work in a directory flexibly given a limited scope
    """
    try:
        # Validate the path to `directory` is inside `working_directory`
        abs_working_dir = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(abs_working_dir, directory))
        is_valid_target_dir = os.path.commonpath([abs_working_dir, target_dir]) == abs_working_dir
        if not is_valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        # Validate `directory` exists
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'
        return f'Success: "{directory}" is within the working directory'
    except Exception as e:  # noqa: BLE001
        return f"Error: {e}"
