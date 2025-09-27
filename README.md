# ECHONET

A decentralized environmental monitoring network built with a microservice architecture on Fluence Network, combining IoT sensors, blockchain protocols, and AI services for transparent environmental data collection and verification.
![WhatsApp Image 2025-09-27 at 16 08 47](https://github.com/user-attachments/assets/a0d0b6fd-a7f3-46ff-ab49-4af2b887b095)


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
├── Frontend/           # React + Vite frontend (UI, components, assets)
├── Server/             # Node.js microservices orchestrator
│   ├── routes/         # API endpoints for each microservice
│   │   ├── sensorRoutes.js      # Sensor data management
│   │   ├── ensRoutes.js         # ENS resolution service
│   │   ├── wordCoinRoutes.js    # Identity verification
│   │   ├── stakeDataRoutes.js   # Staking mechanisms
│   │   ├── CidRoutes.js         # IPFS content addressing
│   │   └── hyperGraphSensor.js  # Analytics & querying
│   └── controller/     # Business logic for each service
├── Python-microservice/ # Python microservice for heatmap data
├── Hardware/           # IoT firmware, sensor scripts, and device code
├── Protocol/           # Multi-blockchain protocol implementations
│   ├── Fetch.AI/       # Autonomous agent services
│   ├── FileCoin/       # Decentralized storage services
│   └── Polygon/        # Smart contract artifacts and tests
├── Deployment-Fluence/ # Terraform infrastructure as code
│   ├── main.tf         # Fluence service definitions
│   ├── fluence-service.json  # Service configuration
│   └── terraform.tfvars      # Environment variables
└── docker-compose.yml  # Local development orchestration
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

## 🚀 Key Features

- **Decentralized Data Collection**: IoT sensors managed through distributed services
- **Multi-Chain Support**: Seamless integration across Polygon, Filecoin, and Fetch.AI
- **Identity Verification**: WorldCoin integration for human verification
- **Distributed Storage**: IPFS/Filecoin for immutable data storage
- **Real-time Analytics**: HyperGraph-powered environmental insights
- **Staking Economy**: Token-based incentive mechanisms for data contributors
