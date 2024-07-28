import aiohttp
import asyncio
import time  # Import the module to measure time

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

    with open('tlds.txt', 'r') as file:
        tlds = file.read().splitlines()
    with open('subdomains.txt', 'r') as file:
        subdomains = file.read().splitlines()
    
    discovered_subdomains = asyncio.run(discover_subdomains_and_tlds(domain, tlds, subdomains, semaphore))

    print("\nDiscovered subdomains:")
    for sub in discovered_subdomains:
        print(sub)

    end_time = time.time()  # Record end time
    execution_time = end_time - start_time  # Calculate execution time
    print(f"\nTotal execution time: {execution_time:.2f} seconds")  # Display execution time
