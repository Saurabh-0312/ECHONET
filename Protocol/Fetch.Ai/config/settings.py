import os
from dotenv import load_dotenv

# --- Locate project root ---
# This assumes the 'config' folder is in the project's root directory.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(PROJECT_ROOT, ".env")

# --- Load variables from .env at project root ---
# This line reads the .env file and makes the variables available to your application.
load_dotenv(dotenv_path)

# --- Sensitive configs loaded from .env ---
WEB3_STORAGE_TOKEN = os.getenv("WEB3_STORAGE_TOKEN")
ETHEREUM_NODE_URL = os.getenv("ETHEREUM_NODE_URL")
ECHONET_STAKING_CONTRACT_ADDRESS = os.getenv("ECHONET_STAKING_CONTRACT_ADDRESS")
CONTRACT_OWNER_PRIVATE_KEY = os.getenv("CONTRACT_OWNER_PRIVATE_KEY")

GITHUB_PAT=os.getenv("GITHUB_PAT")
KNOWLEDGE_GRAPH_GIST_ID=os.getenv("KNOWLEDGE_GRAPH_GIST_ID")
ASI_API_KEY = os.getenv("ASI_API_KEY")
AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY")



# --- Debug check (optional but recommended) ---
if not CONTRACT_OWNER_PRIVATE_KEY:
    print("⚠️ WARNING: CONTRACT_OWNER_PRIVATE_KEY is missing or empty in your .env file!")



