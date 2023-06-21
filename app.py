# Import the required dependencies
import os
from dotenv import load_dotenv

from custom_confluence_loader import CustomConfluenceLoader

# Load environment variables from .env file
load_dotenv()

#Get specific environment variables
sitename = os.getenv("ATLASSIAN_SITENAME")
username = os.getenv('ATLASSIAN_USERNAME')
api_key = os.getenv('ATLASSIAN_API_KEY')
space_key = os.getenv('ATLASSIAN_SPACE_KEY')

# Create a CustomConfluenceLoader instance
loader = CustomConfluenceLoader(
    url = f'https://{sitename}.atlassian.net/wiki',
    username = username,
    api_key = api_key
)

# Load documents from Confluence
documents = loader.load(space_key=space_key, include_attachments=False, limit=50, max_pages=10)

for document in documents:
    print(f"Document: {document.metadata}")

print(f"Found {len(documents)} documents")

# Last document page content
# print(f"Document: {documents[2].page_content}")
print(f"Version: {documents[2].metadata['version']}")




