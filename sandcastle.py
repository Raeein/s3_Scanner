#!/usr/bin/env python3

import sys
import requests
import time
import json
from argparse import ArgumentParser

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


parser = ArgumentParser()
parser.add_argument("-t", "--target",
                    help="Select a target stem name (e.g. 'shopify')", required="True")
parser.add_argument("-f", "--file",
                    help="Select the wordlist file to use (default: bucket-names.txt)", default="bucket-names.txt")
parser.add_argument("-v", "--verbose", action='store_true',
                    help="Prints out everything - use this flag for debugging preferably",)
parser.add_argument("-s", "--silent", action='store_false',
                    help="Only prints out the found buckets")
parser.add_argument("-oP", "--public", action='store_false',
                    help="Only prints out the found public buckets")
args = parser.parse_args()

if args.silent:
    print(bcolors.HEADER, """
    ____             __             __  __   
    / __/__ ____  ___/ /______ ____ / /_/ /__ 
    _\ \/ _ `/ _ \/ _  / __/ _ `(_-</ __/ / -_)
    /___/\_,_/_//_/\_,_/\__/\_,_/___/\__/_/\__/ 
                                                
    S3 bucket enumeration // release v2.0.0

    """)


def proccess_file():
    with open(args.file, 'r') as file:
        words = file.read().splitlines()
        lineCount = len(words)
    if lineCount == 0:
        print("Empty text file, Exiting...")
        sys.exit()
    return words, lineCount

def create_mutations(words, target):
    all_mutations = []
    for word in words:
        all_mutations.append(f"http://{target}-{word}.s3.amazonaws.com")
        all_mutations.append(f"http://{target}.{word}.s3.amazonaws.com")
        all_mutations.append(f"http://{word}-{target}.s3.amazonaws.com")
        all_mutations.append(f"http://{word}.{target}.s3.amazonaws.com")
        all_mutations.append(f"http://s3.amazonaws.com/{target}-{word}/")
        all_mutations.append(f"http://s3.amazonaws.com/{target}.{word}/")
        all_mutations.append(f"http://s3.amazonaws.com/{word}-{target}/")
        all_mutations.append(f"http://s3.amazonaws.com/{word}.{target}/")
    return all_mutations


def print_output(url, status_code, public):
    combined = []
    combined.extend([url, status_code])
    if public:
        print(bcolors.OKGREEN, "{: <75} {: <75}".format(*combined), end="\n")
    else:
        print(bcolors.WARNING, "{: <75} {: <75}".format(*combined), end="\n")


def check_for_buckets(all_mutations):

    buckets_found = {}

    for mutation in all_mutations:
        if args.verbose:
            print(bcolors.OKCYAN,f"Checking {mutation}")
        try:
            reply = requests.head(mutation)
        except (requests.exceptions.ConnectionError, KeyboardInterrupt) as e:
            if (e.__class__.__name__) == "KeyboardInterrupt":
                print("\nExiting...")
                sys.exit()
            if args.silent:
                print(bcolors.OKBLUE,f"Connection refused for {mutation}")
                status_code = 404

        status_code = reply.status_code

        if status_code == 404:
            pass
        elif 'Bad Request' in reply.reason:
            pass 
        elif status_code == 200:
            print_output(mutation, f"({status_code})", True)
            buckets_found[mutation] = status_code
        elif reply.status_code == 403:
            if args.public:
                print_output(mutation, f"({status_code})", False)
            buckets_found[mutation] = status_code
        elif 'Slow Down' in reply.reason:
            print(bcolors.FAIL, "[*] You've been rate limited, exiting the program!")
            sys.exit()
        else:
            buckets_found[mutation] = status_code
            
    return buckets_found


def start_timer():

    start_time = time.time()
    return start_time


def stop_timer(start_time):

    elapsed_time = time.time() - start_time
    formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

    print("\n")
    print(f" Time Taken: {formatted_time}")
    print("\n")

def main():
    words, lineCount = proccess_file()
    start = start_timer()
    bucket_names = args.file
    target  = args.target
    if args.silent:
        print(bcolors.WARNING,f"[*] Starting Enumeration | Target: {target} | Words loaded: {lineCount} | Text file: {bucket_names}\n\n")
    all_mutations = create_mutations(words, target)
    results = check_for_buckets(all_mutations)
    print(results)
    json_data = json.dumps(results)
    print("\n\n\n\n")
    print(json_data)
    stop_timer(start)
    print(bcolors.WARNING, f"[*] Enumeration of {args.target} S3 buckets completed.")


if __name__ == "__main__":
    main()
