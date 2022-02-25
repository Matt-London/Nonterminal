import packages.resources.variables as var
from packages.parser.Interpreter import Interpreter


def main() -> None:
    """
    Main function with command loop

    :return: None
    """
    interpreter = Interpreter()

    # Check if colors should be disabled
    print("Is the following text readable?")
    print(var.ps1)
    readable = str(input("Type y for yes and n for no:"))
    if readable != "y":
        var.colorPrompt = False

    while True:
        try:
            interpreter.prompt()

        except KeyboardInterrupt:
            print()
            var.exit_code = 130
            continue

if __name__ == "__main__":
    main()