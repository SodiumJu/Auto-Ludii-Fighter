import pytesseract
from PIL import Image, ImageGrab
import os
import time

# --- 設定 Tesseract 路徑 ---
# 指定您剛剛安裝的 Tesseract 執行檔位置
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
else:
    print(f"警告: 找不到檔案: {TESSERACT_CMD}")

screenshots_path = "screenshots"
if not os.path.exists(screenshots_path):
    os.makedirs(screenshots_path)

def capture_and_read(p1, p2):
    """
    從兩個座標點 (左上與右下) 定義的區塊進行截圖與文字辨識
    
    Args:
        p1 (tuple): (x1, y1)
        p2 (tuple): (x2, y2)
        
    Returns:
        str: 辨識出的文字
    """
    try:
        # 計算左上角座標與寬高
        left = min(p1[0], p2[0])
        top = min(p1[1], p2[1])
        right = max(p1[0], p2[0])
        bottom = max(p1[1], p2[1])
        
        width = right - left
        height = bottom - top
        
        print(f"定義區塊: P1{p1}, P2{p2} -> Region: (L:{left}, T:{top}, W:{width}, H:{height})")

        # 使用 ImageGrab 支援多螢幕截圖
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)
        
        # 儲存截圖以便確認
        save_path = os.path.join(screenshots_path, "ocr_debug.png")
        screenshot.save(save_path)
        print(f"已儲存截圖至: {save_path}")
        
        # 2. 進行 OCR 辨識
        # lang='eng+chi_tra' 可以同時支援英文和繁體中文 (前提是有下載中文包)
        # 預設只有 'eng'
        text = pytesseract.image_to_string(screenshot, lang='eng')
        
        return text.strip()
    
    except Exception as e:
        return f"發生錯誤: {e}"

if __name__ == "__main__":
    # --- 使用範例 ---
    
    # 給予左上角與右下角座標
    p_left_top = (1288, 60)
    p_right_bottom = (2555, 677)
    
    recognized_text = capture_and_read(p_left_top, p_right_bottom)
    
    print("-" * 30)
    print("辨識結果:")
    print(recognized_text)
    print("-" * 30)
