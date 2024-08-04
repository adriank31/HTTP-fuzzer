import requests
import logging
import random
import string
import threading


# Timeout for requests
TIMEOUT = 5

# Configure logging
logging.basicConfig(filename='fuzzing.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Define the target URL
TARGET_URL = 'http://example.com'  # Change this to the target URL

# Define the list of HTTP methods to fuzz
HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT']

# Define the list of User-Agent headers to test
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/90.0',
    'CustomUserAgent/1.0'
]

# Define the list of HOST headers to test
HOST_HEADERS = [
    'example.com',
    'localhost',
    'malicious.com'
]

# Define custom payloads for POST and PUT methods
PAYLOADS = [
    {'key1': 'value1', 'key2': 'value2'},
    {'username': 'admin', 'password': 'password'},
    {''.join(random.choices(string.ascii_letters + string.digits, k=10)): ''.join(random.choices(string.ascii_letters + string.digits, k=10))}
]

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def fuzz_http_methods(url):
    for method in HTTP_METHODS:  # Loop through each HTTP method
        for payload in PAYLOADS:  # Loop through each payload
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Host': random.choice(HOST_HEADERS)
            }
            try:
                # Try sending the request with the current method and payload
                if method == 'GET':  # If the method is GET
                    response = requests.get(url, headers=headers, timeout=TIMEOUT)
                elif method == 'HEAD':  # If the method is HEAD
                    response = requests.head(url, headers=headers, timeout=TIMEOUT)
                elif method == 'POST':  # If the method is POST
                    response = requests.post(url, data=payload, headers=headers, timeout=TIMEOUT)
                elif method == 'PUT':  # If the method is PUT
                    response = requests.put(url, data=payload, headers=headers, timeout=TIMEOUT)
                
                log_message = f'Method: {method} - Status Code: {response.status_code} - Headers: {headers} - Payload: {payload}'
                print(log_message)
                logging.info(log_message)
            except requests.RequestException as e:
                # Handle any exceptions that occur during the request
                log_message = f'Method: {method} - Error: {e} - Headers: {headers} - Payload: {payload}'
                print(log_message)
                logging.error(log_message)

def fuzz_http_headers(url):
    for user_agent in USER_AGENTS:  # Loop through each User-Agent header
        for host_header in HOST_HEADERS:  # Loop through each Host header
            headers = {
                'User-Agent': user_agent,
                'Host': host_header,
                'Custom-Header': generate_random_string()
            }
            try:
                # Try sending the request with the current headers
                response = requests.get(url, headers=headers, timeout=TIMEOUT)
                log_message = f'User-Agent: {user_agent} - Host: {host_header} - Custom-Header: {headers["Custom-Header"]} - Status Code: {response.status_code}'
                print(log_message)
                logging.info(log_message)
            except requests.RequestException as e:
                # Handle any exceptions that occur during the request
                log_message = f'User-Agent: {user_agent} - Host: {host_header} - Custom-Header: {headers["Custom-Header"]} - Error: {e}'
                print(log_message)
                logging.error(log_message)

def run_fuzzer():
    threads = []
    for func in [fuzz_http_methods, fuzz_http_headers]:  # Loop through each fuzzing function
        thread = threading.Thread(target=func, args=(TARGET_URL,))
        thread.start()
        threads.append(thread)

    for thread in threads:  # Wait for all threads to finish
        thread.join()

if __name__ == '__main__':
    print("Starting Fuzzing...")
    run_fuzzer()
    print("Fuzzing Completed.")
