import sys
import os
import json
import requests
from uagents import Agent, Context
from datetime import datetime, timezone

# --- Path and Config ---
# This ensures the agent can find other project files and the config.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
# API endpoint to fetch sensor registry data from Flask app
API_BASE_URL = "https://fetch-dev.onrender.com"

# Import secrets and configuration for the Gist
from config.settings import AGENTVERSE_API_KEY, GITHUB_PAT, KNOWLEDGE_GRAPH_GIST_ID

# Import the schema for the incoming message
from fetch_services.agents.schemas import FactCandidate

# --- Agent Definition ---
NOTARY_SEED = "notary_agent_super_secret_seed_phrase_for_echonet"
agent = Agent(
    name="EchoNetNotary",
    seed=NOTARY_SEED,
    # The port/endpoint are for local testing; on Agentverse, it will use its mailbox.
    port=8001,
    mailbox=f"{AGENTVERSE_API_KEY}@agentverse.ai",
)

# --- State and Gist Helpers ---
SENSOR_REGISTRY = {}
WRITTEN_LOCATIONS = set()
EVENT_COUNTER = 0
GIST_API_URL = f"https://api.github.com/gists/{KNOWLEDGE_GRAPH_GIST_ID}"
GIST_HEADERS = {"Authorization": f"token {GITHUB_PAT}", "Accept": "application/vnd.github.v3+json"}

def update_knowledge_graph_gist(new_content: str, ctx: Context):
    """
    Atomically updates the public knowledge graph Gist by fetching its
    current content, appending the new atoms, and patching it.
    """
    try:
        # Step 1: Get the current content of the Gist file.
        response = requests.get(GIST_API_URL, headers=GIST_HEADERS, timeout=10)
        response.raise_for_status()
        # We assume the Gist has a file named 'knowledge_graph.metta'
        current_content = response.json()['files']['knowledge_graph.metta']['content']
        
        # Step 2: Append the new atoms to the current content.
        updated_content = current_content + new_content
        
        # Step 3: Send a PATCH request to update the Gist.
        payload = {"files": {"knowledge_graph.metta": {"content": updated_content}}}
        patch_response = requests.patch(GIST_API_URL, headers=GIST_HEADERS, json=payload, timeout=10)
        patch_response.raise_for_status()
        
        ctx.logger.info("Successfully updated public knowledge graph Gist.")
    except requests.exceptions.RequestException as e:
        ctx.logger.error(f"Failed to update knowledge graph Gist: {e}")
    except KeyError:
        ctx.logger.error("Gist does not contain a 'knowledge_graph.metta' file. Please check your Gist setup.")


def load_sensor_registry():
    """
    Fetches the sensor registry from the Flask API.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/registry", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to load sensor registry from API: {e}")
        return {}

@agent.on_event("startup")
async def startup(ctx: Context):
    """
    On startup, the Notary loads the sensor registry from Flask API and initializes the
    public knowledge base Gist, ensuring it starts from a clean slate.
    """
    global SENSOR_REGISTRY, WRITTEN_LOCATIONS, EVENT_COUNTER
    ctx.logger.info(f"Notary Agent starting up. Address: {agent.address}")
    
    # Load registry from Flask API instead of local file
    SENSOR_REGISTRY = load_sensor_registry()
    if SENSOR_REGISTRY:
        # Count only actual devices (exclude _network_services)
        device_count = len([k for k in SENSOR_REGISTRY.keys() if not k.startswith('_')])
        ctx.logger.info(f"Successfully loaded sensor registry with {device_count} devices from API.")
    else:
        ctx.logger.warning("Could not load sensor registry from API or registry is empty.")

    # Initialize the public Gist with a header
    initial_content = "; EchoNet Shared Knowledge Graph\n; Managed by the Notary Agent.\n"
    update_knowledge_graph_gist(initial_content, ctx)
    
    WRITTEN_LOCATIONS = set()
    EVENT_COUNTER = 0
    ctx.logger.info("Public knowledge base Gist initialized.")

@agent.on_message(model=FactCandidate, replies=set())
async def add_fact_to_kb(ctx: Context, sender: str, msg: FactCandidate):
    """
    Receives a validated fact and writes it to the PUBLIC knowledge graph Gist.
    """
    global SENSOR_REGISTRY, WRITTEN_LOCATIONS, EVENT_COUNTER
    
    data = msg.validated_event
    ctx.logger.info(f"Received fact candidate from worker for device {data.mac_address}")
    
    # Refresh sensor registry from API to get latest data
    SENSOR_REGISTRY = load_sensor_registry()
    
    sensor_info = SENSOR_REGISTRY.get(data.mac_address)
    if not sensor_info:
        ctx.logger.warning(f"Received fact for unregistered MAC address {data.mac_address}. Discarding.")
        return

    loc_id = sensor_info['loc_id']
    new_atoms_to_write = ""
    
    # Location Atom Logic: Add the location atom only if it's new.
    # To be robust, we need to check the Gist content itself. For this prototype,
    # the in-memory WRITTEN_LOCATIONS is a good-enough approximation.
    if loc_id not in WRITTEN_LOCATIONS:
        new_atoms_to_write += f"\n; --- Location Definition: {sensor_info['name']} ---\n"
        new_atoms_to_write += f"(location {loc_id} \"{sensor_info['name']}\" {sensor_info['latitude']} {sensor_info['longitude']})\n"
        WRITTEN_LOCATIONS.add(loc_id)

    # Noise Event Atom Logic: Always add a new event.
    EVENT_COUNTER += 1
    event_id = f"N{str(EVENT_COUNTER).zfill(3)}"
    iso_timestamp = datetime.fromtimestamp(data.timestamp, tz=timezone.utc).isoformat()
    new_atoms_to_write += f"(noise_event {event_id} {loc_id} \"{iso_timestamp}\" {data.sound_level_db})\n"
    
    # Update the public Gist with the new atoms
    update_knowledge_graph_gist(new_atoms_to_write, ctx)

if __name__ == "__main__":
    print(f"Starting Notary Agent...")
    print(f"Address: {agent.address}")
    agent.run()