#!/usr/bin/env python3
import requests
import threading
import argparse
import sys
from queue import Queue
from time import time, sleep
from datetime import datetime
import random
import string
import os

# Constants for Matrix-style visuals
MATRIX_COLOR = "\033[92m"  # Bright green color for the Matrix effect
RESET_COLOR = "\033[0m"    # Reset terminal color to default

# Initialize global variables
lock = threading.Lock()  # Lock for thread-safe printing
payloads = []  # List of payloads loaded from file
headers = {}   # Custom HTTP headers loaded from file

# Matrix-style intro displayed when the script starts
def matrix_intro():
    """
    Display a Matrix-style ASCII art banner with a disclaimer.
    """
    matrix_text = f"""
{MATRIX_COLOR}
███████╗███████╗██╗     ██╗██╗    ███╗   ███╗ █████╗ ███████╗███████╗
██╔════╝██╔════╝██║     ██║██║    ████╗ ████║██╔══██╗╚══███╔╝██╔════╝
█████╗  █████╗  ██║     ██║██║    ██╔████╔██║███████║  ███╔╝ █████╗  
██╔══╝  ██╔══╝  ██║     ██║██║    ██║╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝  
███████╗███████╗███████╗██║███████╗██║ ╚═╝ ██║██║  ██║███████╗███████╗
╚══════╝╚══════╝╚══════╝╚═╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝
                               By Adrian Korwel
{RESET_COLOR}
"""
    print(matrix_text)
    print(f"{MATRIX_COLOR}Legal Disclaimer: Use this tool only on systems you are authorized to test.{RESET_COLOR}")

# Load payloads from a file
def load_payloads(payload_file):
    """
    Load SQL Injection payloads from a specified file.
    :param payload_file: Path to the file containing payloads.
    :return: List of payloads.
    """
    if not os.path.exists(payload_file):
        print(f"{MATRIX_COLOR}[ERROR] Payload file '{payload_file}' not found.{RESET_COLOR}")
        sys.exit(1)

    with open(payload_file, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Load custom headers from a file
def load_headers(header_file):
    """
    Load custom HTTP headers from a specified file.
    :param header_file: Path to the file containing headers in 'Key: Value' format.
    :return: Dictionary of headers.
    """
    if not os.path.exists(header_file):
        print(f"{MATRIX_COLOR}[WARNING] Header file '{header_file}' not found. Using default headers.{RESET_COLOR}")
        return {}

    with open(header_file, 'r') as file:
        return {line.split(':')[0].strip(): line.split(':', 1)[1].strip() for line in file if ':' in line}

# Test SQL Injection vulnerabilities on a single URL
def test_sql_injection(url, payloads):
    """
    Test a single URL for SQL injection vulnerabilities.
    :param url: The target URL.
    :param payloads: List of SQL Injection payloads to test.
    """
    global headers
    vulnerable = False  # Flag to track if a vulnerability is detected

    for payload in payloads:
        try:
            # Log the payload being tested
            with lock:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"{MATRIX_COLOR}[{now}] Testing payload: {payload} on {url}{RESET_COLOR}")

            # Send the HTTP request with the payload
            response = requests.get(url, headers=headers, params={"input": payload}, timeout=10)

            # Check for potential SQL injection by analyzing the response
            if "error" in response.text.lower() or response.elapsed.total_seconds() > 10:
                print(f"{MATRIX_COLOR}[DETECTED] SQL Injection found: {url}{RESET_COLOR}")
                print(f"{MATRIX_COLOR}Payload: {payload}{RESET_COLOR}")
                vulnerable = True
                break
        except requests.exceptions.RequestException as e:
            # Log any request errors
            with lock:
                print(f"{MATRIX_COLOR}[ERROR] Request failed for {url}: {e}{RESET_COLOR}")

    if not vulnerable:
        print(f"{MATRIX_COLOR}[INFO] No vulnerabilities detected for {url}.{RESET_COLOR}")

# Worker function for multi-threaded scanning
def worker(queue):
    """
    Worker thread function to process URLs from the queue.
    :param queue: Queue containing URLs to be tested.
    """
    while not queue.empty():
        url = queue.get()
        test_sql_injection(url, payloads)
        queue.task_done()

# Main function
def main():
    """
    Main entry point of the script.
    Parses arguments, loads configurations, and starts the scanner.
    """
    parser = argparse.ArgumentParser(
        description="Matrix-Style HTTP Fuzzer - By Adrian Korwel",
        epilog=f"Example Usage: {MATRIX_COLOR}./matrix_fuzzer.py -u http://example.com{RESET_COLOR}"
    )

    # Define command-line arguments
    parser.add_argument("-u", "--url", help="Single URL to test")
    parser.add_argument("-p", "--pipe", action="store_true", help="Read URLs from pipeline input")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads to use for scanning")
    parser.add_argument("--payloads", type=str, default="payloads.txt", help="File containing SQLi payloads")
    parser.add_argument("--headers", type=str, default="headers.txt", help="File containing custom HTTP headers")

    args = parser.parse_args()

    # Display the Matrix-style intro
    matrix_intro()

    # Load payloads and headers
    global payloads, headers
    payloads = load_payloads(args.payloads)
    headers = load_headers(args.headers)

    # Multi-threading setup
    queue = Queue()

    # Handle a single URL scan
    if args.url:
        print(f"{MATRIX_COLOR}[INFO] Starting Single URL Scan...{RESET_COLOR}")
        queue.put(args.url)

    # Handle piped input for multiple URLs
    elif args.pipe:
        print(f"{MATRIX_COLOR}[INFO] Reading URLs from pipeline input...{RESET_COLOR}")
        for url in sys.stdin:
            queue.put(url.strip())

    else:
        print(f"{MATRIX_COLOR}[ERROR] No URL or pipeline input provided. Use -h for help.{RESET_COLOR}")
        sys.exit(1)

    # Start worker threads
    threads = []
    for _ in range(args.threads):
        thread = threading.Thread(target=worker, args=(queue,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    queue.join()

    # Log completion of the scan
    print(f"{MATRIX_COLOR}[INFO] Scanning completed.{RESET_COLOR}")

if __name__ == "__main__":
    main()
