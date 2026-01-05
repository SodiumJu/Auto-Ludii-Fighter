import pyautogui
import time

# 安全設定：將滑鼠移到螢幕左上角 (0, 0) 可以強制終止程式
pyautogui.FAILSAFE = True

def get_current_position():
    """
    這個函式會持續印出目前滑鼠的座標，方便你尋找要把滑鼠移到哪裡。
    按 Ctrl+C 可以停止。
    """
    print("按下 Ctrl+C 來停止顯示座標...")
    try:
        while True:
            x, y = pyautogui.position()
            position_str = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            print(position_str, end='')
            print('\b' * len(position_str), end='', flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('\n完成座標測量。')

def run_click_automation():
    """
    這是一個自動點擊的範例函式。
    """
    print("自動點擊程式將在 3 秒後開始，請準備好視窗...")
    time.sleep(3)

    # 範例動作 1: 移動到特定座標 (例如 100, 100)
    # duration 設定移動耗時，讓動作看起來比較像真人
    target_x, target_y = 500, 500
    print(f"正在移動到 ({target_x}, {target_y})...")
    pyautogui.moveTo(target_x, target_y, duration=1.0)

    # # 範例動作 2: 點擊滑鼠左鍵
    # print("點擊左鍵")
    # pyautogui.click() 
    
    # 範例動作 3: 點擊滑鼠右鍵
    print("點擊右鍵")
    pyautogui.rightClick()
    # 或者也可以這樣寫: pyautogui.click(button='right')

    # 也可以指定點擊位置
    # pyautogui.click(x=200, y=200)

    # 範例動作 4: 輸入文字 (只能輸入英文)
    # print("輸入文字...")
    # pyautogui.write('Hello World', interval=0.1)

    # 範例動作 4: 雙擊
    # pyautogui.doubleClick()

    print("任務完成！")

if __name__ == "__main__":
    # 如果你還不知道要點哪裡，請先取消下面這一行的註解來測量座標：
    # get_current_position()
    
    # 如果已經知道座標，就可以執行自動化流程：
    run_click_automation()
