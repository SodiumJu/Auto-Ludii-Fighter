import os

def read_model_list(file_path):
    """
    Reads a file and returns a list of non-empty lines, stripped of whitespace.
    """
    if not os.path.exists(file_path):
        print(f"錯誤: 找不到檔案 {file_path}")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 讀取所有行並去除前後空白，同時過濾掉空字串
            lines = [line.strip() for line in f.readlines()]
            # 過濾空行 (如果檔案中有空白行)
            valid_lines = [line for line in lines if line]
            
            return valid_lines
            
    except Exception as e:
        print(f"讀取檔案時發生錯誤: {e}")
        return []

if __name__ == "__main__":
    target_file = r"C:\Users\RLLAB\Desktop\othello-experiments\use-model-list.txt"
    
    print(f"正在讀取: {target_file}")
    model_list = read_model_list(target_file)
    
    print(f"共讀取到 {len(model_list)} 行資料:")
    for idx, model in enumerate(model_list):
        print(f"{idx + 1}: {model}")
