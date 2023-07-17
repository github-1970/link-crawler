import argparse
import requests
import re
import os
import sys
import base64
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def collect_links_from_quote(url, pattern, response):
    # Extract the protocol and host from the URL
    main_url = get_main_url(url)

    # Find all value matching in the '' or ""
    quoted_values = re.findall('"(.*?)"', response.text)
    quoted_values.extend(re.findall("'(.*?)'", response.text))

    # Get values if has / or \
    links = filter_paths(quoted_values)

    # Find correct links matching the regex pattern
    links = check_pattern(quoted_values, pattern)

    # Append the main URL to links that don't have the protocol (convert links to correct links)
    links = list(set(urljoin(main_url, link) for link in links))

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


def delete_directory(url, pattern):
    host = extract_host(url)
    pattern = generate_safe_folder_name(pattern)
    folder_path = os.path.join("data", host, pattern)
    if os.path.exists(folder_path):
      shutil.rmtree(folder_path)
      return True
    else:
      return False


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


def collect_links_from_tags(url, pattern, response):
    main_url = get_main_url(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Select tags containing links
    tag_with_links = get_tag_with_links()

    # Collect links from specified tags
    links = []
    for tag in tag_with_links:
        elements = soup.find_all(tag)
        for element in elements:
            href = element.get("href")
            src = element.get("src")
            data_src = element.get("data-src")
            if href and re.match(pattern, href):
                links.append(urljoin(main_url, href))
            if src and re.match(pattern, src):
                links.append(urljoin(main_url, src))
            if data_src and re.match(pattern, data_src):
                links.append(urljoin(main_url, data_src))

    return list(set(links))


def get_tag_with_links():
    return [
        "a",
        "link",
        "script",
        "base",
        "form",
        "area",
        "iframe",
        "img",
        "audio",
        "video",
        "source",
        "track",
        "embed",
    ]


def collect_links_with_main_url(url, pattern):
    response = get_response(url)
    main_url = get_main_url(url)
    main_host = extract_host(url)
    main_host_escaped = re.escape(main_host)
    tag_with_links = get_tag_with_links()
    soup = BeautifulSoup(response.content, "html.parser")

    # "every things..." => "blog"
    links = re.findall('"(.*?)"', response.text)
    # 'every things...' => 'blog'
    links.extend(re.findall("'(.*?)'", response.text))
    # \/\/example.com...
    links.extend(re.findall("\/\/[^\s>\"'\`]+", response.text))
    # https//example.com... or http//example.com...
    links.extend(re.findall("https?:\/\/[^\s>\"'\`]+", response.text))
    # \/\/main_host_escaped...
    links.extend(re.findall("//" + main_host_escaped + "[^\s>\"'\`]+", response.text))
    # https://main_host_escaped... or http://main_host_escaped...
    links.extend(
        re.findall("https?:\/\/" + main_host_escaped + "[^\s>\"'\`]+", response.text)
    )
    links = [urljoin(main_url, link) for link in links]
    # Find correct links matching the regex pattern
    links = check_pattern(links, pattern)

    # Get links from tags
    links.extend(collect_links_from_tags(url, pattern, response))

    return list(set(links))


def get_response(url):
    # Retrieve the web page content
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the web page.")
        sys.exit()
    return response


def get_main_url(url):
    parsed_url = re.match(r"(https?://[^/]+)", url)
    if not parsed_url:
        print("Invalid URL format.")
        return []

    return parsed_url.group(1)


def collect_all_links(url, pattern):
    response = get_response(url)
    all_links = collect_links_from_tags(url, pattern, response)
    all_links.extend(collect_links_from_quote(url, pattern, response))
    return list(set(all_links))


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Website Link Collector")

    # Add the command line arguments
    parser.add_argument("-u", "--url", help="Webpage url", required=True)
    parser.add_argument("-p", "--pattern", help="Regex Pattern", required=True)
    parser.add_argument(
        "-d", "--domain", help="Include website domain for internal links", action="store_true"
    )
    parser.add_argument(
        "-c", "--clear-directory", help="Clear the directory if it already exists for this command", action="store_true"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Collect links
    print("Collecting links from the webpage...")
    if args.domain:
        links = collect_links_with_main_url(args.url, args.pattern)
    else:
        links = collect_all_links(args.url, args.pattern)

    if args.clear_directory:
      delete_directory(args.url, args.pattern)

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
