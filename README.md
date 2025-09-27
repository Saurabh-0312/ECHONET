# ECHONET 🌍

**A comprehensive decentralized environmental monitoring ecosystem** that combines IoT sensors, multi-blockchain protocols, AI/ML services, and distributed computing to create a transparent, incentivized network for environmental data collection, verification, and analysis.

ECHONET leverages cutting-edge technologies including **Fetch.AI** autonomous agents for consensus validation, **Polygon** smart contracts for tokenomics, **IPFS/Filecoin** for decentralized storage, and real-time **MQTT** communication for sensor networks.

![ECHONET Dashboard](https://github.com/user-attachments/assets/a0d0b6fd-a7f3-46ff-ab49-4af2b887b095)

## 🚀 Key Features

### 🌍 Environmental Monitoring
- **IoT Sensor Network**: Distributed audio sensors with real-time decibel monitoring
- **Real-time Data Streaming**: MQTT-based sensor communication + FastAPI SSE streams
- **Geographic Validation**: Location-based consensus using GPS coordinates
- **Peer-to-Peer Verification**: Fetch.AI autonomous agents validate sensor data authenticity
- **Audio Processing**: Real-time RMS/dB calculation with CSV logging and ASCII visualization

### ⛓️ Multi-Blockchain Architecture  
- **Polygon Smart Contracts**: EVM-compatible contracts for tokenomics and staking
- **Fetch.AI Agent Network**: Autonomous consensus validation with cryptographic signatures
- **IPFS/Filecoin Storage**: Decentralized data storage with CID-based retrieval
- **MQTT Broker Integration**: HiveMQ for real-time sensor communication
- **Cross-chain Data Flow**: Seamless data pipeline from sensors to blockchain

### 🔐 Identity & Security
- **WorldCoin Verification**: Human-proof identity system integration
- **ENS Support**: Ethereum Name Service for user-friendly addresses  
- **Wallet Integration**: MetaMask and Web3 wallet compatibility
- **Cryptographic Verification**: End-to-end data integrity and authenticity

### 💰 Token Economy
- **ECHO Token**: Native utility token for rewards and staking
- **Staking Mechanisms**: Sensor operators stake tokens for network participation
- **Automated Rewards**: Smart contract-based incentive distribution
- **DePIN Marketplace**: Trade and manage decentralized sensor devices

### 🎨 Modern User Experience
- **React 19 Frontend**: Latest React features with server components
- **3D Visualizations**: Three.js-powered environmental data visualization  
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Real-time Updates**: Live dashboard with animated charts and metrics

### 🚀 Deployment & Operations

#### Docker Containerization
```bash
# Full stack deployment
docker-compose up -d

# Scale services
docker-compose up --scale backend=3 --scale python-service=2

# Health monitoring
./monitor_echonet.sh
```

#### Fluence Cloud Deployment
```bash
cd Deployment-Fluence/
terraform init
terraform apply
# Deploys to decentralized Fluence network
```

#### Development Workflow
- **Hot Reloading**: Vite for instant frontend updates
- **API Documentation**: FastAPI auto-generated docs at `/docs`
- **Testing Suite**: Foundry for smart contract testing
- **Monitoring**: Built-in health checks and logging

#### Production Features
- **Load Balancing**: Nginx reverse proxy configuration
- **SSL/TLS**: Automatic HTTPS with Let's Encrypt
- **Auto-scaling**: Kubernetes-ready container orchestration
- **Monitoring**: Grafana dashboards and alerting systems for tokenomics, **Fetch.AI** autonomous agents for data validation, **Filecoin** for decentralized storage, and a modern **React** frontend with real-time analytics.

![WhatsApp Image 2025-09-27 at 16 08 47](https://github.com/user-attachments/assets/a0d0b6fd-a7f3-46ff-ab49-4af2b887b095)

## 🛠️ Technology Stack

### Frontend & UI
- **React 19** - Modern UI library with latest features
- **Vite** - Fast build tool and development server  
- **Tailwind CSS 4** - Utility-first CSS framework
- **Three.js** - 3D graphics and visualizations
- **Framer Motion** - Advanced animations
- **Ethers.js 6** - Ethereum blockchain interactions
- **Leaflet** - Interactive maps for sensor locations
- **Recharts** - Data visualization and analytics charts

### Backend & APIs
- **Node.js** - Server-side JavaScript runtime
- **Express.js 5** - Web framework for APIs
- **Filoz Synapse SDK** - Filecoin integration
- **GraphProtocol GRC-20** - The Graph protocol support  
- **ENS.js** - Ethereum Name Service resolution
- **WorldCoin IDKit** - Identity verification
- **Viem** - Ethereum client utilities

### Blockchain & Protocols
- **Polygon** - EVM-compatible blockchain for smart contracts
- **Fetch.AI** - Autonomous agent network for data validation
- **Filecoin** - Decentralized storage network via IPFS
- **Ethereum** - ENS resolution and cross-chain compatibility
- **Foundry** - Smart contract development and testing

### Hardware & IoT
- **Python 3.x** - IoT sensor programming and real-time audio processing
- **SoundDevice & NumPy** - Real-time audio capture and RMS/dB calculation
- **FastAPI** - High-performance async web framework for sensor APIs
- **MQTT (Paho)** - Message queuing for sensor network communication
- **GetMac** - Automatic MAC address detection for device identification
- **Fetch.AI uAgents** - Autonomous agent framework for consensus protocols
- **Rust** - High-performance kernel monitoring (Raspberry Pi)

### Infrastructure & DevOps
- **Fluence Network** - Decentralized serverless computing
- **Docker & Docker Compose** - Containerization and orchestration
- **Terraform** - Infrastructure as Code for Fluence deployment
- **Nginx** - Reverse proxy and web server
- **GitHub Actions** - CI/CD pipelines

## Architecture Overview

ECHONET leverages a distributed microservice architecture deployed on **Fluence Network** - a decentralized computing platform that provides serverless, peer-to-peer infrastructure for our environmental monitoring services.

### 🏗️ Microservice Architecture on Fluence

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUENCE NETWORK                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              ECHONET Services                       │    │
│  │                                                     │    │
│  │  ├── Sensor Data Aggregation Service               │    │
│  │  ├── ENS Resolution Service                         │    │
│  │  ├── WorldCoin Identity Verification Service       │    │
│  │  ├── Staking & Rewards Service                     │    │
│  │  ├── IPFS/Filecoin Storage Service (CID)          │    │
│  │  ├── HyperGraph Analytics Service                  │    │
│  │  └── Python Heatmap Service                        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
            ↕️ P2P Communication & Service Discovery
┌─────────────────────────────────────────────────────────────┐
│                 Multi-Protocol Layer                        │
│  ├── Fetch.AI     # Autonomous agent services              │
│  ├── FileCoin     # Decentralized storage protocols        │
│  └── Polygon      # Smart contract execution               │
└─────────────────────────────────────────────────────────────┘
            ↕️ Blockchain & Storage Interactions
┌─────────────────────────────────────────────────────────────┐
│              Hardware & Frontend Layer                      │
│  ├── IoT Sensors  # Environmental data collection          │
│  └── Web Frontend # React-based user interface             │
└─────────────────────────────────────────────────────────────┘
```

### 📁 Project Structure

```
├── Frontend/                    # 🎨 React 19 + Vite Frontend Application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/             # Application pages and routes  
│   │   ├── context/           # React Context providers (Auth, EchoNet, Data)
│   │   ├── hooks/             # Custom React hooks (device registration, etc.)
│   │   ├── ABI/               # Smart contract ABIs (EchoNet Token, Exchange)
│   │   └── assets/            # Static assets (images, videos, icons)
│   ├── components.json         # shadcn/ui components configuration
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   ├── Dockerfile             # Frontend containerization
│   └── docker-compose.yml     # Frontend service configuration
│
├── Server/                      # 🚀 Node.js Express API Gateway
│   ├── routes/                 # RESTful API endpoints
│   │   ├── sensorRoutes.js     # IoT sensor data management
│   │   ├── ensRoutes.js        # Ethereum Name Service resolution
│   │   ├── wordCoinRoutes.js   # WorldCoin identity verification
│   │   ├── stakeDataRoutes.js  # Token staking and rewards
│   │   ├── CidRoutes.js        # IPFS/Filecoin content addressing
│   │   └── hyperGraphSensor.js # The Graph protocol analytics
│   ├── controller/             # Business logic controllers
│   ├── ABI/                   # Smart contract interfaces
│   ├── Dockerfile             # Backend containerization
│   └── nginx.conf             # Reverse proxy configuration
│
├── Python-microservice/         # 🐍 FastAPI Analytics Service
│   ├── index.py               # FastAPI app for heatmap generation
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Python service containerization
│
├── Hardware/                    # 🔧 IoT Sensor Infrastructure
│   ├── combined.py            # Audio monitoring + FastAPI streaming
│   ├── sound-input.py         # Audio sensor processing utilities
│   ├── stream.py              # Real-time data streaming
│   ├── requirements.txt       # Python ML/IoT dependencies
│   └── kernel_monitoring/     # Rust-based system monitoring
│       ├── Cargo.toml         # Rust project configuration
│       ├── src/               # Rust monitoring code
│       └── RASPBERRY_PI_SETUP.md # Hardware setup guide
│
├── Protocol/                    # ⛓️ Multi-Blockchain Integration
│   ├── Pi_fetch_config/       # 🎯 **MAIN SENSOR NODE IMPLEMENTATION**
│   │   ├── super_combined.py  # **Complete device node with all features**
│   │   ├── device_node.py     # Fetch.AI agent + MQTT + consensus logic
│   │   ├── combined.py        # Audio monitoring + FastAPI streaming
│   │   └── requirements.txt   # All sensor node dependencies
│   ├── Polygon/               # Ethereum-compatible smart contracts
│   │   ├── src/               # Solidity contracts (EchoNetToken, MainContract)
│   │   ├── script/            # Foundry deployment scripts
│   │   ├── test/              # Smart contract tests
│   │   └── foundry.toml       # Foundry configuration
│   ├── Fetch.AI/              # Autonomous agent network
│   │   ├── fetch_services/    # Agent definitions and protocols
│   │   ├── backend/           # Flask API for agent coordination
│   │   ├── config/            # Environment and settings
│   │   └── requirements.txt   # Python agent dependencies
│   ├── FileCoin/              # Decentralized storage integration
│   │   ├── app.js             # Synapse SDK integration
│   │   ├── Routes/            # Storage API endpoints
│   │   └── Controller/        # Storage business logic
│   └── SubGraph/              # The Graph protocol indexing
│
├── Deployment-Fluence/          # ☁️ Infrastructure as Code
│   ├── main.tf               # Terraform Fluence service definitions
│   ├── variables.tf          # Infrastructure variables
│   ├── outputs.tf            # Deployment outputs
│   ├── terraform.tfvars      # Environment-specific values
│   └── fluence-service.json  # Fluence service configuration
│
├── depin-marketplace/           # 🛒 DePIN Device Marketplace
│   ├── server.js             # Express marketplace API
│   ├── client.js             # Client SDK for device trading
│   ├── test-minimal.js       # Marketplace integration tests
│   └── Dockerfile            # Marketplace containerization
│
├── docker-compose.yml          # 🐳 Multi-service orchestration
├── monitor_echonet.sh         # 📊 System monitoring and health checks
└── package.json              # Root project dependencies
```

## 🚀 Getting Started

### Prerequisites

Before running ECHONET, ensure you have the following installed:

- **Node.js** (v18 or higher) and **npm**
- **Docker** and **Docker Compose**
- **Python 3.8+** with **pip**
- **Git** for cloning the repository
- **MetaMask** or compatible Web3 wallet
- **Audio Input Device** (USB microphone or system audio)
- **Fetch.AI AgentVerse Account** for agent mailbox configuration

### Quick Start with Docker

The fastest way to run ECHONET is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/Saurabh-0312/ECHONET.git
cd ECHONET

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:80
# Backend API: http://localhost:3001
# Python Service: http://localhost:8000
```

### Manual Development Setup

For development with hot reloading:

```bash
# 1. Setup Frontend
cd Frontend
npm install
npm run dev  # Runs on http://localhost:5173

# 2. Setup Backend (new terminal)
cd ../Server
npm install
npm start  # Runs on http://localhost:3001

# 3. Setup Python Microservice (new terminal)  
cd ../Python-microservice
pip install -r requirements.txt
uvicorn index:app --reload --port 8000

# 4. Setup Sensor Node (new terminal) - MAIN COMPONENT
cd ../Protocol/Pi_fetch_config
pip install -r requirements.txt

# Option A: Run complete sensor node with all features
python super_combined.py

# Option B: Run individual components
python combined.py      # Audio monitoring only
python device_node.py   # Agent consensus only
```

### 🎯 Super Combined Sensor Node

The `super_combined.py` script is the **complete sensor node implementation** that includes:

- **🎤 Real-time Audio Processing**: Captures audio, calculates dB levels
- **📡 MQTT Communication**: Publishes data every 2 seconds to HiveMQ broker
- **🤖 Fetch.AI Agent Network**: Autonomous consensus validation with peer verification
- **🌐 FastAPI Web Interface**: Real-time streaming API and status endpoints
- **🔗 API Integration**: Sends validated data to external collectors
- **💾 Local Logging**: CSV file logging with timestamps

```bash
# Run the complete sensor node
cd Protocol/Pi_fetch_config
python super_combined.py [optional_mac_address]

# Outputs:
# 🎤 Audio processing started...
# 📡 MQTT Publisher connected successfully
# 🌐 FastAPI server on http://0.0.0.0:5007
# 🤖 Agent running with consensus validation
```

### Environment Configuration

Create `.env` files in the respective directories:

**Frontend/.env:**
```bash
VITE_TOKEN_CONTRACT_ADDRESS=your_token_contract_address
VITE_MAIN_CONTRACT_ADDRESS=your_main_contract_address
VITE_BACKEND_URL=http://localhost:3001
```

**Server/.env:**
```bash
PROVIDER_PRIVATE_KEY=your_private_key
ETHEREUM_NODE_URL=your_rpc_url
PORT=3001
```

**Protocol/Pi_fetch_config Configuration:**

Edit the hardcoded configuration section in `super_combined.py`:

```python
# ======================================================================================
# --- HARDCODED CONFIGURATION ---
# ❗️ EDIT THE VALUES IN THIS SECTION ❗️
# ======================================================================================

# 1. Your central Flask server API
API_BASE_URL = "https://fetch-dev.onrender.com"

# 2. Your Agentverse API Key from https://agentverse.ai
AGENTVERSE_API_KEY = "your_agentverse_api_key_here"

# 3. External data ingestion API
EXTERNAL_INGEST_API_URL = "http://82.177.167.151:5001/ingest"

# 4. Raw data collector API
RAW_DATA_COLLECTOR_URL = "http://82.177.167.151:3001/api/sensor"

# 5. MQTT Broker (usually no change needed)
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

# 6. Audio settings (adjust for your microphone)
SAMPLERATE = 48000
BLOCKSIZE = 1024
CHANNELS = 1

# 7. FastAPI settings
FASTAPI_HOST = "0.0.0.0"
FASTAPI_PORT = 5007
```

### Smart Contract Deployment

Deploy contracts using Foundry:

```bash
cd Protocol/Polygon

# Install dependencies
forge install

# Compile contracts
forge build

# Deploy to testnet
forge script script/Script.s.sol --rpc-url $RPC_URL --private-key $PRIVATE_KEY --broadcast

# Verify contracts (optional)
forge verify-contract <contract_address> src/EchoNetToken.sol:EchoNetToken --etherscan-api-key $ETHERSCAN_API_KEY
```

### Monitoring and Health Checks

Use the included monitoring script:

```bash
# Make executable and run
chmod +x monitor_echonet.sh
./monitor_echonet.sh

# Check container status
docker ps
docker-compose ps

# View service logs
docker-compose logs frontend
docker-compose logs backend
docker-compose logs python-service
```

## � Sensor Node Architecture

**ECHONET's core innovation is the distributed sensor node network** powered by Fetch.AI autonomous agents:

### 🤖 Fetch.AI Agent Consensus System

- **Peer-to-Peer Validation**: Agents validate each other's sensor data using proximity algorithms
- **Geographic Grid System**: Location-based grouping for efficient consensus (0.1° grid squares)
- **Smart Consensus Logic**: Haversine distance + sound attenuation calculations
- **Cryptographic Signatures**: Ed25519 signatures for tamper-proof validation
- **Failure Handling**: Automatic stake slashing for sensors that consistently fail validation

### 📡 Real-time Communication Pipeline

```
🎤 Audio Input → 🔢 dB Processing → 📦 MQTT Queue → 🌐 Network Broadcast
                                         ↓
🤖 Agent Validation ← 🔐 Cryptographic Verification ← 👥 Peer Consensus
                                         ↓
📊 External APIs ← 💾 IPFS Storage ← ✅ Validated Data
```

### 🏗️ Multi-threaded Architecture

1. **Main Thread**: Fetch.AI agent execution (blocking event loop)
2. **Audio Thread**: Real-time audio capture and dB calculation
3. **MQTT Publisher**: Publishes sensor data every 2 seconds
4. **MQTT Subscriber**: Listens for peer sensor data
5. **FastAPI Thread**: Web server for status monitoring and streaming

### 🔧 Deployment Options

**Option 1: Terraform Infrastructure (Advanced)**
```bash
cd Deployment-Fluence/
terraform init && terraform apply
# Deploys to distributed infrastructure
```

**Option 2: Direct Sensor Node (Recommended)**
```bash
cd Protocol/Pi_fetch_config/
python super_combined.py
# Runs complete sensor node locally
```

## 📡 API Documentation

ECHONET provides multiple API interfaces for different use cases:

### 🎯 Sensor Node APIs (super_combined.py)

**FastAPI Server:** `http://localhost:5007` (or your device IP)

#### Real-time Streaming
```http
GET    /stream                  # Server-Sent Events stream of audio data
GET    /status                  # Current device status and metrics
GET    /health                  # Health check endpoint
```

**Example SSE Stream Response:**
```json
{
  "avg_db": 45.32,
  "mac_address": "2c:cf:67:c5:6b:63", 
  "timestamp": "2025-09-27T19:13:05.554833",
  "agent_address": "agent1qthegeucnx2gj0w8agu0xfhpf7lyjq5l8n3e89nqxhv8gvry2nwhk2hsytn",
  "agent_name": "worker_agent_4"
}
```

#### MQTT Topics
```
# Publishing sensor data
echonet/sensors/{MAC_ADDRESS}

# Payload format:
{
  "mac_address": "2c:cf:67:c5:6b:63",
  "timestamp": "2025-09-27T19:13:05.554833", 
  "decibel": 45.32
}
```

### 🌐 Backend API Endpoints

**Base URL:** `http://localhost:3001` (development)

#### Sensor Data Collection
```http
POST   /api/sensor              # Submit sensor readings (from devices)
GET    /registry                # Get sensor registry and configurations
POST   /request-slash           # Request stake slashing for failed sensors
```

#### Identity & Authentication  
```http
POST   /api/worldcoin/verify    # Verify WorldCoin identity proof
POST   /api/ens/resolve         # Resolve ENS name to address
POST   /api/ens/reverse         # Reverse resolve address to ENS name
```

#### Storage & IPFS
```http
POST   /api/cid/store           # Store data on IPFS/Filecoin
GET    /api/cid/retrieve/:cid   # Retrieve data by Content ID
POST   /api/cid/pin             # Pin important data
DELETE /api/cid/unpin/:cid      # Unpin data from storage
```

### 🐍 Python Microservice

**Base URL:** `http://localhost:8000`

```http
GET    /heatmap                 # Generate environmental heatmaps
POST   /analyze/audio           # Process audio sensor data
GET    /health                  # Service health check
GET    /docs                    # FastAPI interactive documentation
```

### 📊 Real-time Data Streaming

**Server-Sent Events (SSE):**
```javascript
// Connect to sensor node stream
const eventSource = new EventSource('http://192.168.1.100:5007/stream');

eventSource.onmessage = (event) => {
  const sensorData = JSON.parse(event.data);
  console.log(`Sensor ${sensorData.mac_address}: ${sensorData.avg_db} dB`);
};
```

**MQTT Subscription:**
```javascript
// Using MQTT.js client
const mqtt = require('mqtt');
const client = mqtt.connect('mqtt://broker.hivemq.com:1883');

client.subscribe('echonet/sensors/+');
client.on('message', (topic, message) => {
  const data = JSON.parse(message.toString());
  console.log('Received sensor data:', data);
});
```

### Error Handling

All APIs use consistent error response format:

```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2025-09-27T10:30:00Z"
}
```

## 🎯 Complete Deployment Example

### Quick Start: Run a Complete Sensor Node

```bash
# 1. Clone repository
git clone https://github.com/Saurabh-0312/ECHONET.git
cd ECHONET

# 2. Setup sensor node
cd Protocol/Pi_fetch_config
pip install -r requirements.txt

# 3. Configure your settings in super_combined.py
# - Add your Agentverse API key
# - Register your device MAC address via web UI
# - Configure API endpoints

# 4. Run complete sensor node
python super_combined.py

# Expected output:
# ✅ Automatically detected MAC Address: 2c:cf:67:c5:6b:63
# ✅ Successfully fetched registry from API
# 🎤 Audio processing started...
# 📡 MQTT Publisher connected successfully  
# 🌐 FastAPI server on http://0.0.0.0:5007
# 🤖 Agent running with consensus validation
```

### 📊 Key System Outputs

- **Real-time dB Monitoring**: ASCII visualization + numeric values
- **MQTT Publishing**: Every 2 seconds to `echonet/sensors/{MAC}`
- **API Data Submission**: Validated data sent to collector APIs
- **Peer Consensus**: Fetch.AI agents validate neighboring sensor data
- **Web Interface**: Status dashboard at `http://device_ip:5007/status`

### 🚀 Production Features

- **Autonomous Operation**: Runs 24/7 with automatic error recovery
- **Peer-to-Peer Validation**: No single point of failure for data validation  
- **Multi-threaded Architecture**: Concurrent audio, MQTT, agent, and web processing
- **Geographic Consensus**: Location-based validation using GPS coordinates
- **Cryptographic Security**: Ed25519 signatures for all agent communications
- **Token Economics**: Automatic stake slashing for sensors that fail validation consistently
- **Real-time Streaming**: Multiple APIs for data consumption (SSE, MQTT, REST)
- **Cross-platform Support**: Runs on Raspberry Pi, desktop, or cloud instances
