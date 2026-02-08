# GhostRay: AI-Powered Marine Debris Incentive System

**GhostRay** is a "Scan-to-Earn" prototype designed to incentivize the collection of marine debris by bridging AI Computer Vision with the Solana blockchain.

## 🌊 The Vision: Why Blockchain?
Marine debris collection often lacks transparency and immediate rewards. We use blockchain for three core reasons:
* **Transparency:** Every payout from the "UN Treasury" is visible on-chain, ensuring funds go directly to collectors without middlemen.
* **Immutability:** Data regarding the mass and type of waste is stored on IPFS, creating a permanent audit trail of environmental impact.
* **Instant Incentives:** Traditional grants take months; GhostRay delivers borderless SOL rewards in seconds.

## 🛠️ How It Works (The Core Logic)

### 1. Verification (The Vision Oracle)
* **Object Detection:** We use a custom **YOLO** model to identify debris in real-time.
* **Material & Mass Analysis:** Captured frames are sent to **Google Gemini 1.5 Flash**. Gemini acts as an "Environmental Oracle," identifying the material and estimating the **mass (kg)** of the debris based on its volume and type in the image.

### 2. The Reward Engine
Rewards are calculated based on ecological impact:
* **Mass-Based:** The base reward is tied directly to the **estimated weight (kg)** provided by Gemini.
* **Location Multiplier:** We use a `SustainabilityEngine` that adjusts rewards based on the country's environmental index.
* **Current Multiplier (Canada):** Since the demo is currently running in **Canada (CAN)**, the engine applies a specific multiplier from our sustainability dataset to reflect local economic and environmental standards.

### 3. On-Chain Settlement
* **IPFS Metadata:** All scan data is pushed to IPFS to secure the evidence.
* **Atomic Payout:** Once verified, the backend signs a Solana transaction to send a SOL reward directly to the collector's wallet.

## 🚧 Project Status & Pivots (Honest Disclosure)
During development, we faced a steep learning curve regarding **Metaplex Bubblegum** (the protocol for compressed NFTs). 
* **The Challenge:** Implementing cNFTs in Python is technically complex due to Merkle Tree serialization requirements, and we encountered API rate-limits during high-frequency testing.
* **The Pivot:** To ensure a stable demo, we prioritized the **AI-to-SOL Bridge**. We focused on making the payment and mass estimation 100% functional rather than shipping a buggy NFT feature.

## 🚀 Roadmap
* **Full Lifecycle cNFTs:** Transition to tracking waste from *Collected → Verified → Recycled* using on-chain state updates.
* **Hybrid Architecture:** Implement a Node.js microservice specifically to handle high-speed cNFT minting.
* **On-Chain Logic:** Migrate payout rules from the backend to an **Anchor (Rust)** smart contract for full decentralization.

## 💻 Tech Stack
* **AI:** Ultralytics YOLO, Google Gemini 1.5 Flash.
* **Backend:** Python (FastAPI), Uvicorn.
* **Blockchain:** Solana (Devnet), Shyft API, `solders` library.
* **Frontend:** Next.js (Tailwind CSS).