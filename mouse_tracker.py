import pyautogui
import tkinter as tk

def show_mouse_position():
    """
    建立一個透明的浮動視窗，跟隨滑鼠顯示目前的 (X, Y) 座標。
    """
    root = tk.Tk()
    
    # 移除標題列
    root.overrideredirect(True)
    # 設定永遠在最上層
    root.wm_attributes("-topmost", True)
    # 設定背景透明 (Windows 專用: 將 'black' 設定為透明色)
    root.wm_attributes("-transparentcolor", "black")
    
    # 建立顯示文字的標籤
    # bg='black' 會被轉為透明，fg='red' 是字體顏色 (紅色醒目)
    label = tk.Label(root, text="Init", font=("Arial", 20, "bold"), fg="red", bg="black")
    label.pack()

    print("座標顯示器已啟動。按 Ctrl+C (在終端機) 或將滑鼠移到螢幕左上角來強制結束。")

    # 取得螢幕解析度 (即座標的最大範圍)
    sw, sh = pyautogui.size()
    print(f"您的螢幕解析度為: {sw} x {sh}")

    def update_position():
        try:
            # 取得滑鼠座標
            x, y = pyautogui.position()
            
            # 更新文字
            label.config(text=f"X: {x}, Y: {y}")
            
            # 讓視窗跟隨滑鼠，稍微偏移一點以免擋住點擊點
            # 注意：如果靠近螢幕邊緣可能會報錯或跑出畫面，這裡做個簡單處理
            new_x = x + 20
            new_y = y + 20
            
            # 簡單邊界檢查，以免視窗跑不見
            if new_x > sw - 150: new_x = x - 150
            if new_y > sh - 50: new_y = y - 50
            
            root.geometry(f"+{new_x}+{new_y}")
            
            # 每 50 毫秒更新一次
            root.after(50, update_position)
        except Exception as e:
            print("發生錯誤或程式終止:", e)
            root.destroy()

    # 啟動更新迴圈
    update_position()
    
    # 開始主迴圈
    root.mainloop()

if __name__ == "__main__":
    show_mouse_position()
