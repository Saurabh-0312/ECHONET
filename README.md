# ECHONET 🌍

**A comprehensive decentralized environmental monitoring ecosystem** that combines IoT sensors, multi-blockchain protocols, AI/ML services, and distributed computing to create a transparent, incentivized network for environmental data collection, verification, and analysis.

ECHONET leverages cutting-edge technologies including **Fluence Network** for serverless microservices, **Polygon** smart c## 🚀 Key Features

### 🌍 Environmental Monitoring
- **IoT Sensor Network**: Distributed environmental sensors with AI-powered audio analysis
- **Real-time Data Streaming**: WebSocket-based live sensor data feeds
- **Geographic Visualization**: Interactive maps showing sensor locations and data
- **Data Validation**: Fetch.AI autonomous agents verify sensor authenticity

### ⛓️ Multi-Blockchain Architecture  
- **Polygon Integration**: EVM-compatible smart contracts for tokenomics and staking
- **Fetch.AI Agents**: Autonomous validation and reputation systems
- **Filecoin Storage**: Decentralized, immutable data storage via IPFS
- **Cross-chain Compatibility**: Seamless interaction between different protocols

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
- **Python 3.x** - IoT sensor programming and data processing
- **PyTorch & Transformers** - AI/ML for audio analysis
- **SoundDevice & LibROSA** - Audio processing and analysis
- **FastAPI** - High-performance Python web framework
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
│   ├── combined.py            # Main sensor data collection script
│   ├── sound-input.py         # Audio sensor processing
│   ├── stream.py              # Real-time data streaming
│   ├── requirements.txt       # Python ML/IoT dependencies
│   └── kernel_monitoring/     # Rust-based system monitoring
│       ├── Cargo.toml         # Rust project configuration
│       ├── src/               # Rust monitoring code
│       └── RASPBERRY_PI_SETUP.md # Hardware setup guide
│
├── Protocol/                    # ⛓️ Multi-Blockchain Integration
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
- **Terraform** (for Fluence deployment)

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

# 4. Setup Hardware/IoT (optional, new terminal)
cd ../Hardware
pip install -r requirements.txt
python combined.py
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

**Protocol/Fetch.AI/.env:**
```bash
WEB3_STORAGE_TOKEN=your_web3_storage_token
ETHEREUM_NODE_URL=your_ethereum_rpc
ECHONET_STAKING_CONTRACT_ADDRESS=your_contract_address
CONTRACT_OWNER_PRIVATE_KEY=your_private_key
GITHUB_PAT=your_github_token
ASI_API_KEY=your_asi_api_key
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

## 🌐 Fluence Network Integration

**Fluence** provides the decentralized computing infrastructure that powers ECHONET's microservices:

- **Serverless Architecture**: Services run on a peer-to-peer network without centralized servers
- **Service Discovery**: Automatic discovery and load balancing across Fluence peers
- **Fault Tolerance**: Built-in redundancy and resilience through distributed execution
- **Cost Efficiency**: Pay-per-use model with no infrastructure overhead
- **Scalability**: Automatic scaling based on demand across the network

### 🔧 Deployment with Terraform

Our Fluence services are managed as Infrastructure as Code using Terraform:

```bash
cd Deployment-Fluence/
terraform init
terraform plan
terraform apply
```

This deploys all ECHONET microservices to the Fluence network with:
- Automatic service registration and discovery
- Environment-specific configurations
- Resource allocation and monitoring
- Service mesh connectivity

## � API Documentation

ECHONET provides a comprehensive RESTful API through multiple microservices:

### Core API Endpoints

**Base URL:** `http://localhost:3001` (development) or your deployed backend URL

#### Sensor Management
```http
POST   /api/sensors/register     # Register new IoT sensor device
GET    /api/sensors/data        # Retrieve sensor data
POST   /api/sensors/data        # Submit new sensor readings
GET    /api/sensors/status      # Check sensor health status
```

#### Identity & Authentication  
```http
POST   /api/worldcoin/verify    # Verify WorldCoin identity proof
POST   /api/ens/resolve         # Resolve ENS name to address
POST   /api/ens/reverse         # Reverse resolve address to ENS name
```

#### Staking & Rewards
```http
POST   /api/stake/deposit       # Stake ECHO tokens
POST   /api/stake/withdraw      # Withdraw staked tokens  
GET    /api/stake/balance       # Check staking balance
GET    /api/stake/rewards       # Get pending rewards
```

#### Storage & IPFS
```http
POST   /api/cid/store           # Store data on IPFS/Filecoin
GET    /api/cid/retrieve/:cid   # Retrieve data by Content ID
POST   /api/cid/pin             # Pin important data
DELETE /api/cid/unpin/:cid      # Unpin data from storage
```

#### Analytics & Querying
```http
GET    /api/hypergraph/sensors  # Query sensor data via The Graph
GET    /api/hypergraph/analytics # Get environmental analytics
POST   /api/hypergraph/query    # Custom GraphQL queries
```

### Python Microservice Endpoints

**Base URL:** `http://localhost:8000`

```http
GET    /heatmap                 # Generate environmental heatmaps
POST   /analyze/audio           # Process audio sensor data
GET    /health                  # Service health check
GET    /docs                    # FastAPI interactive documentation
```

### Fetch.AI Agent Endpoints

**Base URL:** `http://localhost:5000`

```http
POST   /register               # Register sensor with agents
GET    /agents/status          # Check agent network status  
POST   /validate/data          # Submit data for agent validation
GET    /reputation/:sensor_id  # Get sensor reputation score
```

### WebSocket Connections

Real-time data streaming is available via WebSocket:

```javascript
// Frontend WebSocket example
const ws = new WebSocket('ws://localhost:3001/ws/sensors');
ws.onmessage = (event) => {
  const sensorData = JSON.parse(event.data);
  // Handle real-time sensor updates
};
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

## �🚀 Key Features

- **Decentralized Data Collection**: IoT sensors managed through distributed services
- **Multi-Chain Support**: Seamless integration across Polygon, Filecoin, and Fetch.AI
- **Identity Verification**: WorldCoin integration for human verification
- **Distributed Storage**: IPFS/Filecoin for immutable data storage
- **Real-time Analytics**: HyperGraph-powered environmental insights
- **Staking Economy**: Token-based incentive mechanisms for data contributors
