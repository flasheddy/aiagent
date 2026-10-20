import os


def get_files_info(working_directory: str, directory: str = ".") -> str:
    """
    `working_directory` is specified by human, `directory` is for agent
    so agent can work in a directory flexibly given a limited scope
    """
    try:
        # Validate the path to `directory` is inside `working_directory`
        abs_working_dir = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(abs_working_dir, directory))
        is_valid_target_dir = (
            os.path.commonpath([abs_working_dir, target_dir]) == abs_working_dir
        )
        if not is_valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        # Validate `directory` exists
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'
        # Process the target directory
        files_info: list[str] = []
        for item in os.listdir(target_dir):
            item_path = os.path.normpath(os.path.join(target_dir, item))
            size = os.path.getsize(item_path)
            is_dir = os.path.isdir(item_path)
            files_info.append(f"  - {item}: file_size={size} bytes, is_dir={is_dir}")
        return "\n".join(files_info)
    except Exception as e:  # noqa: BLE001
        return f"Error: listing files: {e}"


schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list files from, relative to the working directory (default is the working directory itself)",
                },
            },
        },
    },
}
