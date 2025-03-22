import os
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
import subprocess
from tkinter import filedialog
from manager.main import run


def on_drop_resume(event):
    resume_path.set(event.data)
    resume_label.config(bg="#D3D3D3", text="Resume file dropped", state="disabled")
    upload_resume_btn.config(state="disabled")  # Disable upload button after drop


def on_drop_job_description(event):
    job_desc_path.set(event.data)
    job_desc_label.config(bg="#D3D3D3", text="Job Description file dropped", state="disabled")
    upload_job_desc_btn.config(state="disabled")  # Disable upload button after drop


def run_other_script():
    resume_file = resume_path.get()
    job_desc_file = job_desc_path.get()
    resume_file = resume_file.strip("{}")
    job_desc_file = job_desc_file.strip("{}")
    if resume_file and job_desc_file:
        print(resume_file)
        print(job_desc_file)
        run(resume_file, job_desc_file)
    else:
        print("Both files need to be dropped before generating!")


def undo_drop_resume():
    resume_path.set("")
    resume_label.config(bg="white", text="Drag and drop\nResume file here", state="normal")
    upload_resume_btn.config(state="normal")


def undo_drop_job_description():
    job_desc_path.set("")
    job_desc_label.config(bg="white", text="Drag and drop\nJob Description file here", state="normal")
    upload_job_desc_btn.config(state="normal")


def upload_resume():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf"), ("Text Files", "*.txt")])
    if file_path:
        resume_path.set(file_path)
        resume_label.config(bg="#D3D3D3", text="Resume file uploaded", state="disabled")
        upload_resume_btn.config(state="disabled")


def upload_job_description():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf"), ("Text Files", "*.txt")])
    if file_path:
        file_path = file_path.strip("{}")
        job_desc_path.set(file_path)
        job_desc_label.config(bg="#D3D3D3", text="Job Description file uploaded", state="disabled")
        upload_job_desc_btn.config(state="disabled")


def drop_all():
    undo_drop_resume()
    undo_drop_job_description()


# Initialize main window
root = TkinterDnD.Tk()
root.title("Drag and Drop Example")

root.configure(bg="#ADD8E6")

resume_path = tk.StringVar()
job_desc_path = tk.StringVar()

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

job_desc_label = tk.Label(frame, text="Drag and drop\nJob Description file here", relief="solid", width=30, height=15, bd=1, bg="white")
job_desc_label.grid(row=1, column=1, padx=10)
job_desc_label.drop_target_register(DND_FILES)
job_desc_label.dnd_bind('<<Drop>>', on_drop_job_description)

generate_btn = tk.Button(button_frame, text="Generate Resume", command=run_other_script, relief="flat", highlightbackground="#ADD8E6")
generate_btn.grid(row=0, column=0, padx=0)

drop_all_btn = tk.Button(button_frame, text="Drop Files", command=drop_all, relief="flat", highlightbackground="#ADD8E6")
drop_all_btn.grid(row=0, column=1, padx=0)

button_frame.configure(bg="#ADD8E6")

root.mainloop()
