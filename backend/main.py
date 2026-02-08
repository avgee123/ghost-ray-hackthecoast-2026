import cv2
import time
import os
import json
import PIL.Image
import google.generativeai as genai
from ultralytics import YOLO
import solana_service  

GENAI_API_KEY = "AIzaSyBMVdMrT60J1jYCXNX1G0e8v4RoloGrdME"
genai.configure(api_key=GENAI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')


yolo_model = YOLO('backend/best.pt') 


SOL_PER_KG = 0.01  


def get_weight_analysis(image_path):
    print("--- Mengirim foto ke Gemini untuk penaksiran berat... ---")
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
        data = json.loads(clean_json)
        return data
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return None


cap = cv2.VideoCapture(0)
sudah_dibayar = False 

print("--- GHOST-RAY: AI + BLOCKCHAIN SYSTEM ACTIVE ---")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # Jalankan YOLO (59 Classes)
    results = yolo_model(frame, conf=0.6, verbose=False)
    annotated_frame = results[0].plot()
    
    debris_detected = len(results[0].boxes) > 0

    if debris_detected and not sudah_dibayar:
        cv2.putText(annotated_frame, "DEBRIS DETECTED! ANALYZING...", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.imshow("Ghost-Ray Monitor", annotated_frame)
        cv2.waitKey(1) 


        temp_img = "detected_debris.jpg"
        cv2.imwrite(temp_img, annotated_frame)

        analysis = get_weight_analysis(temp_img)
        
        if analysis:
            total_kg = analysis.get('total_weight', 0)
            reward_sol = total_kg * SOL_PER_KG
            
            print(f"✅ Gemini Report: {total_kg} kg detected.")
            print(f"💰 Intesive Total: {reward_sol} SOL")

            if reward_sol > 0:
                tx_sig = solana_service.log_net_report("Marine Debris", reward_sol)
                if tx_sig:
                    print(f"🚀 BLOCKCHAIN SUCCESS: {tx_sig}")
                    sudah_dibayar = True
        
        if os.path.exists(temp_img): os.remove(temp_img)


    status_msg = "STATUS: TRANSACTION FINISHED" if sudah_dibayar else "STATUS: DETECTING DEBRIS..."
    color = (255, 0, 0) if sudah_dibayar else (0, 0, 255)
    cv2.putText(annotated_frame, status_msg, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    cv2.imshow("Ghost-Ray Monitor", annotated_frame)


    key = cv2.waitKey(1) & 0xFF
    if key == ord('r'):
        sudah_dibayar = False
        print("--- System Reset: Ready for new debris detection ---")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()