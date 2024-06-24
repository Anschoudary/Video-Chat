
import os
import time
import google.generativeai as genai
genai.configure(api_key="YOUR-GOOGLE-API-KEY")

# upload file to gemini (large files are necessarily to upload for processing)
def upload_to_gemini(path, mime_type=None):
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

# check files after uploading
def wait_for_files_active(files):
  print("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      time.sleep(10)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  print("...all files ready")
  print()

# Setting parameters for model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

print("Loading Model...")
# getting the model
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)
paths = input("Enter file path: ")
paths = os.fspath(paths)
# get file path
try:
  files = [
  upload_to_gemini(paths, mime_type="video/mp4"),
  ]
except:
  print("File not found!")

wait_for_files_active(files)

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

conversation = open("conversation.txt", "a")
user = ""
bot = ""
# chat loop
print("Enter 'exit' to exit the chat")
chat = 'Hi'
while(chat != 'exit'):

  user = "user: " + chat + "\n"
  conversation.write(user)
  response = chat_session.send_message(chat)
  print(response.text)
  bot = "Bot: " + response.text + "\n"
  conversation.write(bot)
  chat = input(">> ")

conversation.close()