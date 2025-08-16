import requests
from bs4 import BeautifulSoup
import html2text
import os


def scrape_and_save_as_mdx(url, output_dir="output_mdx"):
    """
    Scrapes the main content from a Metronome docs URL, converts it to MDX,
    and saves it to a file.
    """
    try:
        # Step 1: Fetch the HTML content of the page
        print(f"Fetching {url}...")
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Step 2: Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Step 3: Isolate the main content area
        # On docs.metronome.com, the primary article content is inside <div class="flex-1 ...">
        content_div = soup.find("div", class_="theme-doc-markdown")

        if not content_div:
            print(f"Could not find the main content div on {url}")
            return

        # Step 4: Convert the extracted HTML to Markdown
        html_converter = html2text.HTML2Text()
        html_converter.body_width = 0  # Prevents line wrapping
        markdown_content = html_converter.handle(str(content_div))

        # Step 5: Save the content to an .mdx file
        # Create a filename from the URL path
        filename = url.strip("/").split("/")[-1] + ".mdx"
        if not filename:
            filename = "index.mdx"  # For base URLs

        # Create the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"Successfully saved content to {output_path}\n")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL {url}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# --- SCRIPT STARTS HERE ---
if __name__ == "__main__":
    # URL of the documentation page you want to scrape
    # You can change this to any page on docs.metronome.com
    target_url = "https://docs.metronome.com/how-metronome-works/"

    # Scrape the single page
    scrape_and_save_as_mdx("https://docs.metronome.com/launch-guides/pay-go/")

    # To scrape multiple pages, create a list of URLs
    # all_urls = [
    #     "https://docs.metronome.com/getting-started/how-metronome-works",
    #     "https://docs.metronome.com/pricing-and-packaging/create-a-plan",
    #     "https://docs.metronome.com/set-prepaid-balance-thresholds"
    # ]
    #
    # for url in all_urls:
    #     scrape_and_save_as_mdx(url)
