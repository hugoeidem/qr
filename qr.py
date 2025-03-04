

import sys
from basic_reader import Basic_reader

def main():

    show_info = False

    if len(sys.argv) == 1:
        print("You need a file to decode!\n") # or a messsage to encode!\n")
        print("Usage:")
        print("   python qr.py some_file.png [optional flags]\n")
        sys.exit(1)

    for parameter in sys.argv[1:]:
        if len(parameter) == 2 and parameter == "-v":
            show_info = True
            
        else:
            filename = parameter
            if ".png" not in filename:
                print("File is not a .png!\n")
                sys.exit(1)
                
    Basic_reader(filename, show_info).decode()


main()




