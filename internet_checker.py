import socket
import time

def is_internet_available(host="8.8.8.8", port=53, timeout=3):
    """
    檢查網路是否連線。嘗試連線至 8.8.8.8 (Google DNS)。
    連線成功傳回 True，斷線或失敗傳回 False。
    """
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return True
    except (socket.timeout, socket.error):
        return False

def wait_for_internet():
    """
    檢查網路連線。
    連線成功傳回 True，斷線則傳回 False。
    """
    if is_internet_available():
        return True
    
    # 斷線時的處理
    print("網路已斷開...")
    return False

if __name__ == "__main__":
    print(wait_for_internet())

