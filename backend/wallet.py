import json
from solders.keypair import Keypair

# 1. Bikin kunci baru
keypair = Keypair()

# 2. Ambil angkanya saja (ini isi dari my-wallet.json nanti)
key_bytes = list(keypair.to_bytes())

# 3. Simpan jadi file
with open("backend/my-wallet.json", "w") as f:
    json.dump(key_bytes, f)

print(f"✅ File my-wallet.json sudah muncul di folder backend!")
print(f"Address Dompet Admin kamu: {keypair.pubkey()}")