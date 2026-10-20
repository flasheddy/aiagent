from functions.write_file import write_file


def test() -> None:
    inputs = [
        ("calculator", "lorem.txt", "wait, this isn't lorem ipsum"),
        ("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"),
        ("calculator", "/tmp/temp.txt", "this should not be allowed")
    ]

    results = {
        file_path: write_file(working_dir, file_path, content)
        for working_dir, file_path, content in inputs
    }

    lines = [
        f"Result for `{file_path}`:\n{content}"
        for file_path, content in results.items()
    ]

    print("\n\n".join(lines))


if __name__ == "__main__":
    test()
