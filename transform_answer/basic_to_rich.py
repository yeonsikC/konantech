
import sys
import intent_file_to_rich
import worked_file_to_rich


def choose_module(option):
    if option == "-i" or option == "--i":
        intent_file_to_rich.intent_file_to_rich()
    else:
        worked_file_to_rich.worked_file_to_rich()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        option = sys.argv[1]
    else:
        option = "-p"
    choose_module(option)