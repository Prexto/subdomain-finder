import aiohttp
import asyncio

async def fetch(session, url, semaphore):
    async with semaphore:
        for scheme in ['http', 'https']:
            full_url = f"{scheme}://{url}"
            try:
                async with session.get(full_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        print(f"[+] Active subdomain detected: {full_url}")
                        return full_url
            except aiohttp.ClientError as e:
                print(f"[-] Error with {full_url}: {e}")
            except asyncio.TimeoutError:
                print(f"[-] Timeout with {full_url}")
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
    return domain.count('.') == 0

if __name__ == "__main__":
    # Obtener el número de solicitudes concurrentes del usuario
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
