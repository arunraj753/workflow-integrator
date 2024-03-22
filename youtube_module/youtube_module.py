from googleapiclient.discovery import build
import os
import json

youtube_api_key = os.environ.get("YOUTUBE_API_KEY")


class YoutubeModule:

    def __init__(self):
        self.youtube = build("youtube", "v3", developerKey=youtube_api_key)
        self.yt_url_pattern_1 = "https://www.youtube.com/watch?v="
        self.yt_url_pattern_2 = "https://youtu.be/"
        self.yt_url_patterns = [self.yt_url_pattern_1, self.yt_url_pattern_2]
        # self.logger = logger

    def is_youtube_url(self, url):
        for pattern in self.yt_url_patterns:
            if url.startswith(pattern):
                print(f"Identified as YouTube URL : {url}")
                return pattern
        return False

    def analyze_url(self, url: str):
        video_id, play_list_id = None, None
        yt_pattern = self.is_youtube_url(url)
        if not yt_pattern:
            return video_id, play_list_id
        url_split = url.split(yt_pattern)
        if yt_pattern == self.yt_url_pattern_1:
            video_and_playlist = url_split[1].split("&list=")
            video_id = None
            play_list_id = None
            if len(video_and_playlist) == 1:
                video_id = video_and_playlist[0]
            elif len(video_and_playlist) == 2:
                video_id, play_list_id = video_and_playlist
        if yt_pattern == self.yt_url_pattern_2:
            video_id = url_split[1].split("?")[0]
        return video_id, play_list_id

    def get_thumbnail_and_title(self, url):
        video_title, thumbnail_url = None, None
        try:
            video_id, play_list_id = self.analyze_url(url)
            if video_id:
                vid_request = self.youtube.videos().list(part="snippet", id=video_id)
                vid_response = vid_request.execute()
                video_title = vid_response["items"][0]["snippet"]["title"]
                channel_thumbnails = vid_response["items"][0]["snippet"]["thumbnails"]["standard"]
                thumbnail_url = channel_thumbnails["url"]
        except Exception as err:
            print(f"An error occurred while fetching details of {url}. Reason: {err}")

        return video_title, thumbnail_url
