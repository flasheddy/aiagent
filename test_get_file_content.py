from functions.get_file_content import get_file_content


def test() -> None:
    inputs = [
        ("calculator", "lorem.txt"),
        ("calculator", "main.py"),
        ("calculator", "pkg/calculator.py"),
        ("calculator", "/bin/cat"),
        ("calculator", "pkg/does_not_exist.py")
    ]

    results = {
        file_path: get_file_content(working_dir, file_path)
        for working_dir, file_path in inputs
    }

    lorem_content = results["lorem.txt"]
    print("Result for `lorem.txt`:")
    print(f"lorem.txt length: {len(lorem_content)}")
    print(f"lorem.txt truncated: {'truncated' in lorem_content}", end="\n\n")
    del results["lorem.txt"]

    other_lines = [
        f"Result for `{file_path}`:\n{content}"
        for file_path, content in results.items()
    ]

    print("\n\n".join(other_lines))


if __name__ == "__main__":
    test()
