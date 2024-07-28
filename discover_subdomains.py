import aiohttp
import asyncio

async def fetch(session, url):
    for scheme in ['http', 'https']:
        full_url = f"{scheme}://{url}"
        try:
            async with session.get(full_url) as response:
                if response.status == 200:
                    print(f"[+] Active subdomain detected: {full_url}")
                    return full_url
        except aiohttp.ClientError as e:
            print(f"[-] Error with {full_url}: {e}")
    return None

async def discover_subdomains_and_tlds(domain, tlds, subdomains):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for subdomain in subdomains:
            for tld in tlds:
                url = f"{subdomain}.{domain}.{tld}"
                tasks.append(fetch(session, url))
        results = await asyncio.gather(*tasks)
    return [result for result in results if result]

def is_valid_domain(domain):
    return domain.count('.') == 0

if __name__ == "__main__":
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
    
    discovered_subdomains = asyncio.run(discover_subdomains_and_tlds(domain, tlds, subdomains))
    print("\nDiscovered subdomains:")
    for sub in discovered_subdomains:
        print(sub)
