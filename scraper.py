import aiohttp
import asyncio
import time
import os
from re import compile
from pystyle import Colors, Colorate, Center
from colorama import Fore
import ctypes

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

TIMEOUT: int = 5
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
REGEX = compile(
    r"(?:^|\D)?((" + r"(?:[1-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"):" + (r"(?:\d|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}"
    + r"|65[0-4]\d{2}|655[0-2]\d|6553[0-5])")
    + r")(?:\D|$)"
)

logo = """
    _   ___ __                ____                           _____                                
   / | / (_) /_____  ___     / __ \_________  _  ____  __   / ___/______________ _____  ___  _____
  /  |/ / / //_/ _ \/ _ \   / /_/ / ___/ __ \| |/_/ / / /   \__ \/ ___/ ___/ __ `/ __ \/ _ \/ ___/
 / /|  / / ,< /  __/  __/  / ____/ /  / /_/ />  </ /_/ /   ___/ / /__/ /  / /_/ / /_/ /  __/ /    
/_/ |_/_/_/|_|\___/\___/  /_/   /_/   \____/_/|_|\__, /   /____/\___/_/   \__,_/ .___/\___/_/     
                                                /____/                        /_/                 """

logo = Center.XCenter(logo)

async def scrape_proxy(url: str, protocol: str, scrapped_proxies):
    global working_links_count
    global error_links
    temp_proxies = 0
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers={'user-agent': user_agent}, 
                timeout=aiohttp.ClientTimeout(total=TIMEOUT)
            ) as response:
                working_links_count += 1
                html = await response.text()
                if tuple(REGEX.finditer(html)):
                    output_filename = f"scraped/{protocol.lower()}.txt"
                    with open(output_filename, 'a') as output_file:
                        for proxy in tuple(REGEX.finditer(html)):
                            if proxy.group(1) not in scrapped_proxies:
                                output_file.write(f'{proxy.group(1)}\n')
                                scrapped_proxies.add(proxy.group(1))
                                temp_proxies += 1
                        print(f'{Fore.GREEN} [~] Found: {temp_proxies} {protocol.upper()} Proxies from {url} | Total: {len(scrapped_proxies)}')
                        set_console_title(f"Proxies: {len(scrapped_proxies)} | Links Working: {working_links_count} | Links not working: {error_links}")
                else:
                    error_links += 1
                    print(f'{Fore.RED} [~] Can\'t Find At: {url}')
    except Exception as e: 
        error_links += 1
        print(f'{Fore.RED} [ERROR AT]: {url} {e}\n')

async def main():
    global working_links_count
    global error_links
    scrapped_proxies = set()

    print(Colorate.Horizontal(Colors.red_to_blue, logo, 1))
    print(f"{Fore.LIGHTWHITE_EX}Choose a protocol to scrape:")
    print("1. SOCKS5")
    print("2. SOCKS4")
    print("3. HTTP")
    choice = input("Enter the number of your choice: ")

    protocols = {
        '1': ('sources/socks5_sources.txt', 'SOCKS5'),
        '2': ('sources/socks4_sources.txt', 'SOCKS4'),
        '3': ('sources/http_sources.txt', 'HTTP'),
    }

    chosen_protocol, output_filename = protocols.get(choice, (None, None))
    if chosen_protocol and output_filename:
        if os.path.exists(chosen_protocol):
            working_links_count = 0
            error_links = 0

            with open(chosen_protocol, 'r') as sources:
                urls = sources.read().splitlines()

                await asyncio.wait(
                    [ asyncio.create_task(scrape_proxy(url, output_filename, scrapped_proxies)) 
                    for url in urls ])

                print(f'{Fore.CYAN}\n [!] Done Scraping {output_filename}...\n [~] Total {output_filename} Proxies: {len(scrapped_proxies)} \n\n [~] Returning to the menu after 5 seconds...')
        else:
            print(f'{Fore.RED} [~] Error: {chosen_protocol} does not exist. Returning to the choice menu after 5 seconds.')
            time.sleep(2)
    else:
        print(f'{Fore.RED} [~] Invalid choice. Please choose a number between 1 and 3.')

    time.sleep(5)
    os.system('cls' if os.name == 'nt' else 'clear')
    return await main()

if __name__ == "__main__":
    asyncio.run(main())
