import requests

class DocumentUploader:
    def __init__(self, api_key, backend_url):
        self.api_key = api_key
        self.backend_url = backend_url

    def upload_file(self, filename):
        url = f"{self.backend_url}/upload"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        file_path = f"./{filename}"

        with open(file_path, "rb") as f:
            files = {
                "file": (filename, f)
            }

            response = requests.post(url, headers=headers, files=files)
            return response.json()
