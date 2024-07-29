# Discover Domains

Discover Domains is a Python script designed for efficient domain and subdomain discovery. Utilizing asynchronous requests, it probes for active subdomains and Top-Level Domains (TLDs) with enhanced performance. The script provides an interactive menu for flexible scanning options and outputs results in a clear and organized manner.

## Features

- **Subdomain Discovery**: Identify active subdomains for a specified domain.
- **TLD Discovery**: Detect active TLDs associated with a given domain.
- **Concurrent Requests**: Leverages asynchronous processing to optimize performance.
- **Interactive Menu**: Choose between analyzing subdomains, TLDs, or both.
- **Colored Output**: Employs `colorama` for visually distinct terminal output.

## Installation

1. **Clone the Repository**

   Clone this repository to your local machine using:

   ```bash
   git clone https://github.com/Prexto/subdomain-finder.git
   ```

**2. Navigate to the Project Directory**

Change to the project directory:

```bash
cd discover-domains
```

**3. Install Python Dependencies**

Ensure you have Python 3.7 or higher installed. Install the necessary Python packages using the provided requirements.txt file:

```bash
pip install -r requirements.txt
```

This will install the following required packages:

- aiohttp

- colorama

## Usage

**1. Run the Script**

Execute the script via the command line:

```bash
python discover_subdomains.py
```

**2. Interactive Menu**

Once the script starts, you will be presented with an interactive menu. The available options are:

```bash
1: Analyze subdomains only
2: Analyze TLDs only
3: Analyze both subdomains and TLDs
4: Exit the script
```

**Selecting an Option:**

Enter the number corresponding to the desired option and press Enter.

For options 1 and 2, the script will perform the chosen analysis and output the results.

Option 3 performs both analyses and combines results into a single file.

**3. Set Concurrency Level**

After selecting an option, you will be prompted to enter the number of concurrent requests. The acceptable range is between 10 and 200. Enter a number within this range and press Enter.

**NOTE: Using more than 100 concurrent requests may overload the system. A warning will be displayed if you choose a value greater than 100.**

**4. Provide Domain**

The script will then prompt you to enter the base domain (e.g., example), without any TLDs or subdomains. Input the domain and press Enter.

**5. Results and Output**

The script will process the domain based on the selected options and concurrency level.

Results will be saved in the output directory:

**Subdomains: domain_discovered_subdomains.txt**

**TLDs: domain_discovered_tlds.txt**

The terminal will display the total execution time, the number of domains discovered, and the file paths where results are saved.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome. Please open issues or submit pull requests for any improvements or suggestions.
