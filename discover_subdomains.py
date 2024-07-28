import aiohttp
import asyncio
import time
import os  # Import os for directory and file operations

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
        results = await asyncio.gather(*tasks)
    return [result for result in results if result]

def is_valid_domain(domain):
    # Check if the domain is valid (should not contain dots)
    return domain.count('.') == 0

def save_discovered_subdomains(subdomains, domain, output_dir):
    # Create output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Define the output file path with domain name
    output_file = os.path.join(output_dir, f'{domain}_discovered_subdomains.txt')
    
    # Write discovered subdomains to the file
    with open(output_file, 'w') as file:
        for sub in subdomains:
            file.write(sub + '\n')
    return output_file

def format_execution_time(seconds):
    # Convert seconds to a formatted string with hours, minutes, and seconds
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

if __name__ == "__main__":
    start_time = time.time()  # Record start time

    # Get the number of concurrent requests from the user
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
    
    discovered_subdomains = asyncio.run(discover_subdomains_and_tlds(domain, tlds, subdomains, semaphore))

    print("\nDiscovered subdomains:")
    for sub in discovered_subdomains:
        print(sub)
    
    # Define output directory
    output_dir = 'output'

    # Save discovered subdomains to a file with domain name and get the file path
    output_file = save_discovered_subdomains(discovered_subdomains, domain, output_dir)

    # Print the total number of discovered subdomains and the file path
    print(f"\nTotal subdomains found: {len(discovered_subdomains)}")
    print(f"Discovered subdomains saved to: {output_file}")

    end_time = time.time()  # Record end time
    execution_time = end_time - start_time  # Calculate execution time
    formatted_time = format_execution_time(execution_time)
    print(f"\nTotal execution time: {formatted_time}")  # Display execution time
