#!/usr/bin/python3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox  # Import messagebox correctly
import subprocess as sp
import os

os.environ['PATH'] += os.pathsep + os.path.expanduser('~/.local/bin')

def send_text():
    text = text_box.get("1.0", tk.END).strip()
    tone = tone_var.get()
    wpm = wpm_var.get()

    # Send user-supplied text to C++ program audiocw (needs to be in PATH)
    if text:
        try:
            result = sp.run(['audiocw', text, tone, wpm],
                capture_output=True,
                text=True,
                check=True
            )
        except sp.CalledProcessError as e:
            messagebox.showerror(f"An error occured: {e}")
    else:
        messagebox.showwarning("Warning", "Please enter some text.")

    # Retrieve audio file full path from stdout:
    output = result.stdout.strip()
    audio_path = output.split("AUDIO OUT:")[1].strip().replace('"', '')

    # Play the audio through the speakers:
    try:
        sp.run(['mpv', audio_path])
    except sp.CalledProcessError as e:
        messagebox.showerror(f"An error occured: {e}")

    # Remove audio file:
    try:
        os.remove(audio_path)
    except OSError as e:
        messagebox.showerror(f"An error occured: {e}")


# Create the main window
root = tk.Tk()
root.title("AudioCW - GUI")

# Create a large text box
text_box = tk.Text(root, height=10, width=50)
text_box.pack(pady=10)

# Create a label and drop-down for tone selection
tone_var = tk.StringVar(value=700)
tone_label = tk.Label(root, text="Tone (Hz):")
tone_label.pack()
tone_dropdown = ttk.Combobox(root, textvariable=tone_var)
tone_dropdown['values'] = list(range(300,1800,100))
tone_dropdown.pack(pady=5)

# Create a label and drop-down for WPM selection
wpm_var = tk.StringVar(value=10)
wpm_label = tk.Label(root, text="WPM:")
wpm_label.pack()
wpm_dropdown = ttk.Combobox(root, textvariable=wpm_var)
wpm_dropdown['values'] = (5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100)
wpm_dropdown.pack(pady=5)

# Create an OK button
send_button = tk.Button(root, text="Send", command=send_text)
send_button.pack(pady=20)

# Run the application
root.mainloop()
