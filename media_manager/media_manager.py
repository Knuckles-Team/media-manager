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
        self.download_directory = f'{os.path.expanduser("~")}/Downloads'
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
            r"s([0-9][0-9]*)e([0-9][0-9]*)": r"S\1E\2"
        }

        # in_file = ffmpeg.input('input.mp4')
        # overlay_file = ffmpeg.input('overlay.png')(ffmpeg.concat(in_file.trim(start_frame=10, end_frame=20),
        #                                                          in_file.trim(start_frame=30, end_frame=40), ).overlay(
        # overlay_file.hflip()).drawbox(50, 50, 120, 120, color='red', thickness=5).output('out.mp4').run())

    def clean_media(self):
        parent_directory = ""
        for media_file_path in self.media_files:
            directory = os.path.dirname(media_file_path)
            media_file = os.path.basename(media_file_path)
            file_name, file_extension = os.path.splitext(media_file)

            if bool(re.search("S[0-9][0-9]*E[0-9][0-9]*", file_name)) or bool(re.search("s[0-9][0-9]*e[0-9][0-9]*", file_name)):
                filters = self.series_filters
                series = True
                print("Series is True")
            else:
                filters = self.movie_filters
                series = False
                print("Series is False")

            new_file_name = file_name
            for key in filters:
                new_file_name = re.sub(str(key), str(filters[key]), new_file_name)
                print(f"FILENAME: {new_file_name}")

            if series:
                self.folder_name = re.sub(" - S[0-9][0-9]*E[0-9][0-9]*", "", new_file_name)
                print(f"SERIES NAME: {self.folder_name}")
            else:
                self.folder_name = new_file_name
                print(f"FOLDER NAME: {self.folder_name}")
            print(f"Directory: {directory} - Filename: {new_file_name} - Extension: {file_extension}")
            # Rename directory
            parent_directory = os.path.dirname(os.path.normpath(directory))
            os.rename(f"{directory}", f"{parent_directory}/{self.folder_name}")
            # Rename file
            new_media_file_path = f"{parent_directory}/{self.folder_name}/{new_file_name}{file_extension}"
            os.rename(f"{parent_directory}/{self.folder_name}/{file_name}{file_extension}", new_media_file_path)

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

    def set_save_path(self, download_directory):
        self.download_directory = download_directory
        self.download_directory = self.download_directory.replace(os.sep, '/')


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
    media_manager_instance.find_media(directory="/home/mrdr/Desktop/Vincenzo")
    #media_manager_instance.clean_media()
