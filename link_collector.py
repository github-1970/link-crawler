import argparse
import requests
import re
import os
import sys
import base64
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def collect_links_from_quote(url, pattern):
    response = get_response(url)

    # Extract the protocol and host from the main URL
    parsed_url = re.match(r"(https?://[^/]+)", url)
    if not parsed_url:
        print("Invalid URL format.")
        return []

    main_url = parsed_url.group(1)

    # Find all value matching in the '' or ""
    quoted_values = re.findall('"(.*?)"', response.text)
    quoted_values.append(re.findall("'(.*?)'", response.text))

    # All array in one array
    quoted_values = flatten_array(quoted_values)

    # Get values if has / or \
    links = filter_paths(quoted_values)

    # Find correct links matching the regex pattern
    links = check_pattern(quoted_values, pattern)

    # Append the main URL to links that don't have the protocol (convert links to correct links)
    links = set(urljoin(main_url, link) for link in links)

    # links = [ main_url + link if not link.startswith(("http://", "https://", "//")) else "https:" + link if link.startswith("//") else link for link in links ]

    # Check Links is valid with send head request (time-consuming)
    # links = remove_links_with_errors(links)

    return links

def save_links_to_file(links, url, pattern):
    host = extract_host(url)
    pattern = generate_safe_folder_name(pattern)
    folder_path = os.path.join("data", host, pattern)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, "links.txt")

    with open(file_path, "w", encoding="utf-8") as file:
        for link in links:
            file.write(link + "\n")

def check_pattern(quoted_values, pattern):
    links = []
    for link in quoted_values:
        link = re.findall(pattern, str(link))
        if len(link) >= 1:
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
            response.raise_for_status()
            valid_links.append(link)
        except requests.exceptions.RequestException:
            pass
    return valid_links


def filter_paths(array):
    filtered_array = [item for item in array if "/" in item or "\\" in item]
    return filtered_array


def extract_host(url):
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    return host


def generate_safe_folder_name(value):
    if isinstance(value, str):
        value = value.encode("utf-8")
    safe_name = base64.b64encode(value).decode("utf-8")
    safe_name = safe_name.replace("/", "_")
    return safe_name

def collect_links(url, pattern):
    response = get_response(url)

    soup = BeautifulSoup(response.content, "html.parser")

    # Select <link> tags
    link_tags = soup.find_all("link", href=re.compile(pattern))

    # Select <script> tags
    script_tags = soup.find_all("script", src=re.compile(pattern))

    # Select <base> tags
    base_tags = soup.find_all("base", href=re.compile(pattern))

    # Select <a> tags
    a_links = soup.find_all("a", href=re.compile(pattern))

    # Select <form> tags
    form_links = soup.find_all("form", action=re.compile(pattern))

    # Select <area> tags
    area_links = soup.find_all("area", href=re.compile(pattern))

    # Select <iframe> tags
    iframe_links = soup.find_all("iframe", src=re.compile(pattern))

    # Select <img> tags
    img_links = soup.find_all("img", src=re.compile(pattern))

    # Select <audio> tags
    audio_links = soup.find_all("audio", src=re.compile(pattern))

    # Select <video> tags
    video_links = soup.find_all("video", src=re.compile(pattern))

    # Select <source> tags
    source_links = soup.find_all("source", src=re.compile(pattern))

    # Select <track> tags
    track_links = soup.find_all("track", src=re.compile(pattern))

    # Select <embed> tags
    embed_links = soup.find_all("embed", src=re.compile(pattern))

    # Combine all links
    all_links = []
    all_links.extend(link_tags)
    all_links.extend(script_tags)
    all_links.extend(base_tags)
    all_links.extend(a_links)
    all_links.extend(form_links)
    all_links.extend(area_links)
    all_links.extend(iframe_links)
    all_links.extend(img_links)
    all_links.extend(audio_links)
    all_links.extend(video_links)
    all_links.extend(source_links)
    all_links.extend(track_links)
    all_links.extend(embed_links)
    for link in all_links:
      print()
      print(link)
    # print(all_links)
    sys.exit()

    return all_links

def get_response(url):
    # Retrieve the web page content
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the web page.")
        sys.exit()
    return response


def collect_all_links(url, pattern):
    all_links = collect_links(url, pattern)
    all_links.extend(collect_links_from_quote(url, pattern))
    print(all_links)
    sys.exit()
    return all_links


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
    links = collect_all_links(args.url, args.pattern)

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
