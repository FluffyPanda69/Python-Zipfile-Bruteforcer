import zipfile
import argparse
import itertools
import string
import sys


# One process, one thread, not that slow but I think we can do better
def main():
    parser = argparse.ArgumentParser("%prog -f <zipfile>")
    parser.add_argument("-f", dest="zname", help="Zip to crack")
    args = parser.parse_args()

    if args.zname is None:
        print(parser.usage)
        sys.exit()
    else:
        zname = args.zname

    zfile = zipfile.ZipFile(zname)

    tested = 0

    for keysize in range(10):
        for key in map(''.join, itertools.product(string.ascii_letters + string.digits, repeat=keysize + 1)):
            tested = tested + 1
            print(str(tested) + " - " + key)
            try:
                password = bytes(key, 'utf-8')
                zfile.setpassword(password)
                if zfile.testzip() is None:
                    print("\n\nFound password = " + key)
                    exit(0)
            except RuntimeError:
                pass

    print('Password not found')


if __name__ == "__main__":
    main()
