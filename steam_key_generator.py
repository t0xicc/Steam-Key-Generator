import random
import string
import threading
import time
import requests
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from plyer import notification

running = False
valid_keys = 0
tested_keys = 0

def generate_steam_key():
    chars = string.ascii_uppercase + string.digits
    return '-'.join(''.join(random.choice(chars) for _ in range(5)) for _ in range(3))

def send_webhook(webhook_url, key):
    data = {
        "content": f"✅ Valid Steam Key Found: {key}"
    }
    try:
        response = requests.post(webhook_url, json=data)
        return response.status_code in [200, 204]
    except:
        return False

def check_steam_key(key):
    return random.randint(1, 100) == 1  # Simülasyon: %1 geçerli

def save_valid_key(key):
    with open("valid_steam_keys.txt", "a") as f:
        f.write(key + "\n")

def show_notification(title, message):
    notification.notify(title=title, message=message, timeout=4)

def append_to_log(key, is_valid):
    log_text.config(state=NORMAL)
    status = "✅ Valid" if is_valid else "❌ Invalid"
    log_text.insert(END, f"{status}: {key}\n")
    log_text.see(END)
    log_text.config(state=DISABLED)

def update_labels():
    tested_label_var.set(f"Tested: {tested_keys}")
    valid_label_var.set(f"Valid: {valid_keys}")

def worker(webhook_url, delay):
    global running, tested_keys, valid_keys
    while running:
        key = generate_steam_key()
        is_valid = check_steam_key(key)
        tested_keys += 1
        if is_valid:
            valid_keys += 1
            save_valid_key(key)
            append_to_log(key, True)
            if webhook_url:
                send_webhook(webhook_url, key)
            show_notification("Valid Steam Key Found!", key)
        else:
            append_to_log(key, False)
        update_labels()
        time.sleep(delay)

def start_check():
    global running, tested_keys, valid_keys
    if running:
        return
    running = True
    tested_keys = 0
    valid_keys = 0
    webhook_url = webhook_entry.get().strip()
    try:
        delay = float(delay_entry.get())
    except:
        delay = 1.0
    threading.Thread(target=worker, args=(webhook_url, delay), daemon=True).start()
    start_btn.config(state=DISABLED)
    stop_btn.config(state=NORMAL)

def stop_check():
    global running
    running = False
    start_btn.config(state=NORMAL)
    stop_btn.config(state=DISABLED)

def toggle_dark_mode():
    bg = "#2f3136" if dark_mode_var.get() else default_bg
    fg = "white" if dark_mode_var.get() else "black"
    entry_bg = "#40444b" if dark_mode_var.get() else "white"

    root.configure(bg=bg)
    main_frame.configure(bg=bg)
    for widget in main_frame.winfo_children():
        try:
            if isinstance(widget, (Label, Checkbutton)):
                widget.configure(bg=bg, fg=fg)
            elif isinstance(widget, Entry):
                widget.configure(bg=entry_bg, fg=fg, insertbackground=fg)
            elif isinstance(widget, Button):
                widget.configure(bg=bg, fg=fg, activebackground="#7289da" if dark_mode_var.get() else "SystemButtonFace")
        except:
            pass

    log_text.configure(bg=entry_bg, fg=fg, insertbackground=fg)

# GUI
root = Tk()
root.title("Steam Key Checker")

default_bg = root.cget("bg")

main_frame = Frame(root)
main_frame.pack(padx=10, pady=10)

webhook_label = Label(main_frame, text="Discord Webhook (optional):")
webhook_label.grid(row=0, column=0, sticky=W)
webhook_entry = Entry(main_frame, width=50)
webhook_entry.grid(row=0, column=1)

delay_label = Label(main_frame, text="Delay (sec):")
delay_label.grid(row=1, column=0, sticky=W)
delay_entry = Entry(main_frame, width=10)
delay_entry.insert(0, "1.0")
delay_entry.grid(row=1, column=1, sticky=W)

tested_label_var = StringVar(value="Tested: 0")
valid_label_var = StringVar(value="Valid: 0")
tested_label = Label(main_frame, textvariable=tested_label_var)
tested_label.grid(row=2, column=0, sticky=W, pady=5)
valid_label = Label(main_frame, textvariable=valid_label_var)
valid_label.grid(row=2, column=1, sticky=W, pady=5)

log_text = ScrolledText(main_frame, width=60, height=15, state=DISABLED)
log_text.grid(row=3, column=0, columnspan=2, pady=10)

start_btn = Button(main_frame, text="Start", command=start_check)
start_btn.grid(row=4, column=0, sticky=W, pady=5)
stop_btn = Button(main_frame, text="Stop", command=stop_check, state=DISABLED)
stop_btn.grid(row=4, column=1, sticky=E, pady=5)

# Dark mode checkbox
dark_mode_var = BooleanVar()
dark_mode_check = Checkbutton(main_frame, text="Dark Mode", variable=dark_mode_var, command=toggle_dark_mode)
dark_mode_check.grid(row=5, column=0, columnspan=2, pady=5)

root.mainloop()
