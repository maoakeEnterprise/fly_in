from utils import FlagManager


def main() -> None:
    try:
        parsing = FlagManager()
        parsing.init_args(None)
        print(parsing._get_args_values())
        print("Hello from fly-in!")
    except ValueError as e:
        print("=======VALUE==ERROR========")
        print(f"Message : {e}")
        print("===========================")
    except (FileNotFoundError, PermissionError) as e:
        print("=======FILE===ERROR========")
        print(f"Message : {e}")
        print("===========================")


if __name__ == "__main__":
    main()
