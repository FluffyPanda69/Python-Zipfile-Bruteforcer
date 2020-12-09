import itertools
import string
from tqdm import tqdm

# Testing the speed of itertools.product with tqdm progress bar
# Generating entire keyspace to a file for faster reading is not viable, requires too much space
def main():

    f = open("all_passwords.txt", "w")
    for keysize in range(3):
        for key in tqdm(map(''.join, itertools.product(string.ascii_letters + string.digits, repeat=keysize + 1))):
            f.write(key+"\n")
    f.close()

    print(string.ascii_letters)
    print(len(string.ascii_letters))

if __name__ == "__main__":
    main()
