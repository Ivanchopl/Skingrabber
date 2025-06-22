import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import requests
import json
import base64
import pyperclip
from io import BytesIO
import webbrowser
import os

def get_uuid(username):
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["id"]
    return None

def get_skin_url(uuid):
    url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for prop in data["properties"]:
            if prop["name"] == "textures":
                texture = json.loads(base64.b64decode(prop["value"]))
                return texture["textures"]["SKIN"]["url"]
    return None

def fetch_skin():
    username = entry.get().strip()
    if not username:
        messagebox.showwarning("Missing Input", "Please enter a Minecraft username.")
        return

    uuid = get_uuid(username)
    if not uuid:
        messagebox.showerror("Error", f"Invalid username: {username}")
        return

    skin_url = get_skin_url(uuid)
    if not skin_url:
        messagebox.showerror("Error", "Skin not found.")
        return

    try:
        response = requests.get(skin_url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).resize((128, 256))
        img_tk = ImageTk.PhotoImage(img)

        skin_label.config(image=img_tk)
        skin_label.image = img_tk
        skin_label.skin_data = img
        skin_label.skin_url = skin_url
        skin_label.skin_name = username

        copy_button.config(state=tk.NORMAL)
        save_button.config(state=tk.NORMAL)
        open_button.config(state=tk.NORMAL)

        # ✅ Auto-save skin to "skins" folder
        save_dir = os.path.join(os.path.dirname(__file__), "skins")
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, f"{username}_skin.png")
        img.save(file_path)
        print(f"[✔] Skin saved to: {file_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Could not load or save skin image.\n\n{str(e)}")

def copy_url():
    if hasattr(skin_label, "skin_url"):
        pyperclip.copy(skin_label.skin_url)
        messagebox.showinfo("Copied", "Skin URL copied to clipboard.")

def save_skin():
    if hasattr(skin_label, "skin_data"):
        file = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile=f"{skin_label.skin_name}_skin.png"
        )
        if file:
            skin_label.skin_data.save(file)
            messagebox.showinfo("Saved", f"Skin saved as:\n{file}")

def open_in_browser():
    if hasattr(skin_label, "skin_url"):
        webbrowser.open(skin_label.skin_url)

# GUI Setup
root = tk.Tk()
root.title("Skin Grabber by Ivanchop")
root.geometry("360x530")
root.configure(bg="#f0f0f0")

# Header
title = tk.Label(root, text="Skin Grabber", font=("Segoe UI", 20, "bold"), bg="#f0f0f0", fg="#333")
subtitle = tk.Label(root, text="(made by Ivanchop)", font=("Segoe UI", 10), bg="#f0f0f0", fg="#555")
title.pack(pady=(10, 0))
subtitle.pack(pady=(0, 15))

# Username input
entry = tk.Entry(root, font=("Segoe UI", 14), justify="center")
entry.pack(pady=5, ipadx=5, ipady=5)

fetch_button = tk.Button(root, text="Grab Skin", font=("Segoe UI", 12), command=fetch_skin, width=20)
fetch_button.pack(pady=10)

# Skin preview placeholder
skin_label = tk.Label(root, text="Skin Preview", bg="#ddd", width=128, height=256)
skin_label.pack(pady=10)

# Action buttons
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=5)

copy_button = tk.Button(button_frame, text="Copy URL", command=copy_url, state=tk.DISABLED, width=12)
save_button = tk.Button(button_frame, text="Save PNG", command=save_skin, state=tk.DISABLED, width=12)
open_button = tk.Button(button_frame, text="Open Browser", command=open_in_browser, state=tk.DISABLED, width=12)

copy_button.grid(row=0, column=0, padx=5, pady=5)
save_button.grid(row=0, column=1, padx=5, pady=5)
open_button.grid(row=0, column=2, padx=5, pady=5)

# Footer
footer = tk.Label(root, text="Built with ❤ in Python", font=("Segoe UI", 8), bg="#f0f0f0", fg="#888")
footer.pack(pady=10)

root.mainloop()
