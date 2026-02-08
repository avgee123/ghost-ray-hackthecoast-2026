# ghost-ray-hackthecoast-2026

𓇼 GhostRay: AI-Powered Circular Economy for Marine Debris
GhostRay is an end-to-end environmental infrastructure that incentivizes coastal communities to collect marine debris. By combining Computer Vision (YOLOv8), Multimodal AI (Gemini 2.5), and the Solana Blockchain, we transform waste into verifiable digital assets and instant rewards.

🚀 The Problem & Our Solution
Marine plastic pollution is a global crisis. Most cleanup efforts lack transparency and economic sustainability. GhostRay solves this by:
Automated Verification: AI detects and estimates the mass of debris.
Fair Incentives: Uses the World Sustainability Dataset (Kaggle) to calculate rewards based on regional sustainability needs.
Traceable Lifecycle: Blockchain-backed "Impact NFTs" track debris from collection to recycling.

🛠 Tech Stack
AI/ML: YOLOv8 (Object Detection), Google Gemini 2.0 Flash (Mass Estimation).
Blockchain: Solana (Devnet), SPL-Memo (On-chain logging), Metaplex Compressed NFTs (Low-cost impact tracking).Backend: Python (FastAPI), OpenCV.
Frontend: Next.js, TailwindCSS, Lucide Icons.

🌊 System Workflow (The Lifecycle)
Phase 1: Collection (Collector Terminal)
AI Detection: YOLOv8 detects ghost nets, plastic bottles, and debris in real-time.
Mass Estimation: Gemini 2.5 analyzes the visual context to estimate the debris weight.
Impact Minting: An NFT is minted with the status COLLECTED. This NFT contains metadata like location, estimated mass, and the collector's wallet address.

Phase 2: Traceability (Impact Dashboard)
Provides a transparent gallery of all collected debris.
Data is pulled directly from the Solana Ledger, ensuring it cannot be tampered with.

Phase 3: Finality (Recycler Terminal)
Verification: Recyclers verify the physical receipt of the debris.
Settlement: Once verified, the system triggers an Atomic Transaction:
SOL Transfer: Reward is released to the collector.
On-chain Memo: Payment proof and audit logs are recorded.
NFT Update: The cNFT status is updated to RECYCLED via Shyft API.

