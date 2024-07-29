import aiohttp
import asyncio
import time
import os
from colorama import Fore, Style, init
import sys
import itertools

# Initialize colorama
init()

async def fetch(session, url, semaphore):
    async with semaphore:
        for scheme in ['http', 'https']:
            full_url = f"{scheme}://{url}"
            try:
                async with session.get(full_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        print(f"{Fore.GREEN}[+] Active subdomain detected: {full_url}{Style.RESET_ALL}")
                        return full_url
                    elif response.status == 404:
                        print(f"{Fore.RED}[-] Domain not found: {full_url}{Style.RESET_ALL}")
                    elif response.status == 403:
                        print(f"{Fore.RED}[-] Forbidden access: {full_url}{Style.RESET_ALL}")
            except aiohttp.ClientConnectorError:
                print(f"{Fore.RED}[-] Connection error with {full_url}: Unable to connect.{Style.RESET_ALL}")
            except asyncio.TimeoutError:
                print(f"{Fore.RED}[-] Timeout error with {full_url}: Request took too long.{Style.RESET_ALL}")
            except aiohttp.ClientResponseError as e:
                print(f"{Fore.RED}[-] HTTP error with {full_url}: {e}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[-] Unexpected error with {full_url}: {e}{Style.RESET_ALL}")
    return None

async def discover_subdomains_and_tlds(domain, tlds, subdomains, semaphore):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for subdomain in subdomains:
            for tld in tlds:
                url = f"{subdomain}.{domain}.{tld}"
                tasks.append(fetch(session, url, semaphore))
        results = await asyncio.gather(*tasks)
    return [result for result in results if result]

async def analyze_subdomains_only(domain, tlds, subdomains, semaphore):
    async with aiohttp.ClientSession() as session:
        discovered_subdomains = await discover_subdomains_and_tlds(domain, tlds, subdomains, semaphore)
    
    print(f"\n{Fore.CYAN}Discovered subdomains:{Style.RESET_ALL}")
    for sub in discovered_subdomains:
        print(sub)
    
    output_dir = 'output'
    output_file = save_discovered_subdomains(discovered_subdomains, domain, output_dir, 'subdomains')
    
    return discovered_subdomains, output_file

async def analyze_tlds_only(domain, tlds, semaphore):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for tld in tlds:
            url = f"{domain}.{tld}"
            tasks.append(fetch(session, url, semaphore))
        results = await asyncio.gather(*tasks)
    discovered_tlds = [result for result in results if result]
    
    print(f"\n{Fore.CYAN}Discovered TLDs:{Style.RESET_ALL}")
    for tld in discovered_tlds:
        print(tld)

    output_dir = 'output'
    output_file = os.path.join(output_dir, f'{domain}_discovered_tlds.txt')
    with open(output_file, 'w') as file:
        for tld in discovered_tlds:
            file.write(tld + '\n')
    
    return discovered_tlds, output_file

def is_valid_domain(domain):
    return domain.count('.') == 0

def save_discovered_subdomains(subdomains, domain, output_dir, file_suffix):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, f'{domain}_discovered_{file_suffix}.txt')
    with open(output_file, 'w') as file:
        for sub in subdomains:
            file.write(sub + '\n')
    return output_file

def format_execution_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = round(hours)
    minutes = round(minutes)
    seconds = round(seconds)
    if hours > 0:
        return f"{hours} hour(s), {minutes} minute(s), {seconds} second(s)"
    elif minutes > 0:
        return f"{minutes} minute(s), {seconds} second(s)"
    else:
        return f"{seconds} second(s)"

def animate_exit():
    animation = itertools.cycle(['|', '/', '-', '\\'])
    for _ in range(20):  # Number of animation cycles
        sys.stdout.write(f"\rExiting... {next(animation)}")
        sys.stdout.flush()
        time.sleep(0.1)
    print()  # Move to the next line

async def menu():
    while True:
        while True:
            print("\nMenu:")
            print(f"{Fore.YELLOW}1. Analyze subdomains only{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}2. Analyze TLDs only{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}3. Analyze all{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}4. Exit{Style.RESET_ALL}")
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice in ['1', '2', '3', '4']:
                break
            else:
                print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and 4.{Style.RESET_ALL}")

        if choice == '4':
            print(f"{Fore.GREEN}Exiting...{Style.RESET_ALL}")
            animate_exit()
            break
        
        while True:
            try:
                concurrency = int(input(f"{Fore.CYAN}Enter the number of concurrent requests (10 to 200): {Style.RESET_ALL}").strip())
                if 10 <= concurrency <= 200:
                    if concurrency > 100:
                        print(f"{Fore.YELLOW}Warning: Using more than 100 concurrent requests may overload the system.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED}Invalid input. Please enter a number between 10 and 200.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter a valid integer.{Style.RESET_ALL}")
        
        semaphore = asyncio.Semaphore(concurrency)
        
        while True:
            domain = input(f"{Fore.CYAN}Please enter the domain (without TLD, e.g., 'example'): {Style.RESET_ALL}").strip()
            if is_valid_domain(domain):
                break
            else:
                print(f"{Fore.RED}Invalid domain. Please enter the base domain without any subdomains or TLDs.{Style.RESET_ALL}")
        
        with open('temp.txt', 'r') as file:
            tlds = file.read().splitlines()
        with open('subdomains.txt', 'r') as file:
            subdomains = file.read().splitlines()
        
        start_time = time.time()
        if choice == '1':
            subdomains_found, subdomains_file = await analyze_subdomains_only(domain, tlds, subdomains, semaphore)
            tlds_found = []  # No TLDs analyzed
            tlds_file = None
        elif choice == '2':
            tlds_found, tlds_file = await analyze_tlds_only(domain, tlds, semaphore)
            subdomains_found = []  # No subdomains analyzed
            subdomains_file = None
        elif choice == '3':
            subdomains_found, subdomains_file = await analyze_subdomains_only(domain, tlds, subdomains, semaphore)
            tlds_found, tlds_file = await analyze_tlds_only(domain, tlds, semaphore)
        
        end_time = time.time()
        execution_time = end_time - start_time
        formatted_time = format_execution_time(execution_time)
        
        # Display results
        if choice == '3' or choice == '1':
            print(f"\n{Fore.GREEN}Total subdomains found: {len(subdomains_found)}{Style.RESET_ALL}")
            if subdomains_file:
                print(f"{Fore.GREEN}Discovered subdomains saved to: {subdomains_file}{Style.RESET_ALL}")
        
        if choice == '3' or choice == '2':
            print(f"\n{Fore.GREEN}Total TLDs found: {len(tlds_found)}{Style.RESET_ALL}")
            if tlds_file:
                print(f"{Fore.GREEN}Discovered TLDs saved to: {tlds_file}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}Total execution time: {formatted_time}{Style.RESET_ALL}")

if __name__ == "__main__":
    asyncio.run(menu())
