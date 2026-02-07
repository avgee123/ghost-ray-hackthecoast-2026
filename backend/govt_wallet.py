import json
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.keypair import Keypair

# 1. Hubungkan ke Solana Devnet
client = Client("https://api.devnet.solana.com")

# 2. Baca file brankas pemerintah
with open("backend/my-wallet.json", "r") as f:
    secret = json.load(f)
government_keypair = Keypair.from_bytes(bytes(secret))
gov_address = government_keypair.pubkey()

print(f"Alamat Kas Pemerintah: {gov_address}")

# 3. Minta 2 SOL (2.000.000.000 Lamports)
try:
    print("Meminta dana dari pusat (Airdrop)...")
    response = client.request_airdrop(gov_address, 2000000000)
    print("✅ Berhasil! Saldo pemerintah sedang diperbarui.")
    print(f"Cek di: https://explorer.solana.com/address/{gov_address}?cluster=devnet")
except Exception as e:
    print(f"❌ Gagal meminta saldo: {e}")