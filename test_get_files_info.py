from functions.get_files_info import get_files_info


def test() -> None:
    results = [
        (
            "Result for current direcotry:",
            get_files_info("calculator", ".")
        ),
        (
            "Result for '/bin' direcotry:",
            get_files_info("calculator", "/bin")
        ),
        (
            "Result for '../' direcotry:",
            get_files_info("calculator", "../")
        ),
        (
            "Result for 'main.py' direcotry:",
            get_files_info("calculator", "main.py")
        )
    ]

    lines = [f"{header}\n{body}" for header, body in results]
    print("\n\n".join(lines))


if __name__ == "__main__":
    test()
