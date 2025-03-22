import os
import platform
import subprocess
from pathlib2 import Path
import shutil
import re
from jinja2 import Template, Environment, FileSystemLoader

input_fields = {}
special_chars = ['$', '&', '#', '%', '{', '}', '<', '>', '@', '*']
replacement_dict = {char: f'\\{char}' for char in special_chars}


def replace_special_chars(text):
    for char, replacement in replacement_dict.items():
        text = text.replace(char, replacement)
    return text


def replace_all(obj):
    if isinstance(obj, str):
        return replace_special_chars(obj)
    elif isinstance(obj, list):
        return [replace_all(sublist) for sublist in obj]
    elif isinstance(obj, dict):
        return {key: replace_all(value) for key, value in obj.items()}
    return obj


final_template = "final_template.tex"
generated_template = "generated_resume.tex"


def update_resume(folder, data: dict):
    env = Environment(
        loader=FileSystemLoader(folder),
        block_start_string='<<%',
        block_end_string='%>>',
        variable_start_string='<<',
        variable_end_string='>>',
        comment_start_string='<<#',
        comment_end_string='#>>',
    )
    template = env.get_template(final_template)
    data = replace_all(data)
    rendered_tex = template.render(data)

    with open(f"{folder}/{generated_template}", "w", encoding="utf-8") as f:
        f.write(rendered_tex)

    print("Resume LaTeX file generated successfully!")


def export_to_pdf(file, folder):
    tex_filename = file
    filename, ext = os.path.splitext(tex_filename)

    pdf_filename = filename + '.pdf'
    print(pdf_filename)

    result = subprocess.run(['pdflatex', '-interaction=nonstopmode', tex_filename], capture_output=True, text=True,
                            cwd=folder)

    subprocess.run(['open', f"{folder}/{pdf_filename}"])
