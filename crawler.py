from loguru import logger
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse, parse_qs, unquote
from typing import List


def find_xlsx_links_in_html(url: str, positions: List[int] = [2]) -> List[str]:
    """
    Given a URL, fetch the HTML and return a list of Excel file download links (absolute URLs) at the specified positions (1-based).
    Looks for links with 'javax.faces.resource=document' and 'ln=downloadResources' in the href.
    Logs how many such links were found.
    Args:
        url: The webpage URL to scan.
        positions: List of 1-based indices of artefacts to return. Default is [2] (the second match).
    Returns:
        List of URLs for the specified positions (empty if not found).
    """
    try:
        logger.info(f"Fetching HTML from {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        matches = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'javax.faces.resource=document' in href and 'ln=downloadResources' in href:
                xlsx_url = urljoin(url, href)
                matches.append(xlsx_url)
        logger.info(f"Found {len(matches)} Excel download link(s) matching the pattern.")
        selected = []
        for pos in positions:
            if 1 <= pos <= len(matches):
                logger.success(f"Selected Excel download link at position {pos}: {matches[pos-1]}")
                selected.append(matches[pos-1])
            else:
                logger.warning(f"Requested position {pos} is out of range (found {len(matches)} links).")
        return selected
    except Exception as e:
        logger.error(f"Error fetching or parsing HTML: {e}")
        return []


def download_xlsx_file(xlsx_url: str, subfolder: str = "downloads") -> str | None:
    """
    Download the .xlsx file from the given URL to the specified subfolder in the assets directory.
    Returns the local file path if successful, else None.
    """
    try:
        logger.info(f"Downloading xlsx file from {xlsx_url}")
        response = requests.get(xlsx_url, stream=True, timeout=20)
        response.raise_for_status()
        # Try to get filename from Content-Disposition header
        filename = None
        content_disp = response.headers.get('content-disposition')
        if content_disp:
            import re
            match = re.search('filename="?([^";]+)"?', content_disp)
            if match:
                filename = match.group(1)
        if not filename:
            # Fallback to URL path or query param
            parsed_url = urlparse(xlsx_url)
            filename = os.path.basename(parsed_url.path)
            if not filename or not filename.lower().endswith('.xlsx'):
                # Try to find .xlsx in query params
                from urllib.parse import parse_qs, unquote
                query_params = parse_qs(parsed_url.query)
                for values in query_params.values():
                    for v in values:
                        if v.lower().endswith('.xlsx'):
                            filename = unquote(v)
                            break
        if not filename:
            filename = 'downloaded_file.xlsx'
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets', subfolder)
        os.makedirs(assets_dir, exist_ok=True)
        file_path = os.path.join(assets_dir, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.success(f"File downloaded to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to download xlsx file: {e}")
        return None
