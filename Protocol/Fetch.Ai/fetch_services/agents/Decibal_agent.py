import sys
import os
import re
import requests
from datetime import datetime, time
from uuid import uuid4
from uagents import Agent, Context
from openai import AsyncOpenAI
from rapidfuzz import process, fuzz
from uagents.setup import fund_agent_if_low

# Official Chat Protocol from uagents_core
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)

# --- Path and Config ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from config.settings import ASI_API_KEY, KNOWLEDGE_GRAPH_GIST_ID, AGENTVERSE_API_KEY

# --- ASI:One API Client ---
if not ASI_API_KEY or "YOUR" in ASI_API_KEY:
    print("WARNING: ASI_API_KEY not found. LLM functionality will be disabled.")
    asi_client = None
else:
    asi_client = AsyncOpenAI(api_key=ASI_API_KEY, base_url="https://api.asi1.ai/v1")

# --- Agent Definition ---
DECIBAL_AGENT_SEED = "decibal_agent_super_secret_seed_phrase"
agent = Agent(
    name="Decibal_Agent",
    seed=DECIBAL_AGENT_SEED,
    mailbox=f"{AGENTVERSE_API_KEY}@agentverse.ai",
    #endpoint=["https://echonet-decibal-agent.onrender.com"],
    publish_agent_details=True,
)

fund_agent_if_low(agent.wallet.address())

# --- Knowledge Base Logic ---
KNOWLEDGE_GRAPH_RAW_URL = f"https://gist.githubusercontent.com/raw/{KNOWLEDGE_GRAPH_GIST_ID}/knowledge_graph.metta"
LOCATIONS_CACHE = {}
EVENTS_CACHE = []

def load_knowledge_base():
    global LOCATIONS_CACHE, EVENTS_CACHE
    print(f"Loading knowledge base from Gist: {KNOWLEDGE_GRAPH_RAW_URL}")
    try:
        response = requests.get(KNOWLEDGE_GRAPH_RAW_URL, timeout=10)
        response.raise_for_status()
        content = response.text
        
        locations = {}
        events = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith(";"):
                continue

            loc_match = re.match(r'\(location (\S+) "(.*)" ([\d\.\-]+) ([\d\.\-]+)\)', line)
            if loc_match:
                loc_id, name, lat, lon = loc_match.groups()
                locations[loc_id] = {"name": name, "lat": float(lat), "lon": float(lon)}

            event_match = re.match(r'\(noise_event (\S+) (\S+) "([^"]+)" (\d+\.?\d*)\)', line)
            if event_match:
                _, loc_id, timestamp, db = event_match.groups()
                events.append({"loc_id": loc_id, "timestamp": timestamp, "db": float(db)})

        LOCATIONS_CACHE = locations
        EVENTS_CACHE = events
        print(f"Loaded {len(LOCATIONS_CACHE)} locations and {len(EVENTS_CACHE)} events.")
    except Exception as e:
        print(f"ERROR: Could not load knowledge base: {e}")

def get_average_db(events, loc_id, night_only=False):
    vals = []
    for ev in events:
        if ev["loc_id"] != loc_id:
            continue
        if night_only:
            try:
                t = datetime.fromisoformat(ev["timestamp"].rstrip('Z')).time()
                if not (time(22, 0) <= t or t < time(6, 0)):
                    continue
            except ValueError:
                continue
        vals.append(ev["db"])
    return sum(vals)/len(vals) if vals else None

def generate_facts_summary(events, locations):
    lines = ["Facts from the sound-sensor network:"]
    if not locations:
        return "No data available."
    for loc_id, loc_data in locations.items():
        avg_all = get_average_db(events, loc_id)
        avg_night = get_average_db(events, loc_id, night_only=True)
        avg_all_str = f"{avg_all:.1f} dB" if avg_all is not None else "No data"
        avg_night_str = f"{avg_night:.1f} dB" if avg_night is not None else "No data"
        lines.append(f"- Location '{loc_data['name']}' (ID: {loc_id}): overall {avg_all_str}, night {avg_night_str}.")
    return "\n".join(lines)

async def query_llm_with_rag(user_query: str) -> str:
    if not asi_client:
        return "ASI:One LLM not configured. Set the API key."

    facts = generate_facts_summary(EVENTS_CACHE, LOCATIONS_CACHE)
    prompt = (
        f"You are EchoNet Decibal Manager AI. Answer based ONLY on the facts below. "
        f"If insufficient, say you cannot answer.\n\n"
        f"--- FACTS ---\n{facts}\n\n"
        f"--- USER QUERY ---\n{user_query}\n\n--- ANSWER ---\n"
    )
    try:
        response = await asi_client.chat.completions.create(
            model="asi1-extended",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error querying LLM: {e}"

# --- Agent Event Logic ---
@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Fleet Manager started. Address: {agent.address}")
    load_knowledge_base()

@agent.on_interval(period=30.0)
async def sync_knowledge_base(ctx: Context):
    ctx.logger.info("Syncing knowledge base...")
    load_knowledge_base()

# --- Chat Message Handling (locked protocol) ---
@agent.on_message(model=ChatMessage, replies={ChatAcknowledgement, ChatMessage})
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    # Acknowledge
    await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id))
    
    # Extract text
    text = "".join([item.text for item in msg.content if isinstance(item, TextContent)])
    ctx.logger.info(f"Received query from {sender}: {text}")
    
    # Generate answer
    answer = await query_llm_with_rag(text)
    
    # Send answer + end session
    await ctx.send(
        sender,
        ChatMessage(
            timestamp=datetime.utcnow(),
            msg_id=str(uuid4()),
            content=[
                TextContent(type="text", text=answer),
                EndSessionContent(type="end-session")
            ]
        )
    )

# --- Main Execution ---
if __name__ == "__main__":
    agent.run()
