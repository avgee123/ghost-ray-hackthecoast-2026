import cv2
import os
import json
import requests
import PIL.Image
import google.generativeai as genai
from ultralytics import YOLO
import solana_service
from engine import SustainabilityEngine
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

app = FastAPI()

# Biarkan Frontend bisa akses API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- KONFIGURASI AI & MODEL ---
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

# Gunakan versi 1.5-flash agar lebih stabil jika 2.5 belum tersedia di regionmu
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

# Pastikan path ke best.pt sudah benar setelah training selesai
yolo_model = YOLO('backend/best.pt') 

# Pastikan file CSV ada di folder backend
engine = SustainabilityEngine('backend/WorldSustainabilityDataset.csv')

# Inisialisasi Kamera
cap = cv2.VideoCapture(0)

def get_auto_country_code():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        data = response.json()
        return data.get('country_code_iso3', 'IDN') 
    except:
        return 'IDN' 

@app.get("/video_feed")
def video_feed():
    def generate_frames():
        while True:
            success, frame = cap.read()
            if not success: break
            # Deteksi Real-time untuk UI
            results = yolo_model(frame, conf=0.6, verbose=False)
            annotated_frame = results[0].plot()
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# --- PAGE 1: DETEKSI & MINT NFT ---
@app.post("/process_detection")
async def process_detection(manual_country: str = None):
    country_code = manual_country if manual_country else get_auto_country_code()
    
    success, frame = cap.read()
    if not success: return {"status": "error", "message": "Camera failed"}

    # 1. YOLO Detection
    results = yolo_model(frame, conf=0.6, verbose=False)
    if len(results[0].boxes) == 0:
        return {"status": "no_debris", "message": "No debris detected"}

    # Simpan frame sementara untuk dianalisa Gemini
    temp_img = "detected_debris.jpg"
    cv2.imwrite(temp_img, frame)

    # 2. Gemini Analysis (Weight Estimation)
    img = PIL.Image.open(temp_img)
    prompt = "Identify the type of debris and estimate its total weight in kg. Return ONLY JSON: {'total_weight': float}"
    
    try:
        response = gemini_model.generate_content([prompt, img])
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        analysis = json.loads(clean_json)
        total_kg = analysis.get('total_weight', 0.5)
    except Exception as e:
        print(f"Gemini Error: {e}")
        total_kg = 0.5 # Default jika AI sibuk
    
    if os.path.exists(temp_img): os.remove(temp_img)

    # 3. Sustainability Engine Logic
    multiplier, _ = engine.get_multiplier(country_code)
    final_reward = round(total_kg * 0.01 * multiplier, 6)

    # 4. Mint Impact NFT ke Wallet Nelayan (Collector)
    nft_address = None
    collector_wallet = os.getenv("COLLECTOR_WALLET_ADDRESS")
    
    try:
        nft_address = solana_service.mint_impact_nft(
            receiver_addr=collector_wallet,
            country=country_code,
            mass=total_kg,
            reward=final_reward,
            status="COLLECTED"
        )
    except Exception as e:
        print(f"NFT Minting failed: {e}")

    return {
        "status": "success",
        "message": "Impact Reported! NFT Issued to Collector.",
        "location": country_code,
        "weight": total_kg,
        "reward_sol_pending": final_reward,
        "nft_address": nft_address,
        "collector_wallet": collector_wallet
    }

# --- PAGE 3: RECYCLER CONFIRMATION ---
@app.post("/confirm_recycle")
async def confirm_recycle(
    nft_address: str = Body(...), 
    collector_wallet: str = Body(...), 
    amount: float = Body(...)
):
    try:
        # 1. Eksekusi Pembayaran SOL (UN -> Nelayan)
        # Fungsi ini sekarang otomatis pakai UN_PRIVATE_KEY dari .env
        tx_sig = solana_service.send_reward_with_memo(
            country="Verified", 
            weight="Recycled",
            amount_sol=amount,
            receiver_pubkey_str=collector_wallet
        )

        if tx_sig:
            # 2. Update Status NFT jadi RECYCLED
            update_res = solana_service.update_to_recycled(nft_address)
            return {
                "status": "success",
                "signature": tx_sig,
                "nft_update": update_res,
                "explorer_url": f"https://explorer.solana.com/tx/{tx_sig}?cluster=devnet"
            }
        
        return {"status": "error", "message": "Transaction failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)