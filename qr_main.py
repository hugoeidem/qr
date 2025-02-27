

import sys
from basic_reader import Basic_reader

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Decode: python qr_main.py file.png [show_info]")
        sys.exit(1)

    filename = sys.argv[1]
    
    show_info = 1 if len(sys.argv) == 3 else 0

    Basic_reader(filename, show_info).decode()


main()




