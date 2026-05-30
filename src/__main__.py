from utils import Parsing


def main() -> None:
    try:
        parsing = Parsing()
        parsing.init_args(None)
        print(parsing.get_args_values())
        print("Hello from fly-in!")
    except Exception as e:
        print(f"{e}")


if __name__ == "__main__":
    main()
