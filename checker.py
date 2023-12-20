import requests
from concurrent.futures import ThreadPoolExecutor
from pystyle import Colors, Colorate, Center
from colorama import Fore
import os
import time
import ctypes


def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)


valid_proxies = 0
invalid_proxies = 0

logo = """
    _   ___ __                ____                           ________              __            
   / | / (_) /_____  ___     / __ \_________  _  ____  __   / ____/ /_  ___  _____/ /_____  _____
  /  |/ / / //_/ _ \/ _ \   / /_/ / ___/ __ \| |/_/ / / /  / /   / __ \/ _ \/ ___/ //_/ _ \/ ___/
 / /|  / / ,< /  __/  __/  / ____/ /  / /_/ />  </ /_/ /  / /___/ / / /  __/ /__/ ,< /  __/ /    
/_/ |_/_/_/|_|\___/\___/  /_/   /_/   \____/_/|_|\__, /   \____/_/ /_/\___/\___/_/|_|\___/_/     
                                                /____/                                           
                               [Made by @FR12Gimenez Github]                                     """

logo = Center.XCenter(logo)

def check_http_proxy(proxy):
    url = 'http://azenv.net/'  # You can change the URL for HTTP proxies
    proxies = {'http': proxy, 'https': proxy}
    return check_proxy(url, proxies)

def check_proxy(url, proxies):
    global valid_proxies
    global invalid_proxies
    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        if response.status_code == 200:
            valid_proxies += 1
            set_console_title(f"Proxies Working: {valid_proxies} | Invalid Proxies: {invalid_proxies}")
            ip_port = proxies[list(proxies.keys())[0]].replace('http://', '').replace('https://', '')
            print(f'{Fore.GREEN}[+] Proxy {ip_port} is working.')
            return True
    except Exception as e:
        invalid_proxies += 1
        set_console_title(f"Proxies Working: {valid_proxies} | Invalid Proxies: {invalid_proxies}")
        ip_port = proxies[list(proxies.keys())[0]].replace('http://', '').replace('https://', '')
        print(f'{Fore.RED}[-] Proxy {ip_port} is not working.')
        return False

def read_proxies_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return []

def write_valid_proxies_to_file(file_path, valid_proxies):
    with open(file_path, 'w') as file:
        file.write('\n'.join(valid_proxies))

async def main():
    global valid_proxies
    global invalid_proxies
    http_proxies = read_proxies_from_file('scraped/http.txt')

    print(Colorate.Horizontal(Colors.red_to_blue, logo, 1))
    print("Choose which proxies to check:")
    print("1. HTTP Proxies")
    choices = input("> ")

    selected_proxies = []
    if '1' in choices:
        selected_proxies.extend(http_proxies)

    if not selected_proxies:
        print("No proxies selected. Exiting.")
        return
    
    print("How many threads would you like to run?")
    num_threads = int(input("> "))

    valid_http = []
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(check_http_proxy, selected_proxies))
        valid_http.extend([proxy for proxy, result in zip(selected_proxies, results) if result])

    if valid_http:
        write_valid_proxies_to_file('checked/http.txt', valid_http)
    
    print(f'{Fore.CYAN}Valid proxies written in the checked folder.')
    time.sleep(3)
    os.system('cls' if os.name == 'nt' else 'clear')
    return await main()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())