#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import getopt
import requests
import ffmpeg


class MediaManager:

    def __init__(self):
        self.media_files = []
        self.folder_name = ""
        self.movie_filters = {
            f"2160p.*$": f"2160p",
            f"1080p.*$": f"1080p",
            f"720p.*$": f"720p",
            f"480p.*$": f"480p",
            f"ARROW.": f"",
            f"REMASTERED.": f"",
            f"REMASTER.": f"",
            f"RESTORED.": f"",
            f"UNCUT.": f"",
            f"UNRATED.": f"",
            f"EXTENDED.": f"",
            f"PROPER.": f"",
            f"THEATRICAL.": f"",
            f"CRITERION.": f"",
            f"Final.Cut.": f"",
            f"GERMAN": f"German",
            f"SPANISH": f"Spanish",
            f"SWEDISH": f"Swedish",
            f"FRENCH": f"French",
            f"JAPANESE": f"Japanese",
            f"CHINESE": f"Chinese",
            f"KOREAN": f"Korean",
            f"ITALIAN": f"Italian",
            f"RUSSIAN": f"Russian",
            f"\[.*\]": f"",
            f"^ ": f"",
            f"\.": f" ",
        }
        self.series_filters = {
            f"2160p.*$": f"",
            f"1080p.*$": f"",
            f"720p.*$": f"",
            f"480p.*$": f"",
            f"ARROW.": f"",
            f"REMASTERED.": f"",
            f"REMASTER.": f"",
            f"RESTORED.": f"",
            f"UNCUT.": f"",
            f"UNRATED.": f"",
            f"EXTENDED.": f"",
            f"PROPER.": f"",
            f"THEATRICAL.": f"",
            f"CRITERION.": f"",
            f"Final.Cut.": f"",
            f"GERMAN": f"German",
            f"SPANISH": f"Spanish",
            f"SWEDISH": f"Swedish",
            f"FRENCH": f"French",
            f"JAPANESE": f"Japanese",
            f"CHINESE": f"Chinese",
            f"KOREAN": f"Korean",
            f"ITALIAN": f"Italian",
            f"RUSSIAN": f"Russian",
            f"\[.*\]": f"",
            f"^ ": f"",
            f"\.": f" ",
            r"(s[0-9][0-9]*e[0-9][0-9]*).*$": r"- \1",
            r"(S[0-9][0-9]*E[0-9][0-9]*).*$": r"- \1",
            r"s([0-9][0-9]*)e([0-9][0-9]*)": r"S\1E\2",
            r" - -": " -",
        }

        # in_file = ffmpeg.input('input.mp4')
        # overlay_file = ffmpeg.input('overlay.png')(ffmpeg.concat(in_file.trim(start_frame=10, end_frame=20),
        #                                                          in_file.trim(start_frame=30, end_frame=40), ).overlay(
        # overlay_file.hflip()).drawbox(50, 50, 120, 120, color='red', thickness=5).output('out.mp4').run())

    def clean_media(self):
        parent_directory = ""
        # Iterate through all media files found
        for media_file_index in range(0, len(self.media_files)):
            directory = os.path.dirname(self.media_files[media_file_index])
            media_file = os.path.basename(self.media_files[media_file_index])
            file_name, file_extension = os.path.splitext(media_file)
            new_file_name = file_name
            # Detect if series or a movie
            if bool(re.search("S[0-9][0-9]*E[0-9][0-9]*", file_name)) or bool(re.search("s[0-9][0-9]*e[0-9][0-9]*", file_name)):
                filters = self.series_filters
                series = True
            else:
                filters = self.movie_filters
                series = False
            # Clean filename
            for key in filters:
                new_file_name = re.sub(str(key), str(filters[key]), new_file_name)
            # Get folder name for movie or series
            if series:
                self.folder_name = re.sub(" - S[0-9][0-9]*E[0-9][0-9]*", "", new_file_name)
            else:
                self.folder_name = new_file_name
            # Rename directory
            parent_directory = os.path.dirname(os.path.normpath(directory))
            # Check if media folder name is the same as what is proposed
            if f"{directory}" != f"{parent_directory}/{self.folder_name}":
                os.rename(f"{directory}", f"{parent_directory}/{self.folder_name}")
            # Rename file
            new_media_file_path = f"{parent_directory}/{self.folder_name}/{new_file_name}{file_extension}"
            temporary_media_file_path = f"{parent_directory}/{self.folder_name}/temp-{new_file_name}{file_extension}"
            # Check if media file name is the same as what is proposed
            if f"{parent_directory}/{self.folder_name}/{file_name}{file_extension}" != f"{new_media_file_path}":
                os.rename(f"{parent_directory}/{self.folder_name}/{file_name}{file_extension}", new_media_file_path)
            # Check if media metadata title is the same as what is proposed
            current_title_metadata = ffmpeg.probe(new_media_file_path)['format']['tags']['title']
            if current_title_metadata != new_file_name:
                ffmpeg.input(new_media_file_path).output(temporary_media_file_path, metadata=f"title={new_file_name}", map_metadata=0, map=0, codec="copy").overwrite_output().run()
                os.remove(new_media_file_path)
                os.rename(temporary_media_file_path, new_media_file_path)
            # Rediscover cleaned media
            self.find_media(directory=f"{parent_directory}/{self.folder_name}")

    def find_media(self, directory):
        self.reset_media_list()
        for file in os.listdir(directory):
            if file.endswith(".mp4") or file.endswith(".mkv"):
                self.media_files.append(os.path.join(directory, file))
                print(os.path.join(directory, file))

    def reset_media_list(self):
        self.media_files = []

    def subtitle_manager(self, media_file, subtitle_file):
        ffmpeg.input(media_file, srt=subtitle_file, langauage='eng', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(width, height)).output(out_filename, pix_fmt='yuv420p').overwrite_output()

        """
        # MP4
        ffmpeg -i "${file}" -f srt -i "${subtitle_files[0]}" -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=eng "${file::-4}-output.${file_type}"
        # MKV
        ffmpeg -i "${file}" -f srt -i "${subtitle_files[0]}" -c:v copy -c:a copy -c:s srt -metadata:s:s:0 language=eng "${file::-4}-output.${file_type}"
        """


def media_manager(argv):
    media_manager_instance = MediaManager()
    audio_only = False
    try:
        opts, args = getopt.getopt(argv, "hac:d:f:l:", ["help", "audio", "channel=", "directory=", "file=", "links="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-a", "--audio"):
            audio_only = True
        elif opt in ("-c", "--channel"):
            video_downloader_instance.get_channel_videos(arg)
        elif opt in ("-d", "--directory"):
            video_downloader_instance.set_save_path(arg)
        elif opt in ("-f", "--file"):
            video_downloader_instance.open_file(arg)
        elif opt in ("-l", "--links"):
            url_list = arg.split(",")
            for url in url_list:
                video_downloader_instance.append_link(url)

    video_downloader_instance.download_all(audio_only)


def usage():
    print(f'Usage:\n'
          f'-h | --help      [ See usage ]\n'
          f'-a | --audio     [ Download audio only ]\n'
          f'-c | --channel   [ YouTube Channel/User - Downloads all videos ]\n'
          f'-d | --directory [ Location where the images will be saved ]\n'
          f'-f | --file      [ Text file to read the URLs from ]\n'
          f'-l | --links     [ Comma separated URLs (No spaces) ]\n'
          f'\n'
          f'media-manager -f "file_of_urls.txt" -l "URL1,URL2,URL3" -c "WhiteHouse" -d "~/Downloads"\n')


def main():
    media_manager(sys.argv[1:])


if __name__ == "__main__":
    #media_manager(sys.argv[1:])

    media_manager_instance = MediaManager()
    media_manager_instance.find_media(directory="/home/mrdr/Desktop/test")
    media_manager_instance.clean_media()
