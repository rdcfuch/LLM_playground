import base64
from openai import OpenAI
import cv2
from moviepy.editor import VideoFileClip
import time
import base64

import os

os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

# client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

VIDEO_PATH = "/Users/fcfu/Downloads/Peak_test.mov"


def process_video_audio(video_path, seconds_per_frame=3):
    base64Frames = []
    base_video_path, _ = os.path.splitext(video_path)
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * seconds_per_frame)
    curr_frame = 0

    while curr_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        curr_frame += frames_to_skip
    video.release()

    audio_path = f"{base_video_path}.mp3"
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, bitrate="32k")
    clip.audio.close()
    clip.close()

    print(f"Extracted {len(base64Frames)} frames")
    print(f"Extracted audio to {audio_path}")
    return base64Frames, audio_path


# def process_video(video_path, frames_numbers_needed=5):
#     base64Frames = []
#     base_video_path, _ = os.path.splitext(video_path)
#
#     video = cv2.VideoCapture(video_path)
#     total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
#     fps = video.get(cv2.CAP_PROP_FPS)
#     video_time_length = int(total_frames / fps)
#     frames_to_skip = int(fps * video_time_length / frames_numbers_needed)
#
#     curr_frame = 0
#     print(f'Total frames: {total_frames}')
#     print(f'FPS: {fps}')
#
#     while curr_frame < total_frames - 1:
#         video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
#         success, frame = video.read()
#         if not success:
#             break
#         _, buffer = cv2.imencode(".jpg", frame)
#         base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
#         curr_frame += frames_to_skip
#     video.release()
#     #
#     # audio_path = f"{base_video_path}.mp3"
#     # clip = VideoFileClip(video_path)
#     # clip.audio.write_audiofile(audio_path, bitrate="32k")
#     # clip.audio.close()
#     # clip.close()
#
#     print(f"Extracted {len(base64Frames)} frames")
#     # print(f"Extracted audio to {audio_path}")
#     return base64Frames


# base64Frames = process_video(VIDEO_PATH, frames_numbers_needed=5)

print(VIDEO_PATH)

response = client.chat.completions.create(
    model="anas/video-llava:test-v2",
    messages=[
        {"role": "system",
         "content": "You are a professional cinematoghrapher. Please provide a summary of the video. you need to capture some key information from it, including: "
                    "*) camera position: e.g. Aerial, high, low, shoulder,.etc"
                    "*) camera movement: e.g. Pan, Tilt,zoom,.etc"
                    "*) camera moving direction: is the camera moving vertically or horizontally"
                    "*) camera zooming: is the camera zooming in or zooming out"
                    "*) main objects in the video"
                    "*) movement of the main objects in the video"
                    "*) if there are human in the video, how many of them, what are they doing"
                    "*) if there are animals in the video, what animals do they have, what are the animals doing "
                    "give the responses in Markdown."},
        {"role": "user", "content":
            "summerize this video: "+str(VIDEO_PATH)
            # *map(lambda x: {"type": "image_url",
            #                 "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, base64Frames)
         }
    ],
    temperature=0,
)
print(response.choices[0].message.content)
