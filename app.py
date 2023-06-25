""" The script containing the entry point for the application. """
import os
from dotenv import load_dotenv
from confluence_extractor import ConfluenceExtractor, ConfluenceConfiguration

# Load environment variables from .env file
load_dotenv()

def main():
    """ The main entry point for the confluence_extractor application. """

    #Get specific environment variables
    sitename = os.getenv("ATLASSIAN_SITENAME")
    username = os.getenv('ATLASSIAN_USERNAME')
    api_key = os.getenv('ATLASSIAN_API_KEY')
    space_key = os.getenv('ATLASSIAN_SPACE_KEY')
    download_folder_base = os.getenv('CONFLUENCE_CONTENT_FOLDER')

    # Location for storing extracted Confluence content for confluence space
    confluence_download_location = download_folder_base + '-' + space_key
    if not os.path.exists(confluence_download_location):
        os.makedirs(confluence_download_location)

    # Create a ConfluenceConfiguration object
    confluence_config = ConfluenceConfiguration(sitename, username, api_key, space_key)

    extractor = ConfluenceExtractor(
        confluence_config,
        confluence_download_location,
    )
    # Example of extracting a single page by id
    # extractor.process_page({'id': 'PAGE_ID', 'title': ''}, include_attachments=True)

    # Extract all pages from the confluence space
    extractor.extract_all_pages(include_attachments=True, max_pages=2000)

# Execute the following code only if the script is run directly, not imported.
if __name__ == '__main__':
    main()
