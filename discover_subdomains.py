import requests

def discover_subdomains_and_tlds(domain, tlds):
    with open('subdomains.txt', 'r') as file:
        subdomains = file.read().splitlines()
    
    discovered_subdomains = []
    
    for subdomain in subdomains:
        for tld in tlds:
            url = f"http://{subdomain}.{domain}.{tld}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    print(f"[+] Active subdomain detected: {url}")
                    discovered_subdomains.append(url)
                else:
                    print(f"[-] {url} does not exist")
            except requests.ConnectionError:
                print(f"[-] {url} does not exist or cannot be reached")
    
    return discovered_subdomains

def is_valid_domain(domain):
    # Ensure the domain does not contain any additional dots
    if domain.count('.') > 0:
        return False
    return True

if __name__ == "__main__":
    while True:
        domain = input("Please enter the domain (without TLD, e.g., 'example'): ").strip()
        if is_valid_domain(domain):
            break
        else:
            print("Invalid domain. Please enter the base domain without any subdomains or TLDs.")

    with open('tlds.txt', 'r') as file:
        tlds = file.read().splitlines()
    discovered_subdomains = discover_subdomains_and_tlds(domain, tlds)
    print("\nDiscovered subdomains:")
    for sub in discovered_subdomains:
        print(sub)
