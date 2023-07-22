# Link Crawler

This script allows you to crawl a website and collect links from its webpages based on a specified regex pattern. It can be useful for extracting links from websites for various purposes such as data scraping or analysis.

## Prerequisites

Before running the script, make sure you have the following installed:

- Python 3.x
- `argparse` library
- `requests` library
- `re` module
- `os` module
- `sys` module
- `base64` module
- `urllib.parse` module
- `bs4` (BeautifulSoup) library
- `shutil` module

You can install the required dependencies using `pip`:

```shell
pip install argparse requests bs4
```

## Usage

To use the script, follow these steps:

1. Clone or download the script file to your local machine.
2. Open a terminal or command prompt.
3. Navigate to the directory where the script is located.
4. Run the following command:

   ```shell
   python link_crawler.py -u <url> -p <pattern> [-d] [-c]
   ```

   Replace `<url>` with the URL of the website you want to crawl, and `<pattern>` with the regex pattern to match the links.

   Optional flags:
   - `-d` or `--domain`: Include the website domain for internal links. By default, it deletes the domain name from internal links and then searches for the pattern.
   - `-c` or `--clear-directory`: Clear the directory if it already exists for this command. By default, if the command is entered with a duplicate pattern and domain, the search is not performed.

5. The script will start crawling the website, collecting links from its webpages, and display the results.

   - If links matching the regex pattern are found, the script will save them to a `links.txt` file in the corresponding directory.
   - If no links are found, the script will display a message accordingly.

Note: The script crawls webpages within the specified website by following links found in HTML tags such as `<a>`, `<link>`, `<script>`, `<base>`, `<form>`, and more (in all tags that contain links). It searches for `href`, `src`, and `data-src` attributes in these tags to extract the links.

Note: this script finds any link anywhere on the webpage, even outside of the attributes of the tags.

## Examples

Here are a few examples of how you can use the script:

- Crawl a website and collect all links from its webpages:

  ```shell
  python link_crawler.py -u https://example.com -p ".*"
  ```

  This will crawl the `example.com` website, collect all links from its webpages, and save them to `links.txt` in the `data/<host>/<pattern>/` directory.

- Crawl a website and collect only specific links matching a pattern:

  ```shell
  python link_crawler.py -u https://example.com -p "https://example.com/downloads/.*"
  ```

  This will crawl the `example.com` website and collect only the links that match the pattern `https://example.com/downloads/`.

- Crawl a website and putting domains in internal links:

  ```shell
  python link_crawler.py -u https://example.com -p ".*" -d
  ```

  This will crawl the `example.com` website, collect all links from its webpage, putting domains in internal links, and save them to `links.txt`.

- Clear the directory and crawl the website to collect fresh links:

  ```shell
  python link_crawler.py -u https://example.com -p ".*" -c
  ```

  This will clear the existing directory (if any) for the specified command and crawl the `example.com` website to collect fresh links.

## License

This script is licensed under the [MIT License](LICENSE). Feel free to modify and use it according to your needs.
