import pyautogui
import time
from ctypes import windll
import os
from PIL import ImageGrab

def main():
    print("=== Screen Coordinate Tool ===")
    print("Press Ctrl+C to exit.")
    
    # 获取虚拟屏幕的左上角坐标 (对于 PIL ImageGrab all_screens=True)
    user32 = windll.user32
    # SM_XVIRTUALSCREEN = 76
    # SM_YVIRTUALSCREEN = 77
    virtual_x = user32.GetSystemMetrics(76)
    virtual_y = user32.GetSystemMetrics(77)
    
    virtual_width = user32.GetSystemMetrics(78)
    virtual_height = user32.GetSystemMetrics(79)
    
    print(f"Virtual Screen Origin (PIL offset): ({virtual_x}, {virtual_y})")
    print(f"Virtual Screen Size: {virtual_width}x{virtual_height}")
    print("-" * 50)
    print(f"{'Mouse (Standard)':<20} | {'PIL ImageGrab Coords':<20}")
    print("-" * 50)

    try:
        while True:
            # 标准 Windows 坐标 (pyautogui)
            x, y = pyautogui.position()
            
            # 转换为 PIL ImageGrab (all_screens=True) 所需的坐标
            # ImageGrab 的 (0,0) 对应 virtual_x, virtual_y
            # 所以 PIL_x = x - virtual_x
            # 但有些版本的 PIL 可能直接接受标准坐标，或者行为不一致
            # 如果之前的代码使用 coordinates - virtual_origin 才能工作，那就是 offset 模式
            # 如果直接用 coordinates 就能工作，那就是标准模式
            # 这里显示两种，方便对比
            
            pil_x = x - virtual_x
            pil_y = y - virtual_y
            
            print(f"X: {x:<5} Y: {y:<5} | X: {pil_x:<5} Y: {pil_y:<5}", end='\r')
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExited.")

if __name__ == "__main__":
    main()
