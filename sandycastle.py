#!/usr/bin/env python3

import sys
import requests
import time
from argparse import ArgumentParser
try:
    from concurrent.futures import ThreadPoolExecutor
    from requests_futures.sessions import FuturesSession
    from concurrent.futures._base import TimeoutError
except ImportError:
    print("[!] Please pip install requirements.txt.")
    sys.exit()


class Custom_colors:
    HEADER = '\033[95m' #Light Pink-Puprle?
    GREEN = '\033[92m'
    ORANGE = '\033[33m'
    BLUE = '\033[94m'
    OKCYAN = '\033[96m'
    RED = '\033[31m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


parser = ArgumentParser()
parser.add_argument("-t", "--target",
                    help="Select a target stem name (e.g. 'shopify')", required="True")
parser.add_argument("-f", "--file",
                    help="Select the wordlist file to use (default: bucket-names.txt)", default="bucket-names.txt")
parser.add_argument("-o", "--output",
                    help="Select output file to use (default: output_\'target\'.txt)", default="default.txt")
parser.add_argument("-th", "--threads",
                    help="Number of threads (default: 5)", default=5, type=int)
parser.add_argument("-v", "--verbose", action='store_true',
                    help="Prints out everything - use this flag for debugging preferably",)
parser.add_argument("-s", "--silent", action='store_false',
                    help="Only prints out the found buckets")
parser.add_argument("-oP", "--public", action='store_false',
                    help="Only prints out the found public buckets")
args = parser.parse_args()

if args.silent:
    print(Custom_colors.HEADER, """
   _____                 __         ______           __  __        ___    ____ 
  / ___/____ _____  ____/ /_  __   / ____/___ ______/ /_/ /__     |__ \  / __ \\
  \__ \/ __ `/ __ \/ __  / / / /  / /   / __ `/ ___/ __/ / _ \    __/ / / / / /
 ___/ / /_/ / / / / /_/ / /_/ /  / /___/ /_/ (__  ) /_/ /  __/   / __/_/ /_/ / 
/____/\__,_/_/ /_/\__,_/\__, /   \____/\__,_/____/\__/_/\___/   /____(_)____/  
                       /____/                                                  

    S3 bucket enumeration // release v2.0.0

    """)


def proccess_file():
    with open(args.file, 'r') as file:
        words = file.read().splitlines()
    if len(words) == 0:
        print("Empty text file, Exiting...")
        sys.exit()
    return words

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

def fmt_output(data):
 
    if data['access'] == 'public':
        ansi = Custom_colors.BOLD + Custom_colors.GREEN
    elif data['access'] == 'protected':
        ansi = Custom_colors.BOLD + Custom_colors.ORANGE
    elif data['access'] == 'disabled':
        ansi = Custom_colors.BOLD + Custom_colors.RED
    elif data['access'] == 'moved':
        ansi = Custom_colors.BOLD + Custom_colors.BLUE
    else:
        ansi = Custom_colors.BOLD + Custom_colors.RED

    sys.stdout.write('  ' + ansi + data['msg'] + ': ' + data['target'] + Custom_colors.ENDC + '\n')
    output_file = args.output

    if output_file == "default.txt":
        target = args.target.replace("/", "_")
        output_file = f"output_{target}.txt"

    with open(output_file, 'a', encoding='utf-8') as log_writer:
        log_writer.write(f'{data["msg"]}: {data["target"]}\n')


def print_s3_response(reply):
 
    data = {'platform': 'aws', 'msg': '', 'target': '', 'access': ''}

    if reply.status_code == 404:
        pass
    elif 'Bad Request' in reply.reason:
        pass
    elif reply.status_code == 200:
        data['msg'] = 'OPEN S3 BUCKET'
        data['target'] = reply.url
        data['access'] = 'public'
        fmt_output(data)
    elif reply.status_code == 403 and args.public:
        data['msg'] = 'Protected S3 Bucket'
        data['target'] = reply.url
        data['access'] = 'protected'
        fmt_output(data)
    elif reply.status_code == 301 and args.public:
        data['msg'] = 'Moved Permanently'
        data['target'] = reply.url
        data['access'] = 'moved'
        fmt_output(data)
    elif 'Slow Down' in reply.reason:
        print("[!] You've been rate limited, skipping rest of the check!")
        return 'breakout'
    else:
        print(f" Unknown status codes being received from {reply.url}:\n"
              f"       {reply.status_code}: {reply.reason}")

    return None


def get_urls(all_mutations, threads=5, callback=''):
    tick = {}
    tick['total'] = len(all_mutations)
    tick['current'] = 0
    buckets_found = {}
    queue = [all_mutations[x:x+threads] for x in range(0, len(all_mutations), threads)]


    for batch in queue:
        session = FuturesSession(executor=ThreadPoolExecutor(max_workers=threads+5))
        batch_pending = {}
        batch_results = {}

        for url in batch:
            batch_pending[url] = session.get(url, allow_redirects=True)

        for url in batch_pending:
            try:
                if args.verbose:
                    print(Custom_colors.OKCYAN,f"Checking: {url}")
                batch_results[url] = batch_pending[url].result(timeout=30)
            except requests.exceptions.ConnectionError as error_msg:
                if args.silent:
                    print(f"  [!] Connection error for: {url}")
                    if args.verbose:
                        print(error_msg)
            except TimeoutError:
                if args.silent:
                    print(f" [!] Timeout on {url}. Investigate if there are"
                         " many of these")
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit()

        for url in batch_results:
            check = callback(batch_results[url])
            if check == 'breakout':
                return
        tick['current'] += threads
        sys.stdout.flush()
        sys.stdout.write(Custom_colors.HEADER)
        sys.stdout.write(f"  {tick['current']}/{tick['total']} completed...")
        sys.stdout.write('\r')
    sys.stdout.write('                            \r')


def check_s3_buckets(all_mutations, threads):

    if args.silent:
        wordlist_length = len(all_mutations)
        print(Custom_colors.WARNING,f"[*] Starting Enumeration | Target: {args.target} | Total mutations: {wordlist_length} | Threads: {args.threads}\n\n")
    start_time = start_timer()

    get_urls(all_mutations,
                callback=print_s3_response,
                threads=threads)

    stop_timer(start_time)



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
    words = proccess_file()
    target = args.target
    all_mutations = create_mutations(words, target)
    check_s3_buckets(all_mutations, args.threads)
    print(Custom_colors.WARNING, f"[*] Enumeration of {args.target} S3 buckets completed.")


if __name__ == "__main__":
    main()
