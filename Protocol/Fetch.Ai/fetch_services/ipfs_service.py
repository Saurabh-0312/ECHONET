import requests
import json

# You will need to get a free API token from https://web3.storage/
# and add it to your config.py file.
try:
    from config.settings import WEB3_STORAGE_TOKEN
except ImportError:
    WEB3_STORAGE_TOKEN = "YOUR_WEB3_STORAGE_API_TOKEN"



class IPFSService:
    """
    A service class to handle uploading data to decentralized storage via IPFS.
    This implementation uses the web3.storage gateway.
    """

    def __init__(self):
        self.token = WEB3_STORAGE_TOKEN
        self.upload_url = "https://api.web3.storage/upload"

    async def upload_json(self, data: dict) -> str:
        """
        Uploads a Python dictionary as a JSON file to IPFS.

        Args:
            data: The dictionary to upload.

        Returns:
            The IPFS CID (Content Identifier) string, or an error message.
        """
        if not self.token or "YOUR" in self.token:
            print("WARNING: WEB3_STORAGE_TOKEN is not configured. Cannot upload to IPFS.")
            return "ipfs_not_configured"
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # The web3.storage API expects the file content directly in the body.
        payload = json.dumps(data)
        
        try:
            # Using requests for simplicity as it's a synchronous call.
            # For a highly concurrent system, an async library like httpx would be better.
            response = requests.post(self.upload_url, headers=headers, data=payload)
            response.raise_for_status()  # This will raise an exception for HTTP errors
            result = response.json()
            cid = result.get("cid")
            if cid:
                return f"https://w3s.link/ipfs/{cid}"
            else:
                return "upload_failed_no_cid"
        except requests.exceptions.RequestException as e:
            print(f"IPFS upload failed: {e}")
            return f"upload_failed_{e}"
