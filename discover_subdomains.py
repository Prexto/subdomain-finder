import aiohttp
import asyncio
import time
import os

async def fetch(session, url, semaphore):
    async with semaphore:
        for scheme in ['http', 'https']:
            full_url = f"{scheme}://{url}"
            try:
                async with session.get(full_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        print(f"[+] Active subdomain detected: {full_url}")
                        return full_url
                    elif response.status == 404:
                        print(f"[-] Domain not found: {full_url}")
                    elif response.status == 403:
                        print(f"[-] Forbidden access: {full_url}")
            except aiohttp.ClientConnectorError:
                print(f"[-] Connection error with {full_url}: Unable to connect.")
            except asyncio.TimeoutError:
                print(f"[-] Timeout error with {full_url}: Request took too long.")
            except aiohttp.ClientResponseError as e:
                print(f"[-] HTTP error with {full_url}: {e}")
            except Exception as e:
                print(f"[-] Unexpected error with {full_url}: {e}")
    return None

async def discover_subdomains_and_tlds(domain, tlds, subdomains, semaphore):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for subdomain in subdomains:
            for tld in tlds:
                url = f"{subdomain}.{domain}.{tld}"
                tasks.append(fetch(session, url, semaphore))
        for tld in tlds:
            url = f"{domain}.{tld}"
            tasks.append(fetch(session, url, semaphore))
        results = await asyncio.gather(*tasks)
    return [result for result in results if result]

async def analyze_subdomains_only(domain, tlds, subdomains, semaphore):
    discovered_subdomains = await discover_subdomains_and_tlds(domain, tlds, subdomains, semaphore)
    
    # Filter only subdomains
    subdomains_only = [sub for sub in discovered_subdomains if any(subdomain in sub for subdomain in subdomains)]
    
    output_dir = 'output'
    output_file = save_discovered_subdomains(subdomains_only, domain, output_dir, 'subdomains')
    return subdomains_only, output_file

async def analyze_tlds_only(domain, tlds, semaphore):
    discovered_tlds = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for tld in tlds:
            url = f"{domain}.{tld}"
            tasks.append(fetch(session, url, semaphore))
        results = await asyncio.gather(*tasks)
        discovered_tlds = [result for result in results if result]
    
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

async def menu():
    while True:
        while True:
            print("\nMenu:")
            print("1. Analyze subdomains only")
            print("2. Analyze TLDs only")
            print("3. Analyze all")
            print("4. Exit")
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice in ['1', '2', '3', '4']:
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")

        if choice == '4':
            print("Exiting...")
            break
        
        while True:
            try:
                concurrency = int(input("Enter the number of concurrent requests (10 to 200): ").strip())
                if 10 <= concurrency <= 200:
                    if concurrency > 100:
                        print("Warning: Using more than 100 concurrent requests may overload the system.")
                    break
                else:
                    print("Invalid input. Please enter a number between 10 and 200.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
        
        semaphore = asyncio.Semaphore(concurrency)
        
        while True:
            domain = input("Please enter the domain (without TLD, e.g., 'example'): ").strip()
            if is_valid_domain(domain):
                break
            else:
                print("Invalid domain. Please enter the base domain without any subdomains or TLDs.")
        
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
            results = await discover_subdomains_and_tlds(domain, tlds, subdomains, semaphore)
            subdomains_found = [result for result in results if any(subdomain in result for subdomain in subdomains)]
            tlds_found = [result for result in results if not any(subdomain in result for subdomain in subdomains)]
            
            output_dir = 'output'
            # Save both subdomains and TLDs to one file
            all_results_file = os.path.join(output_dir, f'{domain}_discovered_all.txt')
            with open(all_results_file, 'w') as file:
                for item in subdomains_found + tlds_found:
                    file.write(item + '\n')
            
            subdomains_file = None
            tlds_file = all_results_file
        
        end_time = time.time()
        execution_time = end_time - start_time
        formatted_time = format_execution_time(execution_time)
        
        # Display results
        if choice == '1':
            print(f"\nTotal subdomains found: {len(subdomains_found)}")
            print(f"Discovered subdomains saved to: {subdomains_file}")
        
        if choice == '2':
            print(f"\nTotal TLDs found: {len(tlds_found)}")
            print(f"Discovered TLDs saved to: {tlds_file}")
        
        if choice == '3':
            total_found = len(subdomains_found + tlds_found)
            print(f"\nTotal domains found: {total_found}")
            print(f"Discovered domains saved to: {tlds_file}")
        
        print(f"\nTotal execution time: {formatted_time}")

if __name__ == "__main__":
    asyncio.run(menu())
