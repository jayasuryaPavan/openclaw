import docx
import os

def read_resume(path):
    doc = docx.Document(path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

resume_path = r"c:\Work Space\Resume\Surya_HUB.docx"
try:
    print(read_resume(resume_path))
except Exception as e:
    print(f"Error: {e}")
