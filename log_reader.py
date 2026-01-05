import os
import glob
import time
import re

def read_latest_file_content(target_dir, verbose=True):
    """
    Finds the most recently created directory in the target directory,
    reads summary.txt, and extracts the completed game count.
    
    Args:
        target_dir (str): The root directory to search in.
        verbose (bool): Whether to print debug messages.
        
    Returns:
        tuple: (count (int or None), latest_dir (str or None))
    """
    if verbose:
        print(f"正在搜尋目錄: {target_dir}")
    
    if not os.path.exists(target_dir):
        if verbose: print(f"錯誤: 找不到目錄 {target_dir}")
        return None, None

    # 取得目錄下所有項目
    raw_list = glob.glob(os.path.join(target_dir, '*'))
    
    # 這裡改成過濾出「子資料夾」
    list_of_dirs = [d for d in raw_list if os.path.isdir(d)]

    if not list_of_dirs:
        if verbose: print("該目錄中沒有子資料夾。")
        return None, None

    # 找出最新的資料夾 (依據建立時間)
    latest_dir = max(list_of_dirs, key=os.path.getctime)
    if verbose: print(f"找到最新的實驗資料夾: {os.path.basename(latest_dir)}")
    
    # 指定我們要讀取的檔案: summary.txt
    target_file = os.path.join(latest_dir, "summary.txt")
    if verbose: print(f"嘗試讀取: {target_file}")
    
    if not os.path.exists(target_file):
        if verbose: print(f"錯誤: 在 {os.path.basename(latest_dir)} 中找不到 summary.txt")
        return None, latest_dir

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # 從最後一行開始往前讀
        for line in reversed(lines):
            line = line.strip()
            # 檢查是否以 "Completed" 開頭
            if line.startswith("Completed"):
                # if verbose: print(f"找到目標行: {line}") # 除錯用
                
                # 使用正則表達式尋找 Completed 後面的數字
                match = re.search(r"Completed\s+(\d+)", line)
                if match:
                    number_str = match.group(1)
                    if verbose: print(f"提取到的數字: {number_str}")
                    # 回傳 (count, dir_path)
                    return int(number_str), latest_dir
                else:
                    if verbose: print(f"警告: 雖然開頭是 Completed，但無法匹配數字格式。行內容: {line}")
                
                return None, latest_dir
                
        if verbose: print("未找到以 'Completed' 開頭的行。")
        return None, latest_dir

    except Exception as e:
        if verbose: print(f"讀取檔案時發生錯誤: {e}")
        return None, latest_dir

if __name__ == "__main__":
    # 指定目標目錄
    target_directory = r"C:\Users\RLLAB\Desktop\othello-experiments\LudiiEvalTrial"
    
    print("開始監控... (按 Ctrl+C 停止)")
    try:
        while True:
            game_count, latest_dir_path = read_latest_file_content(target_directory)
            if game_count is not None:
                # 若需要印出 dir_path:
                print(f"Current Count: {game_count}, Dir: {os.path.basename(latest_dir_path)}")
            else:
                print("Count: None (尚未找到或讀取錯誤)")
            
            print("等待 5 秒...")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n使用者停止監控。")
