import pyautogui
import tkinter as tk
import threading
import time
import os
import pytesseract
from PIL import Image, ImageGrab
import pyperclip
import shutil
from internet_checker import wait_for_internet
import sys

# Tesseract 執行檔路徑預設值 (稍後會由 config 覆寫)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



# 全域變數，用於顯示目前動作狀態
current_status = "Waiting to start..."

def get_text_from_screen(p1, p2, config_data=None):
    """
    擷取 p1, p2 定義的矩形區域名，並使用 pytesseract 進行 OCR 辨識。
    返回辨識出的文字。
    """
    try:
        left = min(p1[0], p2[0])
        top = min(p1[1], p2[1])
        width = abs(p2[0] - p1[0])
        height = abs(p2[1] - p1[1])
        
        # 使用 ImageGrab 支援多螢幕截圖 (all_screens=True)
        # 這裡直接使用 p1, p2 計算出的 bbox，不進行虛擬座標轉換
        right = left + width
        bottom = top + height
        
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)
        
        # 除錯: 儲存截圖到 screenshots 資料夾，並以時間命名
        save_dir = config_data.get('screenshots_path', r"screenshots") if config_data else r"screenshots"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        # 加上微秒以避免快速連續截圖時檔名重複
        timestamp += f"_{int(time.time() * 1000) % 1000:03d}"
        
        filename = f"screenshot_{timestamp}.png"
        debug_path = os.path.join(save_dir, filename)
        
        screenshot.save(debug_path)
        print(f"Debug: Screenshot saved to {debug_path}")
        
        # OCR 辨識
        text = pytesseract.image_to_string(screenshot)
        return text.strip()
    except Exception as e:
        print(f"OCR Function Error: {e}")
        return ""

def detach_minizero(pos_data, config_data=None):
    """
    執行 Minizero 中斷連線的動作序列。
    """
    # 0. 先移到 custom_pos 點左鍵
    c_x, c_y = pos_data.get('custom_pos', (-1877, 43))
    print(f"Moving to custom_pos: {c_x}, {c_y}")
    pyautogui.moveTo(c_x, c_y, duration=0.5)
    pyautogui.click()
    time.sleep(0.5)

    # 1 滑鼠移到 detach_pos
    dx, dy = pos_data.get('detach_pos', (-1877, 103))
    print(f"Moving to detach_pos: {dx}, {dy}")
    pyautogui.moveTo(dx, dy, duration=1.0)
    
    # 2 點左鍵 (detach)
    print("Clicking detach...")
    pyautogui.click()
    time.sleep(0.5)

    # 3 滑鼠移到 detach_check_box_pos 點左鍵
    dcx, dcy = pos_data.get('detach_check_box_pos', (1277, 726))
    print(f"Moving to detach_check_box_pos: {dcx}, {dcy}")
    pyautogui.moveTo(dcx, dcy, duration=1.0)
    
    print("Clicking detach checkbox...")
    pyautogui.click()
    time.sleep(0.5)

def attach_minizero(pos_data, sc, ts, config_data=None):
    """
    執行 Attach Process 的動作序列。
    """
    global current_status
    # 1. Move to custom_pos and Click
    c_x, c_y = pos_data.get('custom_pos', (-1877, 43))
    current_status = f"[{sc}/{ts}] Click Custom"
    print(current_status)
    pyautogui.moveTo(c_x, c_y, duration=0.5)
    pyautogui.click()
    time.sleep(0.5)

    # 2. Move to attach_pos and Click
    a_x, a_y = pos_data.get('attach_pos', (-1877, 76))
    current_status = f"[{sc}/{ts}] Click Attach"
    print(current_status)
    pyautogui.moveTo(a_x, a_y, duration=0.5)
    pyautogui.click()
    time.sleep(3.0)

    # 3. Move to alpha_zero_1899_pos and Click
    # Modified: Move horizontally to -1478 first, then down to 139
    az_x, az_y = pos_data.get('alpha_zero_1899_pos', (-1478, 139))
    current_status = f"[{sc}/{ts}] Click AlphaZero (H->V)"
    print(current_status)
    
    # 從當前位置 (attach_pos) 水平移動到 az_x
    # y 保持不變 (using attach_pos y: a_y)
    pyautogui.moveTo(az_x, a_y, duration=0.5)
    # 再垂直移動到 az_y
    pyautogui.moveTo(az_x, az_y, duration=0.5)
    
    pyautogui.click()
    time.sleep(5.0)

def check_and_terminate(pos_data, config_data=None):
    """
    檢查螢幕上是否有 Terminate 按鈕，如果有則點擊。
    """
    # 先點擊 Ludii 視窗以確保它在最上層
    cx, cy = pos_data.get('click_ludii_pos', (2000, 28))
    print(f"Focusing Ludii at {cx}, {cy}")
    pyautogui.moveTo(cx, cy, duration=0.5)
    pyautogui.click()
    time.sleep(0.5)

    p1 = pos_data.get('terminate_check_box_pos_left_top', (1281, 708))
    p2 = pos_data.get('terminate_check_box_pos_right_bottom', (1393, 748))
    recognized_text = get_text_from_screen(p1, p2, config_data)
    if "Terminate" in recognized_text:
        tx, ty = pos_data.get('terminate_check_box_pos', (1325, 728))
        print(f"Detected Terminate button. Clicking at {tx}, {ty}")
        pyautogui.moveTo(tx, ty, duration=0.5)
        pyautogui.click()
        time.sleep(0.5)
        return True
    return False

def reopen_ludii(pos_data, config_data=None):
    """
    關閉並重新開啟 Ludii 應用程式。
    """
    check_and_terminate(pos_data, config_data)
    tx, ty = pos_data.get('close_ludii_pos', (2530, 20))
    print(f"Closing Ludii at {tx}, {ty}")
    pyautogui.moveTo(tx, ty, duration=0.5)
    pyautogui.click()
    time.sleep(0.5)

    tx, ty = pos_data.get('ludii_exe_pos', (466, 334))
    print(f"Opening Ludii at {tx}, {ty}")
    pyautogui.moveTo(tx, ty, duration=0.5)
    pyautogui.doubleClick()
    time.sleep(10.0) # 等待 Ludii 啟動

def reopen_terminal(pos_data, config_data):
    """
    重新建立 Terminal 環境（SSH 與 Tmux）。
    """
    # 重新開啟主 Console (點開再關掉?)
    mox, moy = pos_data.get('open_main_console_pos', (337, 716))
    print(f"Clicking open main console at {mox}, {moy}")
    pyautogui.moveTo(mox, moy, duration=0.5)
    pyautogui.click()
    time.sleep(0.5)

    mcx, mcy = pos_data.get('close_main_console_pos', (288, 720))
    print(f"Clicking close main console at {mcx}, {mcy}")
    pyautogui.moveTo(mcx, mcy, duration=0.5)
    pyautogui.click()
    time.sleep(0.5)

    cx, cy = pos_data.get('console_pos', (700, 900))
    print(f"Moving to main console at {cx}, {cy} to re-establish environment...")
    pyautogui.moveTo(cx, cy, duration=0.5)
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(1.0)
    
    # SSH RLG05
    print("SSH to RLG05...")
    ssh_cmd = config_data.get('ssh_cmd', "")
    pyperclip.copy(f"{ssh_cmd}")
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    time.sleep(3.0) # 等待登入
    
    # Tmux Attach
    print("Attaching to tmux session RGSC-2...")
    tmux_cmd = config_data.get('tmux_cmd', "")
    pyperclip.copy(f"{tmux_cmd}")
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    time.sleep(2.0)

def check_main_console_disconnect(pos_data, config_data=None):
    """
    使用 OCR 判別主 Console 是否斷線。
    """
    p1 = pos_data.get('console_pos_left_top', (4, 743))
    p2 = pos_data.get('console_pos_right_bottom', (1244, 1322))
    recognized_text = get_text_from_screen(p1, p2, config_data)
    print("辨識結果:", recognized_text)
    return "send disconnect" in recognized_text

def write_log(log_path, model_name, count, reestablish_num, remaining_fights):
    """
    將當前狀態寫入 Log 檔案。
    """
    if not log_path:
        return
    try:
        with open(log_path, 'w') as log_file:
            log_file.write(f"model_name: {model_name}\n")
            log_file.write(f"count: {count}\n")
            log_file.write(f"reestablish_num: {reestablish_num}\n")
            log_file.write(f"remaining_fights: {remaining_fights}\n")
    except Exception as e:
        print(f"Write Log Error: {e}")

def read_log(log_path):
    """
    從 Log 檔案讀取狀態。
    """
    log_model_name = None
    log_count = 0
    log_reestablish_num = 0
    log_remaining_fights = 0
    
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r') as f:
                for line in f:
                    if 'model_name:' in line:
                        log_model_name = line.split('model_name: ')[1].strip()
                    elif 'count:' in line:
                        log_count = int(line.split('count: ')[1].strip())
                    elif 'reestablish_num:' in line:
                        log_reestablish_num = int(line.split('reestablish_num: ')[1].strip())
                    elif 'remaining_fights:' in line:
                        log_remaining_fights = int(line.split('remaining_fights: ')[1].strip())
        except Exception as e:
            print(f"Read Log Error: {e}")
            
    return log_model_name, log_count, log_reestablish_num, log_remaining_fights

def remove_dir(path):
    """
    刪除資料夾及其內容。
    """
    if path and os.path.exists(path):
        try:
            print(f"正在刪除資料夾: {path}")
            shutil.rmtree(path)
            print("刪除完成。")
        except Exception as e:
            print(f"刪除資料夾時發生錯誤: {e}")

def auto_click_actions(config_data, pos_data):
    """
    執行自動點擊動作的函數，將在獨立執行緒中運行。
    """
    global current_status
    
    current_status = "Initializing..."
    print(current_status)
    time.sleep(3)
    
    # 從字典解包參數，方便後續使用
    replicate_num = config_data.get('replicate_num', 3)
    model_file_names = config_data.get('model_file_names', [])
    model_prefix = config_data.get('model_prefix', "")
    execute_str = config_data.get('execute_str', "")

    need_reestablish_connection = False
    try:
        log_path = config_data.get('log_path', "")
        total_steps = len(model_file_names)
        step_count = 0
        log_model_name, log_count, log_reestablish_num, log_remaining_fights = read_log(log_path)
        
        # remove previous models in the list
        if log_model_name != None:
            for i in range(len(model_file_names)):
                if model_file_names[i] == log_model_name:
                    model_file_names = model_file_names[i:]
                    if log_remaining_fights <= 0:
                        model_file_names = model_file_names[1:]
                    break

        for model_name in model_file_names:
            step_count += 1

            # 加入一個 retry 迴圈，如果斷線恢復後需要重跑，就藉由 continue 回到這裡
            reestablish_num = 0
            remaining_fights = 0
            while True:
                attach_success = False
                attempt = 0
                while attach_success == False:
                    attempt += 1

                    # close Ludii and Open a new Ludii
                    reopen_ludii(pos_data, config_data)

                    # 重新建立 Terminal 環境 (SSH 與 Tmux)
                    reopen_terminal(pos_data, config_data)
                    # 組合指令字串
                    # 取得必要參數

                    port = config_data.get('port', 8899)
                    model_id = config_data.get('model_id', 1)
                    gpu_id = config_data.get('gpu_id', 2)
                    fight_num = config_data.get('fight_num', 10)
                    real_fight_num = fight_num
                    
                    # 使用 read_log 函數讀取狀態
                    log_model_name, log_count, log_reestablish_num, log_remaining_fights = read_log(log_path)
                    
                    if log_remaining_fights > 0:
                        model_name = log_model_name
                        reestablish_num = log_reestablish_num
                        remaining_fights = log_remaining_fights
                        real_fight_num = log_remaining_fights
                        print(f"Continue from previous run: {model_name}, real_fight_num: {real_fight_num}, reestablish_num: {reestablish_num}, remaining_fights: {remaining_fights}")

                    
                    # 處理 model_name (確保有 .pt)
                    if not model_name.endswith('.pt'):
                        model_name = f"{model_name}.pt"
                    
                    # 處理 model_prefix
                    prefix = model_prefix
                    if not prefix.endswith('-'):
                        prefix += '-'
                    
                    # 建構多行字串
                    # 注意: 這裡使用 f-string 和 {{ }} 來保留 shell 變數語法 ${...}
                    
                    line1 = f"port={port}"
                    line2 = f"model_id={model_id}"
                    line3 = f'model_name="{model_name}"'
                    line4 = f'model_path="{prefix}${{model_id}}/model/${{model_name}}"'
                    # execute_str 預設為 ...nn_file_name=
                    line5 = f'executable="{execute_str}${{model_path}}"'
                    line6 = f'echo ${{executable}}'
                    line7 = f'CUDA_VISIBLE_DEVICES={gpu_id} gogui-server -port $port -loop -verbose "$executable"'
                    paste_str = f"{line1}\n{line2}\n{line3}\n{line4}\n{line5}\n{line6}\n{line7}"

                    tx, ty = pos_data.get('console_pos', (700, 900))
                    
                    current_status = f"[{step_count}/{total_steps}] Move to ({tx}, {ty})"
                    print(current_status)
                    pyautogui.moveTo(tx, ty, duration=1.0)
                    
                    current_status = f"[{step_count}/{total_steps}] Click Left"
                    pyautogui.click()
                    time.sleep(0.5)

                    # Step 2: Press Ctrl+C
                    current_status = f"[{step_count}/{total_steps}] Press Ctrl+C"
                    print(current_status)
                    pyautogui.hotkey('ctrl', 'c')
                    time.sleep(1.0) # 等待一下確保中斷

                    # Step 3: Type paste_str and Enter
                    current_status = f"[{step_count}/{total_steps}] Input Command"
                    print(f"Typing:\n{paste_str}")
                    # 使用貼上方式輸入字串 (避免太長打錯或太慢)
                    pyperclip.copy(paste_str)
                    time.sleep(0.1)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.5)
                    
                    current_status = f"[{step_count}/{total_steps}] Press Enter"
                    pyautogui.press('enter')
                    time.sleep(0.1)
                    pyautogui.press('enter')
                    time.sleep(5.0)

                    # Step 4: Attach Process
                    attach_minizero(pos_data, step_count, total_steps, config_data)
                    
                    # Step 5: Check attach again (Retry 3 times)
                    p1 = pos_data.get('attach_check_box_pos_left_top', (1288, 60))
                    p2 = pos_data.get('attach_check_box_pos_right_bottom', (2555, 677))
                    time.sleep(15.0)
                    text_check = get_text_from_screen(p1, p2, config_data)
                    print(f"Check OCR: {text_check}")
                    
                    if "MiniZero" in text_check:
                        print("Successfully Attached (MiniZero found)!")
                        current_status = f"[{step_count}/{total_steps}] Attached confirmed"
                        attach_success = True
                    else:
                        print("MiniZero not found, waiting...")
                        print(f"Attempt {attempt}")
                        time.sleep(5.0)
                        attach_minizero(pos_data, step_count, total_steps, config_data)

                
                # Step 5.5: Minizero Dropdown Setup
                # 1. 移到 minizero_click_pos 點左鍵
                mz_x, mz_y = pos_data.get('minizero_click_pos', (-1277, 136))
                current_status = f"[{step_count}/{total_steps}] Click Minizero Dropdown"
                print(current_status)
                pyautogui.moveTo(mz_x, mz_y, duration=0.5)
                pyautogui.click()
                time.sleep(0.5)

                    # 2. 移到 minizero_click_down_list_pos 點左鍵
                mzl_x, mzl_y = pos_data.get('minizero_click_down_list_pos', (-1370, 208))
                current_status = f"[{step_count}/{total_steps}] Select from List"
                print(current_status)
                pyautogui.moveTo(mzl_x, mzl_y, duration=0.5)
                pyautogui.click()
                time.sleep(0.5)

                    # 3. 輸入 a 然後按 enter
                print("Typing 'a' and Enter...")
                pyautogui.write('a', interval=0.1)
                time.sleep(0.2)
                pyautogui.press('enter')
                time.sleep(0.5)
                    
                    # 4. Move to apply_pos and Click
                ap_x, ap_y = pos_data.get('apply_pos', (-1299, 449))
                current_status = f"[{step_count}/{total_steps}] Click Apply"
                print(current_status)
                pyautogui.moveTo(ap_x, ap_y, duration=0.5)
                pyautogui.click()
                time.sleep(0.5)
                
                # Step 6: Setup Fight
                # 1. 移到 analysis_pos 點左鍵
                an_x, an_y = pos_data.get('analysis_pos', (-2235, 49))
                current_status = f"[{step_count}/{total_steps}] Click Analysis"
                print(current_status)
                pyautogui.moveTo(an_x, an_y, duration=0.5)
                pyautogui.click()
                time.sleep(0.5)

                # 2. 移到 ai_vs_ai_pos 點左鍵
                ai_x, ai_y = pos_data.get('ai_vs_ai_pos', (-2189, 220))
                current_status = f"[{step_count}/{total_steps}] Click AI vs AI"
                print(current_status)
                pyautogui.moveTo(ai_x, ai_y, duration=0.5)
                pyautogui.click()
                time.sleep(0.5)

                # 3. 移到 fight_num_pos 點左鍵 輸入 fight_num
                fn_x, fn_y = pos_data.get('fight_num_pos', (1183, 731))
                current_status = f"[{step_count}/{total_steps}] Input fight_num"
                print(current_status)
                pyautogui.moveTo(fn_x, fn_y, duration=0.5)
                pyautogui.click()
                time.sleep(0.2)
                # 先清除可能存在的舊數值 (Ctrl+A -> Backspace) 比較保險，或者直接打
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                
                pyautogui.write(str(real_fight_num), interval=0.05)
                time.sleep(0.5)

                # 4. 移到 ok_pos 點左鍵
                ok_x, ok_y = pos_data.get('ok_pos', (1233, 778))
                current_status = f"[{step_count}/{total_steps}] Click OK"
                print(current_status)
                pyautogui.moveTo(ok_x, ok_y, duration=0.5)
                pyautogui.click()
                time.sleep(0.5)

                # Step 7. check the fight is finished
                ludii_trail_path = config_data.get('ludii_trail_path', "")
                if not ludii_trail_path:
                    print("Error: No ludii_trail_path configured.")
                else:
                    current_status = f"[{step_count}/{total_steps}] Waiting for finish..."
                    print("Start monitoring game count...")
                    last_progress_count = -1
                    last_progress_time = time.time()
                    while True:
                        need_reestablish_connection = False
                        try:
                            # 檢查網路連線 (直到恢復為止)
                            offline_start_time = None
                            while not wait_for_internet():
                                if offline_start_time is None:
                                    offline_start_time = time.time()
                                # 只有當斷線持續超過 5 秒，才標記需要重新建立連線 (Need Re-establish)
                                if time.time() - offline_start_time >= 5 and need_reestablish_connection == False:
                                    
                                    count, _ = read_latest_file_content(ludii_trail_path, verbose=False)
                                    remaining_fights = real_fight_num - int(count)
                                    if remaining_fights == 0:
                                        break
                                    need_reestablish_connection = check_and_terminate(pos_data, config_data)
                                current_status = "Waiting for Internet..."
                                time.sleep(2)
                            
                            # 檢核進度是否卡住 (超過 5 分鐘)
                            p_count, latest_dir = read_latest_file_content(ludii_trail_path, verbose=False)
                            if p_count is not None:
                                p_count = 0 if "Reversi_" not in latest_dir else p_count
                                p_count_int = int(p_count)
                                if p_count_int > last_progress_count:
                                    last_progress_count = p_count_int
                                    last_progress_time = time.time()
                                
                                if (time.time() - last_progress_time > 600) and (real_fight_num - p_count_int != 0) :
                                    print(f"偵測到遊戲進度卡住超過 5 分鐘 (目前: {p_count_int})，準備重新建立連線...")
                                    check_and_terminate(pos_data, config_data)
                                    need_reestablish_connection = True

                            if need_reestablish_connection:
                                count, latest_dir = read_latest_file_content(ludii_trail_path, verbose=False)
                                if latest_dir and "Reversi_" in latest_dir:
                                    reestablish_num += 1
                                    write_log(log_path, model_name, count, reestablish_num, real_fight_num - count)
                                    new_folder_name = model_name.replace('.pt', f'-re-{reestablish_num}')
                                    parent_dir = os.path.dirname(latest_dir)
                                    new_path = os.path.join(parent_dir, new_folder_name)
                                    
                                    print(f"Renaming {latest_dir} to {new_path}")
                                    # if existed, remove it (使用 remove_dir 處理資料夾)
                                    if os.path.exists(new_path):
                                        remove_dir(new_path)
                                    
                                    time.sleep(0.5) # 給系統一點時間反應
                                    os.rename(latest_dir, new_path)
                                break
                            
                            # 讀取當前完成數，verbose=False 減少 log，或可設為 True 除錯
                            count, latest_dir = read_latest_file_content(ludii_trail_path, verbose=False)
                            
                            if count is not None:
                                current_status = f"[{step_count}/{total_steps}] Progress: {count}/{fight_num}"
                                count = 0 if "Reversi_" not in latest_dir else count
                                # flush the print
                                print(f"Current Progress: {count}/{real_fight_num}                  ", end="\r")
                                write_log(log_path, model_name, count, reestablish_num, real_fight_num - count)
                                
                                if count >= real_fight_num and "Reversi_" in latest_dir:
                                    print("Target fight num reached!")
                                    
                                    # Rename folder if latest_dir is valid
                                    if latest_dir and os.path.exists(latest_dir):
                                        try:
                                            # model_name e.g. "weight_iter_100000.pt" -> "weight_iter_100000"
                                            new_folder_name = model_name.replace('.pt', '')
                                            parent_dir = os.path.dirname(latest_dir)
                                            new_path = os.path.join(parent_dir, new_folder_name)
                                            
                                            print(f"Renaming {latest_dir} to {new_path}")
                                            # if existed, remove it (使用 remove_dir 處理資料夾)
                                            if os.path.exists(new_path):
                                                remove_dir(new_path)
                                            
                                            time.sleep(0.5) # 給系統一點時間反應
                                            os.rename(latest_dir, new_path)
                                        except Exception as rename_error:
                                            print(f"Rename Error: {rename_error}")
                                    
                                    break
                            else:
                                print(f"Waiting... (Count not found yet)", end="\r")
                        except Exception as e:
                            print(f"Monitor Error: {e}")
                            
                        # 每 5 秒檢查一次
                        time.sleep(5)
                
                # 任務完成，進入下一個循環
                # After finished detach
                detach_minizero(pos_data, config_data)
                
                # 檢查是否是因為斷線中途跳出，如果是，就繼續 while True 迴圈重跑同一模型
                if need_reestablish_connection:
                    print(f"偵測到斷線並已恢復，準備重新執行模型: {model_name}")
                    continue
                
                print("Task finished, moving to next model...")
                current_status = f"[{step_count}/{total_steps}] Completed."
                time.sleep(5)
                break # 正常完成，跳出 while True 迴圈，處理下一個 model_name

        current_status = "All tasks completed."
        print(current_status)
        
    except pyautogui.FailSafeException:
        current_status = "FailSafe Triggered!"
        print("FailSafe triggered from mouse corner!")
    except Exception as e:
        current_status = f"Error: {e}"
        print(f"Error during automation: {e}")

def show_mouse_position_and_run_automation(config_data, pos_data):
    """
    建立一個透明的浮動視窗，跟隨滑鼠顯示目前的 (X, Y) 座標與動作狀態。
    """
    root = tk.Tk()
    
    # 移除標題列
    root.overrideredirect(True)
    # 設定永遠在最上層
    root.wm_attributes("-topmost", True)
    # 設定背景透明 (Windows 專用)
    root.wm_attributes("-transparentcolor", "black")
    
    # 建立顯示文字的標籤 (座標)
    label_pos = tk.Label(root, text="XY: 0, 0", font=("Arial", 16, "bold"), fg="#00FF00", bg="black")
    label_pos.pack(anchor="w")
    
    # 建立顯示文字的標籤 (狀態)
    label_status = tk.Label(root, text="Init...", font=("Arial", 12), fg="yellow", bg="black")
    label_status.pack(anchor="w")

    print("座標顯示器已啟動。")
    print("按 Ctrl+C (在終端機) 或將滑鼠大力移到螢幕角落來強制結束 (FailSafe)。")

    # 取得螢幕解析度
    try:
        sw, sh = pyautogui.size()
    except:
        sw, sh = 1920, 1080

    def update_gui():
        try:
            # 取得滑鼠座標
            x, y = pyautogui.position()
            
            # 更新文字
            label_pos.config(text=f"Pos: {x}, {y}")
            label_status.config(text=current_status)
            
            # 讓視窗跟隨滑鼠
            new_x = x + 20
            new_y = y + 20
            
            # 簡單邊界檢查
            if new_x > sw - 250: new_x = x - 250
            if new_y > sh - 100: new_y = y - 100
            
            root.geometry(f"+{new_x}+{new_y}")
            
            # 每 50 毫秒更新一次
            root.after(50, update_gui)
        except Exception:
            try:
                root.destroy()
            except:
                pass

    # 啟動自動化執行緒 (傳入參數字典)
    t = threading.Thread(target=auto_click_actions, args=(config_data, pos_data))
    t.daemon = True
    t.start()

    # 啟動 GUI 更新迴圈
    update_gui()
    
    # 開始主迴圈
    root.mainloop()

import configparser
from model_list_reader import read_model_list
from log_reader import read_latest_file_content

if __name__ == "__main__":
    # 讀取設定檔
    config = configparser.ConfigParser()
    config_file = sys.argv[1]
    if not os.path.exists(config_file):
        print(f"Config file not found: {config_file}, using default.")
        config_file = 'config.ini'

    # 預設值
    config_data = {
        'list_path': None,
        'replicate_num': 3,
        'model_prefix': "",
        'execute_str': "",
        'model_file_names': [],
        'port': 8899,
        'model_id': 1,
        'fight_num': 10
    }

    if os.path.exists(config_file):
        config.read(config_file)
        try:
            config_data['list_path'] = config.get('Settings', 'model_list_path', fallback=None)
            config_data['replicate_num'] = config.getint('Settings', 'model_replicate_num', fallback=3)
            
            # 讀取參數
            config_data['port'] = config.getint('Settings', 'port', fallback=8899)
            config_data['model_id'] = config.getint('Settings', 'model_id', fallback=1)
            
            config_data['model_prefix'] = config.get('Settings', 'model_prefix', fallback="")
            config_data['execute_str'] = config.get('Settings', 'execute_str', fallback="")
            config_data['fight_num'] = config.getint('Settings', 'fight_num', fallback=10)
            config_data['ludii_trail_path'] = config.get('Settings', 'ludii_trail_path', fallback="")
            config_data['gpu_id'] = config.getint('Settings', 'gpu_id', fallback=2)
            config_data['ssh_cmd'] = config.get('Settings', 'ssh_cmd', fallback="")
            config_data['tmux_cmd'] = config.get('Settings', 'tmux_cmd', fallback="")
            config_data['pytesseract_path'] = config.get('Settings', 'pytesseract_path', fallback=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
            config_data['screenshots_path'] = config.get('Settings', 'screenshots_path', fallback=r"screenshots")

            # 更新 Tesseract 路徑
            pytesseract.pytesseract.tesseract_cmd = config_data['pytesseract_path']

            # if config_data['ludii_trail_path'] is not existed, create it
            if not os.path.exists(config_data['ludii_trail_path']):
                os.makedirs(config_data['ludii_trail_path'])
            
            # remove everything in screenshots
            if os.path.exists(config_data['screenshots_path']):
                for file in os.listdir(config_data['screenshots_path']):
                    os.remove(os.path.join(config_data['screenshots_path'], file))
            
            # 讀取 Mouse Pos
            # 建立一個新的 dict pos_data
            pos_data = {}
            if 'Mouse Pos' in config:
                for key in config['Mouse Pos']:
                    try:
                        pos_str = config['Mouse Pos'][key]
                        # 解析字串 "X, Y" -> (x, y)
                        # Remove comma if present, then split by whitespace
                        px, py = map(int, pos_str.replace(',', ' ').split())
                        pos_data[key] = (px, py)
                    except Exception as e:
                        print(f"解析座標錯誤 ({key}): {e}")
            
            # 確保必要的值存在 (fallback)
            if 'console_pos' not in pos_data:
                 pos_data['console_pos'] = (700, 700)
            
        except Exception as e:
            print(f"讀取設定檔錯誤: {e}")
            pos_data = {'console_pos': (700, 700)} # fallback if unexpected error
    else:
        print("找不到 config.ini，使用預設值。")
        pos_data = {'console_pos': (700, 700)}

    print(f"Config: {config_data}")

    if config_data['list_path']:
        config_data['model_file_names'] = read_model_list(config_data['list_path'])
    else:
        print("未指定模型列表路徑。")
        config_data['model_file_names'] = []
    
    if not config_data['model_file_names']:
        print("警告: 模型列表為空，腳本即將結束。")
    else:
        show_mouse_position_and_run_automation(config_data, pos_data)
