# Import the required dependencies
import os
from dotenv import load_dotenv

from langchain.document_loaders import ConfluenceLoader, ContentFormat
from document_uploader import DocumentUploader

# Load environment variables from .env file
load_dotenv()

#Get specific environment variables
sitename = os.getenv("ATLASSIAN_SITENAME")
username = os.getenv('ATLASSIAN_USERNAME')
api_key = os.getenv('ATLASSIAN_API_KEY')
space_key = os.getenv('ATLASSIAN_SPACE_KEY')
quivr_api_key = os.getenv('QUIVR_API_KEY')
url = os.getenv('QUIVR_BACKEND_URL')

# Create a ConfluenceLoader instance
loader = ConfluenceLoader(
    url = f'https://{sitename}.atlassian.net/wiki',
    username = username,
    api_key = api_key
)

# Load documents from Confluence
documents = loader.load(space_key=space_key, include_attachments=False, content_format=ContentFormat.STORAGE_VERSION, limit=50, max_pages=10)

for document in documents:
    print(f"Document: {document.metadata}")

print(f"Found {len(documents)} documents")

# Print page content
print('============================================================')
print(f"Source: {documents[2].metadata['source']}")
print(f"Version: {documents[2].metadata['version']}")
print(f"Document: {documents[2].page_content}")

# uploader = DocumentUploader(quivr_api_key, url)
# response = uploader.upload_file("sample.txt")
# print(response)
