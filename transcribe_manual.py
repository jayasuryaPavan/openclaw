import google.generativeai as genai
import os
import sys

def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY not found")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    file_path = r"C:\Users\jayas\.openclaw\media\inbound\file_11---56c4da41-66de-478b-afec-b3a1e484a3e0.ogg"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Upload the file
    audio_file = genai.upload_file(path=file_path)
    
    response = model.generate_content([audio_file, "Transcribe this audio. Output only the transcription text."])
    print(response.text)

if __name__ == "__main__":
    main()
