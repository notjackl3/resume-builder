import os
import time
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import filedialog, messagebox, Tk, Button

resume_path, job_desc_path, upload_resume_btn, resume_label, upload_job_desc_btn, job_desc_label = None, None, None, None, None, None


def on_drop_resume(event):
    resume_path.set(event.data)
    resume_label.config(bg="#D3D3D3", text="Resume file dropped", state="disabled")
    upload_resume_btn.config(state="disabled")  # Disable upload button after drop


def generate_resume():
    try:
        if resume_path.get() and job_desc_label.get("1.0", "end-1c").strip():
            global job_desc_file
            job_desc_file = get_job_description_text().strip()
            root.withdraw()
            root.quit()
            root.destroy()
        else:
            print("Both files need to be dropped before generating.")
    except Exception as e:
        print(e)


def undo_drop_resume():
    try:
        resume_path.set("")
        resume_label.config(bg="white", text="Drag and drop\nResume file here", state="normal")
        upload_resume_btn.config(state="normal")
    except Exception as e:
        print(e)


def upload_resume():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf"), ("Text Files", "*.txt")])
    if file_path:
        resume_path.set(file_path)
        resume_label.config(bg="#D3D3D3", text="Resume file uploaded", state="disabled")
        upload_resume_btn.config(state="disabled")


def drop_all():
    undo_drop_resume()


def upload_job_description():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf"), ("Text Files", "*.txt")])
    if file_path:
        file_path = file_path.strip("{}")
        job_desc_path.set(file_path)
        upload_job_desc_btn.config(state="disabled")


def get_job_description_text():
    return job_desc_label.get("1.0", "end-1c").strip()


def on_call():
    global root, resume_path, job_desc_path, upload_resume_btn, resume_label, upload_job_desc_btn, job_desc_label

    root = TkinterDnD.Tk()  # Create the root window

    root.title("Resume Builder")
    root.configure(bg="#ADD8E6")

    # Initialize StringVars after creating the root window
    resume_path = tk.StringVar(root)
    job_desc_path = tk.StringVar(root)

    frame = tk.Frame(root, bg="#ADD8E6")
    frame.pack(pady=10)

    button_frame = tk.Frame(root, bg="#ADD8E6")
    button_frame.pack(pady=10)

    upload_resume_btn = tk.Button(frame, text="Upload Resume", command=upload_resume, bg="#D3D3D3", relief="flat", highlightbackground="#ADD8E6")
    upload_resume_btn.grid(row=0, column=0, pady=5)

    resume_label = tk.Label(frame, text="Drag and drop\nResume file here", relief="solid", width=30, height=15, bd=1, bg="white")
    resume_label.grid(row=1, column=0, padx=10)
    resume_label.drop_target_register(DND_FILES)
    resume_label.dnd_bind('<<Drop>>', on_drop_resume)

    upload_job_desc_btn = tk.Button(frame, text="Upload Job Description", command=upload_job_description, bg="#D3D3D3", relief="flat", highlightbackground="#ADD8E6")
    upload_job_desc_btn.grid(row=0, column=1, pady=5)

    job_desc_label = tk.Text(frame, wrap="word", width=30, height=15, bd=1, bg="white")
    job_desc_label.grid(row=1, column=1, padx=10)

    generate_btn = tk.Button(button_frame, text="Generate Resume", command=generate_resume, relief="flat", highlightbackground="#ADD8E6")
    generate_btn.grid(row=0, column=0, padx=0)

    drop_all_btn = tk.Button(button_frame, text="Drop Files", command=drop_all, relief="flat", highlightbackground="#ADD8E6")
    drop_all_btn.grid(row=0, column=1, padx=0)

    button_frame.configure(bg="#ADD8E6")

    root.mainloop()  # Start the event loop for the main window

    resume_file = resume_path.get()
    resume_file = resume_file.strip("{}")

    return resume_file, job_desc_file


def notify():
    root = tk.Tk()
    root.title("Notification")
    root.resizable(False, False)
    window_width = 300
    window_height = 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_x = (screen_width - window_width) // 2
    position_y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
    msg_label = tk.Label(root, text="Resume Generated!", font=("Arial", 20))
    msg_label.pack(expand=True, pady=20)
    root.mainloop()


# Main entry point for the program
if __name__ == "__main__":
    # Call the on_call function from the main script
    resume_file, job_desc_file = on_call()
    print(f"Resume File: {resume_file}")
    print(f"Job Description File: {job_desc_file}")
