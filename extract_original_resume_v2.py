import docx
import os
import sys

def read_resume(path):
    doc = docx.Document(path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

resume_path = r"c:\Work Space\Resume\Surya_HUB.docx"
try:
    text = read_resume(resume_path)
    # Print with utf-8 encoding to avoid console issues
    sys.stdout.buffer.write(text.encode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
