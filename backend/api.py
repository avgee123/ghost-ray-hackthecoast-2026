import cv2
import os
import json
import PIL.Image
import google.generativeai as genai
from ultralytics import YOLO
import solana_service
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# 1. SETUP
app = FastAPI()

# Izinkan Next.js mengakses backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# KONFIGURASI API & MODEL
GENAI_API_KEY = "AIzaSyBMVdMrT60J1jYCXNX1G0e8v4RoloGrdME"
genai.configure(api_key=GENAI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash') # Pakai versi flash agar cepat
yolo_model = YOLO('backend/best.pt') 
SOL_PER_KG = 0.01

# Variabel Global untuk Kamera agar bisa dipakai bersama
cap = cv2.VideoCapture(0)

# 2. FUNGSI ANALISIS GEMINI
def get_weight_analysis(image_path):
    img = PIL.Image.open(image_path)
    prompt = """
    Identify the marine debris in this image (already boxed by YOLO). 
    Estimate the weight of each item in Kilograms (kg).
    Return ONLY a JSON object like this:
    {"items": [{"label": "plastic", "weight": 0.5}], "total_weight": 0.5}
    """
    try:
        response = gemini_model.generate_content([prompt, img])
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return None

# 3. ENDPOINT VIDEO STREAMING (Untuk Monitor di Web)
def generate_frames():
    while True:
        success, frame = cap.read()
        if not success: break
        
        results = yolo_model(frame, conf=0.6, verbose=False)
        annotated_frame = results[0].plot()
        
        # Encode ke JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# 4. ENDPOINT TRIGGER PROSES (Dipanggil saat klik tombol di Next.js)
@app.post("/process_detection")
async def process_detection():
    success, frame = cap.read()
    if not success:
        return {"status": "error", "message": "Camera failed"}

    # Jalankan YOLO
    results = yolo_model(frame, conf=0.6, verbose=False)
    if len(results[0].boxes) == 0:
        return {"status": "no_debris", "message": "No debris detected in frame"}

    # Simpan Annotated Frame untuk Gemini
    temp_img = "detected_debris.jpg"
    cv2.imwrite(temp_img, results[0].plot())

    # Analisis Gemini
    analysis = get_weight_analysis(temp_img)
    if os.path.exists(temp_img): os.remove(temp_img)

    if analysis:
        total_kg = analysis.get('total_weight', 0)
        reward_sol = total_kg * SOL_PER_KG
        
        # Kirim Solana
        tx_sig = None
        if reward_sol > 0:
            tx_sig = solana_service.log_net_report("Marine Debris", reward_sol)
            
        return {
            "status": "success",
            "total_kg": total_kg,
            "reward_sol": reward_sol,
            "signature": tx_sig,
            "items": analysis.get('items', [])
        }
    
    return {"status": "error", "message": "Gemini analysis failed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)