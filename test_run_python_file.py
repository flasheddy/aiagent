from functions.run_python_file import run_python_file


def test() -> None:
    inputs = [
        ("calculator", "main.py", None),
        ("calculator", "main.py", ["3 + 5"]),
        ("calculator", "tests.py", None),
        ("calculator", "../main.py", None),
        ("calculator", "nonexistent.py", None),
        ("calculator", "lorem.txt", None),
    ]

    results = {
        file_path if not args else f'{file_path} "{" ".join(args)}"': run_python_file(working_dir, file_path, args)  
        for working_dir, file_path, args in inputs
    }

    lines = [
        f"Result for `{command}`:\n{content}"
        for command, content in results.items()
    ]

    print("\n\n".join(lines))


if __name__ == "__main__":
    test()
