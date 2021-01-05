import zipfile
import argparse
import itertools
import string
import multiprocessing
import time
import sys

# set max password length to check
max_length = 10
# numbers of tries between updates (per process)
update = 0
max_update = 1000
# keyspace to be used
keyspace = ""


# split keyspace into equal number of prefixes for cores to handle
# functionally, split string into n equal-ish parts
def split_keyspace(keyspc, parts):
    avg = len(keyspc) / parts
    avg = int(avg)
    for i in range(parts - 1):
        yield keyspc[i * avg:i * avg + avg]
    yield keyspc[parts * avg - avg:]


# will run on a core, checks for equal chunk of passwords
# will print its progress every max_update number of tries
def test_password_chunk(filename, ml, mu, kspc, prefixes, cnumber, done):
    global update
    test_file = zipfile.ZipFile(filename, allowZip64=True)
    # try password sizes progressively
    for keysize in range(1, ml):
        # try each prefix progressively
        for prefix in prefixes:
            # try all possible combinations in keyspace
            for key in map(''.join, itertools.product(kspc, repeat=keysize)):
                update = update + 1
                # value 100 means somebody found the password
                if done.value < 100:
                    # try the password, report progress each max_update tries
                    password = prefix + key
                    pw_bytes = bytes(password, 'utf-8')
                    if update == mu:
                        print("[Worker " + str(cnumber) + "] : " + password, flush=True)
                        update = 0
                    try:
                        # if the password is good, report it, set value to 100 so everybody knows it's done
                        test_file.setpassword(pw_bytes)
                        if test_file.testzip() is None:
                            print("[Worker " + str(cnumber) + "] : Found password = " + password + " ", flush=True)
                            done.value = 100
                            return
                    # wrong password throws runtime error, so we ignore it
                    except RuntimeError:
                        pass
                # if value is 100 someone else found the password, we can stop
                else:
                    return
    # if we exhaust our chunk and don't find the password, increment value
    # this is so main knows how many workers are done in case nobody finds the password
    print("[Worker " + str(cnumber) + "] : Password not found in chunk " + str(prefixes))
    done.value = done.value + 1


# -f zip name, output password
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", dest="zip_name", help="Zip file to crack (Required)")
    parser.add_argument("-c", dest="max_cores", help="Maximum number of processes to spawn")
    parser.add_argument("-u", dest="update", help="Number of iterations after a process gives a status", type=int)
    parser.add_argument("-lowercase", help="Add lowercase letters to custom keyspace", action="store_true")
    parser.add_argument("-uppercase", help="Add uppercase letters to custom keyspace", action="store_true")
    parser.add_argument("-digits", help="Add digits to custom keyspace", action="store_true")
    parser.add_argument("-k", dest="keyspace", help="Add custom string to keyspace")
    parser.add_argument("-ml", dest="ml", help="Set custom maximum length to check", type=int)
    args = parser.parse_args()

    # check if a file was given
    if args.zip_name is None:
        print("\nNo file given !")
        sys.exit(1)
    else:
        zname = args.zip_name

    # check if zip is valid (not only extension)
    if zipfile.is_zipfile(zname):
        zfile = zipfile.ZipFile(zname, allowZip64=True)
    else:
        print("\nInput file is not a valid zip !")
        sys.exit(1)

    # check if zip actually is password protected
    try:
        if zfile.testzip() is None:
            print("\nInput file is not password protected !")
            sys.exit(0)
    except RuntimeError:
        pass

    # check for custom update interval
    global max_update
    if args.update is not None:
        if args.update > 0:
            max_update = args.update

    # check for custom keyspace, add options
    global keyspace
    if args.lowercase:
        keyspace = keyspace + string.ascii_lowercase
    if args.uppercase:
        keyspace = keyspace + string.ascii_uppercase
    if args.digits:
        keyspace = keyspace + string.digits
    if args.keyspace is not None:
        keyspace = keyspace + args.keyspace
    if len(keyspace) == 0:
        # if no custom options are found, use entire keyspace
        keyspace = (string.ascii_letters + string.digits)
    # remove duplicates from keyspace
    keyspace = "".join(set(keyspace))
    keyspace = "".join(sorted(keyspace))

    # check for custom max length
    global max_length
    if args.ml is not None:
        if args.ml in range(2, 100):
            max_length = args.ml

    # start message
    print("\nOrdered brute force attack using keyspace of size " + str(len(keyspace)) + ":\n")
    print(keyspace + "\n")
    print("Attack will stop if password is not found at length " + str(max_length) + "\n")
    print("Workers will report progress every " + str(max_update) + " checks\n")

    # shared memory, check for end state between processes
    done = multiprocessing.Value('i', 0)

    # check for single character password
    for key in keyspace:
        if done.value == 0:
            try:
                pw_byte = bytes(key, 'utf-8')
                zfile.setpassword(pw_byte)
                if zfile.testzip() is None:
                    print("\nThe password is \"" + key + "\"\n")
                    done.value = 1
                    sys.exit()
            except RuntimeError:
                pass
        else:
            sys.exit()

    # check for custom number of processes to use
    # will spawn a maximum of len(keyspace) processes
    if args.max_cores is None:
        cores = len(keyspace)
    else:
        cores = min(int(args.max_cores), len(keyspace))

    # split the keyspace into roughly equal number of prefixes
    prefix_list = []
    chunks = split_keyspace(keyspace, cores)
    for i in range(cores):
        prefix_list.append(chunks.__next__())

    # define processes to be spawned, then start them
    processes = []
    for i in range(cores):
        processes.append(multiprocessing.Process(target=test_password_chunk,
                                                 args=(
                                                     zname, max_length, max_update, keyspace, prefix_list[i], i,
                                                     done,)))
    for pro in processes:
        pro.start()

    # main thread will report back every 5 seconds that it's still alive
    # cores will always be smaller than 100 (signal that password was found)
    # after all workers are done value is either 100 (found) or number of workers (not found)
    while done.value < cores:
        print("Main still working...")
        time.sleep(5)
    if done.value < 100:
        print("\nPassword not found, shutting down...")
    else:
        print("\nPassword found, shutting down...")
    sys.exit()


if __name__ == "__main__":
    main()
