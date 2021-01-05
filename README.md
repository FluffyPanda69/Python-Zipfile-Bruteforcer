# Python-Zipfile-Bruteforcer

![Requirement](https://i.imgur.com/YgblCp8.png)

## Only works for ZIP files encrypted with ZipCrypto using a UTF-8 password
This program was made for learning purposes only, bruteforcing a password is not viable, and this encryption algorithm is weak and vulnerable to [exploits](https://blog.devolutions.net/2020/08/why-you-should-never-use-zipcrypto) anyway. Use this responsibly, only on files you have permission to access.

## Requirements
Python 3, all libraries used should be included in your environment by default. No OS-specific functions are used, so this should run on anything.
## Usage
>-f zipname

Required : the zip file you want to crack.
>-c cores

Specify the number of processes (cores) to be used. Default value is one process for each character in the keyspace (letters and/or digits).
>-u update_interval

Specify how often the workers should report their progress. Default value is 1000.
>-ml length

Specify the maximum password length to be checked. Default value is 10.
>-uppercase

>-lowercase

>-digits

>-k string

Build a custom keyspace for searching, options can be combined. If none are provided, a-zA-Z0-9 will be used.

## Exceptions
### Handled
>Missing file

>Invalid zipfile

>Unprotected zipfile

### Unhandled
>System process limit reached

>Workers killed manually and password not found

>Wrong password encoding


## Warnings
Be aware that bruteforcing is a CPU-intensive process, so you may experience serious system slowdowns while this is running.

Killing the main process will not stop the workers, so if you decide to do so you must manually kill each one.

Using the entire keyspace for long passwords is unlikely to yield results (62^10 is almost a quintillion possible passwords, while one worker can only try several hundreds/thousands each second).

The program does not work well (or at all) for very large archives. If no worker shows progress being made for a significant ammount of time (eg. a minute) this means the archive is too big to process. Alternatively, try running it again with a lower update interval to see if progress is being made.
