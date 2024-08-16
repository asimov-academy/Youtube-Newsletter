from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import re
import pandas as pd
import os
import re
import json
from tinydb import TinyDB, Query

# Carrega a YOUTUBE_API_KEY, que deve ser obtida no Google Cloud Platform
load_dotenv()
api_key = os.getenv("YOUTUBE_API_KEY")

# Data para iniciar a análise
cutoff = pd.to_datetime('2024-08-01T00:00:00Z')

# Função que pesquisa o nome de um canal e retorna
# seu channel_id.
def search_channel_by_name(youtube, channel_name):
    request = youtube.search().list(
        part="snippet",
        q=channel_name,
        type="channel",
        maxResults=1
    )
    response = request.execute()
    for item in response.get('items', []):
        return item['snippet']['channelId']
    return None


# Função que recebe um channel_id e retorna
# todos os vídeos
def get_channel_videos(youtube, channel_id, cutoff_date=None):
    video_ids = []
    next_page_token = None

    while True:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,
            order="date",
            type="video",
            pageToken=next_page_token
        )
        response = request.execute()
        videos = response.get('items', [])
        if cutoff_date:
            videos = [video for video in videos if pd.to_datetime(video['snippet']['publishedAt']) > cutoff_date]
        
        video_ids.extend(item['id']['videoId'] for item in videos)

        # Verifica se há mais páginas
        next_page_token = response.get('nextPageToken')
        if not next_page_token or len(videos) == 0:
            break
    return video_ids

# Função que obtem detalhes de um vídeo específico.
def get_video_details(youtube, video_ids):
    videos = []
    for i in range(0, len(video_ids), 50):  # Processar em lotes de 50
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(video_ids[i:i+50])  # Fatiar lista de IDs
        )
        response = request.execute()
        
        for item in response.get('items', []):
            video_data = {
                'videoId': item['id'],
                'title': re.sub(r'[^\w\s]', '', item['snippet']['title']).strip(),
                'description': item['snippet']['description'],
                'publishedAt': item['snippet']['publishedAt'],
                'thumbnail': item['snippet']['thumbnails']['default']['url'],
                'duration': item['contentDetails']['duration'],
                'viewCount': item['statistics'].get('viewCount'),
                'likeCount': item['statistics'].get('likeCount'),
                'commentCount': item['statistics'].get('commentCount'),
                'url': f"https://www.youtube.com/watch?v={item['id']}"
            }
            videos.append(video_data)
    return videos



def main(youtube, channel_name):
    # Vamos organizar estas informações usando
    # um banco de dados NoSQL
    db = TinyDB("youtube_db.json")
    cmap_table = db.table("channels")
    c_table = db.table(channel_name)   
    
    # Busca por um channel ID no banco de dados
    c_map = cmap_table.search(Query().channel == channel_name)
    if len(c_map) == 0:
        channel_id = search_channel_by_name(youtube, channel_name)
        cmap_table.insert({"channel": channel_name,
                        "id": channel_id})
    else:
        channel_id = c_map[0]["id"]  


    # Restringe a busca por vídeos 
    cutoff_date = None
    all_videos = c_table.all()
    if len(all_videos) > 0:
        cutoff_date = max(all_videos, 
                    key=lambda x:x['publishedAt'])["publishedAt"]
        cutoff_date = pd.to_datetime(cutoff_date)
    else:
        cutoff_date = cutoff

    video_ids = get_channel_videos(youtube, channel_id, cutoff_date)
    if video_ids:
        videos = get_video_details(youtube, video_ids)
        for video in videos:
            video["viewCount"] = 0 if video["viewCount"] is None else int(video["viewCount"])
            video["likeCount"] = 0 if video["likeCount"] is None else int(video["likeCount"])
            video["commentCount"] = 0 if video["commentCount"] is None else int(video["commentCount"])
        c_table.insert_multiple(videos)
    else:
        print("No new video found for", channel_name)


if __name__ == "__main__":
    youtube = build('youtube', 'v3', developerKey=api_key)
    with open("canais", 'r', encoding='utf-8') as arquivo:
        channels = [linha.strip() for linha in arquivo.readlines()]
    
    for channel_name in channels:
        print("Analyzing", channel_name)
        main(youtube, channel_name)
