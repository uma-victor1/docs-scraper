import requests
from bs4 import BeautifulSoup
import html2text
import os
from urllib.parse import urljoin, urlparse


def download_images_and_update_md(
    base_url, soup_content, output_dir, relative_images_dir="images"
):
    """
    Finds all images, downloads them, and returns the HTML content
    with updated local paths for the images.
    """
    # Create the full path for the image directory
    full_images_dir = os.path.join(output_dir, relative_images_dir)
    if not os.path.exists(full_images_dir):
        os.makedirs(full_images_dir)

    img_tags = soup_content.find_all("img")
    print(f"Found {len(img_tags)} images to download.")

    for img_tag in img_tags:
        # Get the original image source URL
        original_src = img_tag.get("src")
        if not original_src:
            continue

        # Construct the absolute URL for the image
        # This handles both relative (/path/to/img.png) and absolute URLs
        absolute_img_url = urljoin(base_url, original_src)

        # Get a clean filename from the URL
        img_filename = os.path.basename(urlparse(absolute_img_url).path)
        local_img_path = os.path.join(full_images_dir, img_filename)

        try:
            # Download the image
            img_response = requests.get(absolute_img_url, stream=True)
            img_response.raise_for_status()

            with open(local_img_path, "wb") as f:
                for chunk in img_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded {img_filename}")

            # IMPORTANT: Update the src in the HTML to the new local path
            # This ensures the final MDX file points to your local images
            new_src_path = os.path.join(relative_images_dir, img_filename).replace(
                "\\", "/"
            )
            img_tag["src"] = new_src_path

        except requests.exceptions.RequestException as e:
            print(f"Could not download {absolute_img_url}: {e}")

    return soup_content


def scrape_and_save_as_mdx(url, output_dir="output_mdx"):
    """
    Scrapes content, downloads images, and saves a clean MDX file.
    """
    try:
        print(f"Fetching {url}...")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Isolate the main content area
        content_div = soup.find("div", class_="theme-doc-markdown")
        if not content_div:
            print(f"Could not find the main content div on {url}")
            return

        # --- NEW: Download images and get updated HTML ---
        updated_content_div = download_images_and_update_md(
            url, content_div, output_dir
        )

        # Convert the MODIFIED HTML (with local image paths) to Markdown
        html_converter = html2text.HTML2Text()
        html_converter.body_width = 0
        markdown_content = html_converter.handle(str(updated_content_div))

        # Save the content to an .mdx file
        filename = url.strip("/").split("/")[-1] + ".mdx"
        if not filename:
            filename = "index.mdx"

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
    target_url = (
        "https://docs.metronome.com/invoice-customers/solutions/invoice-other-systems/"
    )
    scrape_and_save_as_mdx(target_url)
