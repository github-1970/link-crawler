import argparse
import requests
import re
import os
import sys
from urllib.parse import urlparse
import base64

def collect_links(url, pattern):
    # Retrieve the web page content
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the web page.")
        return []

    # Extract the protocol and host from the main URL
    parsed_url = re.match(r"(https?://[^/]+)", url)
    if not parsed_url:
        print("Invalid URL format.")
        return []

    main_url = parsed_url.group(1)

    # Find all value matching in the '' or ""
    quoted_values = re.findall('\"(.*?)\"', response.text)
    quoted_values.append( re.findall("\'(.*?)\'", response.text) )

    # All array in one array
    quoted_values = flatten_array(quoted_values)

    # Find correct links matching the regex pattern
    links = check_pattern(quoted_values, pattern)

    # Get values if has / or \
    links = filter_paths(links)

    # Append the main URL to links that don't have the protocol (convert links to correct links)
    # # Append the main URL to links that don't have the protocol
    # temp_links = []
    # for link in links:
    #   if not link.startswith(("http://", "https://", "//")):
    #     temp_links.append(main_url + link)
    #   elif link.startswith("//"):
    #     temp_links.append('http:' + link)  
    #   else:
    #     temp_links.append(link)
    # links = temp_links
    links = [main_url + link if not link.startswith(("http://", "https://", "//")) else 'https:' + link if link.startswith("//") else link for link in links]

    # Check Links is valid
    # links = remove_links_with_errors(links)

    return links

def save_links_to_file(links, url, pattern):
    host = extract_host(url)
    pattern = generate_safe_folder_name(pattern)
    folder_path = os.path.join("public", host, pattern)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, "links.txt")

    with open(file_path, "w", encoding="utf-8") as file:
        for link in links:
            file.write(link + "\n")

def check_pattern(quoted_values, pattern):
  links = []
  for link in quoted_values:
    link = re.findall(pattern, str(link))
    if (len(link) >= 1):
      links.extend(link)
  return links

def flatten_array(arr):
    result = []
    for item in arr:
        if isinstance(item, list):
            result.extend(flatten_array(item))
        else:
            result.append(item)
    return result

def remove_links_with_errors(links):
    valid_links = []
    for link in links:
        try:
            response = requests.head(link)
            print(response.status_code)
            response.raise_for_status()
            valid_links.append(link)
        except requests.exceptions.RequestException:
            pass
    return valid_links

def filter_paths(array):
    filtered_array = [item for item in array if '/' in item or '\\' in item]
    return filtered_array

def extract_host(url):
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    return host

def generate_safe_folder_name(value):
    if isinstance(value, str):
        value = value.encode('utf-8')
    safe_name = base64.b64encode(value).decode('utf-8')
    safe_name = safe_name.replace('/', '_')
    return safe_name

def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Website Link Collector")

    # Add the command line arguments
    parser.add_argument("-u", "--url", help="Main Website URL", required=True)
    parser.add_argument("-p", "--pattern", help="Regex Pattern", required=True)

    # Parse the arguments
    args = parser.parse_args()

    # Collect links
    print("Collecting links from the webpage...")
    links = collect_links(args.url, args.pattern)

    # Display the results
    if links:
        print(f"Found {len(links)} link(s) matching the regex pattern.")
        save_links_to_file(links, args.url, args.pattern)
        print("Saving the links to links.txt file.")
    else:
        print("No links found matching the regex pattern.")
        if os.path.exists("links.txt"):
            os.remove("links.txt")


if __name__ == "__main__":
    main()
