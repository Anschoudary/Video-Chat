
import os
import time
import tempfile
import streamlit as st
from pathlib import Path
import google.generativeai as genai
genai.configure(api_key="YOUR-GOOGLE-API-KEY")

def model_setup():
    st.write("Setting up model...")
  # Setting parameters for model
    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
    }

    # getting the model
    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    )

    return model

# upload file to gemini (large files are necessarily to upload for processing)
def upload_to_gemini(path, mime_type=None):
  file = genai.upload_file(path, mime_type=mime_type)
  st.write(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

# check files after uploading
def wait_for_files_active(files):
  st.write("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  st.write("...all files ready")

def main():

    model = model_setup()
    paths = ""
    files = ""
    paths = st.text_input("Upload a video file: ")

    if paths != "":
        try:
            files = [
            upload_to_gemini(paths, mime_type="video/mp4"),
            ]
            wait_for_files_active(files)

        except Exception as e:
            st.write("Something went wrong!")

    if files != "":
        chat_session = model.start_chat(
        history=[
            {
            "role": "user",
            "parts": [
                files[0],
            ],
            },
        ]
        )

        # chat loop
        st.write("Enter 'exit' to exit the chat")
        chat = 'Hi'
        while(chat != 'exit'):
            response = chat_session.send_message(chat)
            st.write(response.text)
            chat = st.text_input(">> ")

if __name__ == "__main__":
  main()