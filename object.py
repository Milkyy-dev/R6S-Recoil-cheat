import ctypes
import time
import threading
from pynput import mouse, keyboard

PUL = ctypes.POINTER(ctypes.c_ulong)

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("mi", MouseInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

MOUSEEVENTF_MOVE = 0x0001
INPUT_MOUSE = 0

def move_mouse(x, y):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.mi = MouseInput(dx=x, dy=y, mouseData=0, dwFlags=MOUSEEVENTF_MOVE, time=0, dwExtraInfo=ctypes.pointer(extra))
    command = Input(type=INPUT_MOUSE, ii=ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))

recoil_strength = 5
adjust_step = 1
running = True
left_down = False
right_down = False

smooth_steps = 5     
step_delay = 0.01     

def recoil_thread():
    global running
    while running:
        if left_down and right_down:
            per_step = recoil_strength / smooth_steps
            for _ in range(smooth_steps):
                if not (left_down and right_down):
                    break 
                move_mouse(0, int(per_step))
                time.sleep(step_delay)
        else:
            time.sleep(0.01)
    print("Recoil thread stopped.")

def on_click(x, y, button, pressed):
    global left_down, right_down
    if button == mouse.Button.left:
        left_down = pressed
    elif button == mouse.Button.right:
        right_down = pressed

def on_key_press(key):
    global recoil_strength, running
    try:
        if key == keyboard.Key.up:
            recoil_strength = max(1, recoil_strength - adjust_step)
            print(f"⬆ Recoil strength: {recoil_strength}")
        elif key == keyboard.Key.down:
            recoil_strength += adjust_step
            print(f"⬇ Recoil strength: {recoil_strength}")
        elif key == keyboard.Key.f9:
            print("❌ Exiting...")
            running = False
            return False
    except:
        pass

def start():
    threading.Thread(target=recoil_thread, daemon=True).start()
    with mouse.Listener(on_click=on_click) as mouse_listener, \
         keyboard.Listener(on_press=on_key_press) as keyboard_listener:
        keyboard_listener.join()
        mouse_listener.join()

if __name__ == "__main__":
    print("▶ Hold RIGHT + LEFT click to activate recoil reducer with smoothing.")
    print("⬆ / ⬇ to adjust strength, F9 to quit.")
    print("⚠ Run this as admin if you encounter issues.")
    start()
