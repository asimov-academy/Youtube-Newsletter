# Para criar o resumo das transcrições
# utilizei um Agent criando no Langflow

# Youtube_Resumer.json

# Para editá-lo, basta instalar o LangFlow e abrir 
# o arquivo por lá, atualizando depois este script abaixo.


from langflow.load import run_flow_from_json
import os
from tinydb import TinyDB, Query
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

final_path = ""
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPEN_API_KEY")

def resume_video(video_transcription, video_name, channel):
    TWEAKS = {
  "ChatInput-wHJjj": {
    "files": "",
    "input_value": video_transcription,
    "sender": "User",
    "sender_name": "User",
    "session_id": "",
    "store_message": True
  },
  "Prompt-OLGmh": {
    "template": "You are an AI helping a user in resuming Youtube videos for him, so he will decide if should watch it or not. \nAnswer only in Portuguese and format you message in Markdown format.\nYou will recieve the video name and the \nvideo's transcription and need to answer with a paragraph about it.\n\nUse the following format:\n*Vídeo:* [Video name]\n*Canal:* [Video name]\n*Resumo:* [Explaining what this video is about]\n\n\nVideo name: {video_name}\nVideo name: {channel_name}\nVideo Transcript: {user_input}\n\nAnswer (in Portuguese): ",
    "user_input": "",
    "video_name": "",
    "channel_name": ""
  },
  "ChatOutput-fxhSA": {
    "data_template": "{text}",
    "input_value": "",
    "sender": "Machine",
    "sender_name": "AI",
    "session_id": "",
    "store_message": True
  },
  "GroqModel-aj41X": {
    "groq_api_base": "https://api.groq.com",
    "groq_api_key": groq_api_key,
    "input_value": "",
    "max_tokens": None,
    "model_name": "llama-3.1-8b-instant",
    "n": None,
    "stream": False,
    "system_message": "",
    "temperature": 0.1
  },
  "TextInput-lngfO": {
    "input_value": video_name
  },
  "OpenAIModel-Q4AFX": {
    "api_key": openai_api_key,
    "input_value": "",
    "json_mode": False,
    "max_tokens": None,
    "model_kwargs": {},
    "model_name": "gpt-4o-mini",
    "openai_api_base": "",
    "output_schema": {},
    "seed": 1,
    "stream": False,
    "system_message": "",
    "temperature": 0.1
  },
  "TextInput-D563R": {
    "input_value": channel
  }
}

    result = run_flow_from_json(flow="Youtube Resumer.json",
                                input_value="message",
                                fallback_to_env_vars=True, # False by default
                                tweaks=TWEAKS)
    return result[0].outputs[0].results["message"].data["text"]
    

if __name__ == "__main__":
    db = TinyDB("youtube_db.json")
    
    with open("canais", 'r', encoding='utf-8') as arquivo:
        channels = [linha.strip() for linha in arquivo.readlines()]
    
    # channel = channels[0]
    for channel in channels:
        db = TinyDB("youtube_db.json")
        t_table = db.table(f"t_{channel}")
        c_table = db.table(f"{channel}")

        resume_videos = [i["title"] for i in t_table.search(Query().resume=="" and 
                                                            Query().transcription!="")]

        for video in resume_videos:
            print(f"Working on {video} from {channel}")
            video_transcription = t_table.search(Query().title==video)[0]["transcription"]

            post_date = c_table.search(Query().title==video)[0]["publishedAt"]
            post_date = post_date.split("T")[0]

            with open(f"{final_path}{post_date}.md", "a") as news_md:
                result = resume_video(video_transcription, video, channel)
                t_table.update({"resume": result},
                        Query().title == video)
                news_md.write(result)
                news_md.write("\n\n")
            # print(result)
            

 
