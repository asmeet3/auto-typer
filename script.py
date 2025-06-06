import pyautogui
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox

try:
    import keyboard
    KEYBOARD_LIB_AVAILABLE = True
except ImportError:
    KEYBOARD_LIB_AVAILABLE = False
    print("Warning: 'keyboard' library not found. ESC hotkey to stop typing will not be available.")
    print("Install it with: pip install keyboard")

stop_typing_flag = False

def set_stop_typing_flag():
    global stop_typing_flag
    print("ESC pressed, attempting to stop typing...")
    stop_typing_flag = True

def type_code_from_gui(code_to_type, initial_delay_str, char_delay_str, status_label, root_window):
    global stop_typing_flag
    stop_typing_flag = False

    try:
        initial_delay = float(initial_delay_str)
        char_delay = float(char_delay_str)
    except ValueError:
        messagebox.showerror("Input Error", "Delays must be numeric values.")
        status_label.config(text="Error: Delays must be numeric.")
        if KEYBOARD_LIB_AVAILABLE:
            try: keyboard.remove_hotkey('esc')
            except: pass
        if root_window.state() == 'iconic':
             root_window.after(100, root_window.deiconify)
        return

    if initial_delay < 0 or char_delay < 0:
        messagebox.showerror("Input Error", "Delays cannot be negative.")
        status_label.config(text="Error: Delays cannot be negative.")
        if KEYBOARD_LIB_AVAILABLE:
            try: keyboard.remove_hotkey('esc')
            except: pass
        if root_window.state() == 'iconic':
            root_window.after(100, root_window.deiconify)
        return

    if KEYBOARD_LIB_AVAILABLE:
        try:
            keyboard.remove_hotkey('esc')
        except:
            pass
        keyboard.add_hotkey('esc', set_stop_typing_flag)
        print("ESC hotkey registered. Press ESC to stop typing.")

    try:
        status_label.config(text=f"Switch window in {initial_delay}s... (Press ESC to cancel)")
        root_window.update_idletasks()

        for i in range(int(initial_delay * 10), 0, -1):
            if stop_typing_flag:
                status_label.config(text="Typing cancelled during initial delay.")
                return
            status_label.config(text=f"Switch window in {i/10:.1f}s... (Press ESC to cancel)")
            root_window.update_idletasks()
            time.sleep(0.1)
        
        if stop_typing_flag:
            status_label.config(text="Typing cancelled during initial delay.")
            return

        status_label.config(text="Starting to type... (Press ESC to stop)")
        root_window.update_idletasks()

        for char_index, char in enumerate(code_to_type):
            if stop_typing_flag:
                status_label.config(text=f"Typing stopped by user (ESC) at char {char_index+1}.")
                break
            pyautogui.typewrite(char)
            if char_delay > 0:
                time.sleep(char_delay)

        if not stop_typing_flag:
            status_label.config(text="Typing complete! 🎉")

    except Exception as e:
        error_msg = f"An error occurred: {e}"
        status_label.config(text=error_msg)
        messagebox.showerror("Runtime Error", error_msg)
        if root_window.state() == 'iconic':
            root_window.after(100, root_window.deiconify)
    finally:
        if KEYBOARD_LIB_AVAILABLE:
            try:
                keyboard.remove_hotkey('esc')
                print("ESC hotkey removed.")
            except Exception as e_hk:
                print(f"Error removing hotkey: {e_hk}")
        stop_typing_flag = False

def start_typing_process():
    code_content = code_area.get("1.0", tk.END).strip()
    initial_delay_val = initial_delay_entry.get()
    char_delay_val = char_delay_entry.get()

    if not code_content:
        messagebox.showwarning("Input Missing", "Please enter some code to type.")
        status_label.config(text="Status: Enter code to type.")
        return

    root.iconify()
    root.after(100, lambda: type_code_from_gui(code_content, initial_delay_val, char_delay_val, status_label, root))

def trim_leading_whitespace_action():
    current_code = code_area.get("1.0", tk.END)
    if not current_code.strip():
        status_label.config(text="Status: Code area is empty. Nothing to trim.")
        return

    lines = current_code.splitlines()
    trimmed_lines = [line.lstrip() for line in lines]
    new_code = "\n".join(trimmed_lines)

    code_area.delete("1.0", tk.END)
    code_area.insert("1.0", new_code)
    
    if not new_code.strip() and current_code.strip():
        status_label.config(text="Status: All lines became empty after trimming.")
    else:
        status_label.config(text="Status: Leading whitespace trimmed successfully.")

if __name__ == "__main__":
    pyautogui.FAILSAFE = True

    root = tk.Tk()
    root.title("AutoTyper GUI 🤖 (Press ESC to Stop)")

    code_frame = tk.Frame(root, padx=10, pady=10)
    code_frame.pack(fill="both", expand=True)

    tk.Label(code_frame, text="Enter Code to Type Below:").pack(anchor="w")

    trim_button = tk.Button(code_frame, text="✂️ Trim Leading Whitespace", command=trim_leading_whitespace_action)
    trim_button.pack(anchor="w", pady=(2, 5))

    code_area = scrolledtext.ScrolledText(code_frame, wrap=tk.WORD, width=60, height=15, font=("Arial", 10))
    code_area.pack(pady=5, fill="both", expand=True)

    delay_frame = tk.Frame(root, padx=10, pady=5)
    delay_frame.pack(fill="x")

    tk.Label(delay_frame, text="Delay Before Typing (s):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    initial_delay_entry = tk.Entry(delay_frame, width=10)
    initial_delay_entry.grid(row=0, column=1, padx=5, pady=5)
    initial_delay_entry.insert(0, "5")

    tk.Label(delay_frame, text="Delay Between Keystrokes (s):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    char_delay_entry = tk.Entry(delay_frame, width=10)
    char_delay_entry.grid(row=1, column=1, padx=5, pady=5)
    char_delay_entry.insert(0, "0")

    action_frame = tk.Frame(root, padx=10, pady=10)
    action_frame.pack(fill="x")

    start_button_text = "🚀 Start Typing"
    if not KEYBOARD_LIB_AVAILABLE:
        start_button_text += " (ESC stop N/A)"

    start_button = tk.Button(action_frame, text=start_button_text, command=start_typing_process, bg="lightblue", font=("Arial", 10, "bold"))
    start_button.pack(pady=5)

    status_label = tk.Label(action_frame, text="Status: Ready", relief=tk.SUNKEN, anchor="w", padx=5)
    status_label.pack(fill="x", pady=5)
    if not KEYBOARD_LIB_AVAILABLE:
        status_label.config(text="Status: Ready ('keyboard' lib not found, ESC stop disabled)")

    def on_closing():
        if KEYBOARD_LIB_AVAILABLE:
            try:
                keyboard.remove_hotkey('esc')
                print("ESC hotkey removed on closing.")
            except Exception:
                pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
