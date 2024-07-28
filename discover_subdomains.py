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
                    print(f"[+] Discovered subdomain: {url}")
                    discovered_subdomains.append(url)
                else:
                    print(f"[-] {url} does not exist")
            except requests.ConnectionError:
                print(f"[-] {url} does not exist or cannot be reached")
    
    return discovered_subdomains

if __name__ == "__main__":
    domain = "google"
    with open('tlds.txt', 'r') as file:
        tlds = file.read().splitlines()
    discovered_subdomains = discover_subdomains_and_tlds(domain, tlds)
    print("\nDiscovered subdomains:")
    for sub in discovered_subdomains:
        print(sub)
