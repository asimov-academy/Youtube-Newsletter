from faster_whisper import WhisperModel
import ffmpeg
import os
from tinydb import TinyDB, Query
from pytubefix import YouTube
from threading import Thread


whisper_model = WhisperModel("small", 
                                compute_type="int8", 
                                cpu_threads=os.cpu_count(), 
                                num_workers=os.cpu_count())

def download_audios(channel):
    global db
    base_dir = f"audios/{channel}"
    os.makedirs(base_dir, exist_ok=True)
    c_table = db.table(channel)

    actual_audios = [i.split(".wa")[0] for i in os.listdir(base_dir)]
    all_videos = [i["title"] for i in c_table.all()]
    to_download = [i for i in all_videos if i not in actual_audios]

    for video in to_download:  
        print(f"Downloading {video} from {channel}.")
        url = c_table.search(Query().title == video)[0]["url"]
        yt = YouTube(url)

        stream_url = yt.streams[0].url
        audio, err = (
            ffmpeg
            .input(stream_url)
            .output("pipe:", format='wav', 
                    acodec='pcm_s16le', 
                    loglevel="error")  
            .run(capture_stdout=True)
        )

        with open(f'{base_dir}/{video}.wav', 'wb') as f:
            f.write(audio)

        db = TinyDB("youtube_db.json")
        t_table = db.table("t_" + channel)
        video_data = {"title": video,
                   "transcription": "",
                   "resume": ""}
        t_table.insert(video_data)

        t = Thread(target=transcribe_audio, 
                   args=(video, channel)).start()


def transcribe_audio(video, channel):
    db = TinyDB("youtube_db.json")
    t_table = db.table("t_"+channel)
    
    print(f"Transcribing: {video} from {channel}")
    audio_file = f"audios/{channel}/{video}.wav"
    audio_file = open(audio_file, "rb")

    segments, _ = whisper_model.transcribe(audio_file, 
                                           language="pt")
    clean_prompt = "".join(segment.text for 
                           segment in segments).strip()

    t_table.update({"transcription": clean_prompt},
                    Query().title == video)
        


if __name__ == "__main__":
    db = TinyDB("youtube_db.json")
    channels = [i for i in db.tables() 
                if i[:2] != "t_" and i != "channels"]
    
    for channel in channels:
        download_audios(channel)