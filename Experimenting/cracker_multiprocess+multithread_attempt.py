import zipfile
import argparse
import itertools
import string
import threading
import multiprocessing
import os

# set max password length to check
max_length = 10
# global indicator to finish
done = False


# will run on a core, checks for equal chunk of passwords
def test_password_chunk(filename, prefixes):
    global done
    test_file = zipfile.ZipFile(filename)
    for prefix in prefixes:
        for keysize in range(max_length):
            for key in map(''.join, itertools.product(string.ascii_letters + string.digits, repeat=keysize)):
                if not done:
                    password = prefix + key
                    t = threading.Thread(target=test_zip_password, args=(test_file, password), daemon=True)
                    t.start()
                else:
                    os.kill(os.getpid(), 0)
                    break


# get zip name and password, try to see if it's good
def test_zip_password(zip_file: zipfile.ZipFile, try_password):
    global done
    print(try_password + " ")
    try:
        pw_bytes = bytes(try_password, 'utf-8')
        zip_file.setpassword(pw_bytes)
        if zip_file.testzip() is None:
            print("\nThe password is \n\n---------- \n" + try_password + "\n----------")
            done = True
            os.kill(os.getppid(), 0)
            exit(0)
    except Exception:
        pass


# -f zip name, output password
def main():
    parser = argparse.ArgumentParser("%prog -f <zipfile> -c <cores>")
    parser.add_argument("-f", dest="zip_name", help="Zip file to crack")
    parser.add_argument("-c", dest="max_cores", help="Maximum number of cores to use")
    args = parser.parse_args()

    zname = None

    if args.zip_name is None:
        print(parser.usage)
        exit(0)
    else:
        zname = args.zip_name

    zFile = zipfile.ZipFile(zname)

    # check if zip is valid
    if zipfile.is_zipfile(zname):
        print("\n" + str(zFile.infolist()))
    else:
        print("\nInput file is not a valid zip")
        exit(0)

    # check for single character password
    for key in (string.ascii_letters + string.digits):
        if not done:
            test_zip_password(zFile, key)
        else:
            exit(1)

    # get number of system cores, split attempts equally
    # 62 characters are used
    if args.max_cores is None:
        cores = multiprocessing.cpu_count()
        print("\nDefaulting to using all your " + str(cores) + " cores")
    else:
        cores = int(args.max_cores)
        print("Brute forcing using " + str(cores) + " cores")
    prefix_list = []
    # todo less hardcoded
    if cores == 1:
        # 62
        prefix_list.append(string.ascii_letters + string.digits)
    elif cores == 2:
        # 31/31
        prefix_list.append(string.ascii_lowercase + "01234")
        prefix_list.append(string.ascii_uppercase + "56789")
    elif cores == 3:
        # 21/21/20
        prefix_list.append("abcdefghijklmnopqrstu")
        prefix_list.append("vwxyzABCDEFGHIJKLMNOP")
        prefix_list.append("QRSTUVWXYZ" + string.digits)
    elif cores == 4:
        # 15/15/16/16
        prefix_list.append("abcdefghijklmno")
        prefix_list.append("pqrstuvwxyzABCD")
        prefix_list.append("EFGHIJKLMNOPQRST")
        prefix_list.append("UVWXYZ" + string.digits)
    else:
        # 1/1/1/... x62
        for s in (string.ascii_letters + string.digits):
            prefix_list.append(s)

    processes = []
    for i in range(cores):
        processes.append(multiprocessing.Process(target=test_password_chunk, args=(zname, prefix_list[i],)))
    for pro in processes:
        pro.start()


if __name__ == "__main__":
    main()
