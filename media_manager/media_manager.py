#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import getopt
import requests
import ffmpeg
import shutil
import glob


class MediaManager:

    def __init__(self):
        self.media_files = []
        self.media_file_directories = []
        self.media_directory = ""
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

    def clean_media(self, subtitle=False):
        # Iterate through all media files found
        media_file_index = 0
        while media_file_index < len(self.media_files):
            print(f"Validating: {self.media_files[media_file_index]}")
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
                if os.path.isdir(f"{parent_directory}/{self.folder_name}"):
                    for file_name in os.listdir(directory):
                        # construct full file path
                        source = f"{directory}/{file_name}"
                        destination = f"{parent_directory}/{self.folder_name}/{file_name}"
                        # move only files
                        if os.path.isfile(source):
                            shutil.move(source, destination)
                    if os.path.isdir(f"{directory}/Subs"):
                        subtitles = glob.glob(f"{directory}/Subs/*/", recursive = True)
                        for subtitle_directory in subtitles:
                            shutil.move(f"{subtitle_directory}", f"{parent_directory}/{self.folder_name}/Subs")
                        os.rmdir(f"{directory}/Subs")
                        os.rmdir(f"{directory}")
                    self.find_media()
                else:
                    os.rename(f"{directory}", f"{parent_directory}/{self.folder_name}")
                media_file_index = 0
            # Rename file
            new_media_file_path = f"{parent_directory}/{self.folder_name}/{new_file_name}{file_extension}"
            temporary_media_file_path = f"{parent_directory}/{self.folder_name}/temp-{new_file_name}{file_extension}"
            # Check if media file name is the same as what is proposed
            file_name, file_extension = os.path.splitext(media_file)
            if f"{parent_directory}/{self.folder_name}/{file_name}{file_extension}" != f"{new_media_file_path}":
                os.rename(f"{parent_directory}/{self.folder_name}/{file_name}{file_extension}", new_media_file_path)
                media_file_index = 0
            # Clean Subtitle directories
            self.clean_subtitle_directory(subtitle_directory=f"{parent_directory}/{self.folder_name}/Subs")
            # Check if media metadata title is the same as what is proposed
            if "title" in ffmpeg.probe(new_media_file_path)['format']['tags']:
                current_title_metadata = ffmpeg.probe(new_media_file_path)['format']['tags']['title']
            else:
                current_title_metadata = ""
            if current_title_metadata != new_file_name and subtitle is False:
                ffmpeg.input(new_media_file_path) \
                    .output(temporary_media_file_path,
                            map_metadata=0,
                            map=0, vcodec='copy', acodec='copy',
                            **{'metadata:g:0': f"title={new_file_name}", 'metadata:g:1': f"comment={new_file_name}"}) \
                    .overwrite_output() \
                    .run()
                os.remove(new_media_file_path)
                os.rename(temporary_media_file_path, new_media_file_path)
                media_file_index = 0
            elif current_title_metadata != new_file_name and subtitle is True:
                subtitle_file = "English.srt"
                subtitle_files = []
                if series and os.path.isdir(f"{parent_directory}/{self.folder_name}/Subs"):
                    matching_video = 0
                    subtitle_directories = glob.glob(f"{parent_directory}/{self.folder_name}/Subs/*/", recursive=True)
                    subtitle_directories.sort()
                    for subtitle_directory_index in range(0, len(subtitle_directories)):
                        if new_file_name in subtitle_directories[subtitle_directory_index]:
                            matching_video = subtitle_directory_index
                    for file in os.listdir(f"{subtitle_directories[matching_video]}"):
                        if os.path.isfile(file) and (file.endswith("English.srt") or file.endswith("Eng.srt")):
                            subtitle_files.append(os.path.join(subtitle_directories[matching_video], file))
                            subtitle_file = subtitle_files[0]
                elif os.path.isdir(f"{parent_directory}/{self.folder_name}/Subs"):
                    for file in os.listdir(f"{parent_directory}/{self.folder_name}/Subs"):
                        if os.path.isfile(file) and (file.endswith("English.srt") or file.endswith("Eng.srt")):
                            subtitle_files.append(os.path.join(f"{parent_directory}/{self.folder_name}/Subs", file))
                            subtitle_file = subtitle_files[0]
                if file_extension == ".mkv":
                    scodec = "srt"
                elif file_extension == ".mp4":
                    scodec = "mov_text"
                else:
                    scodec = "srt"

                subtitle_exists = False
                for stream in ffmpeg.probe(new_media_file_path)['streams']:
                    if "subtitle" in stream['codec_type']:
                        subtitle_exists = True

                if not subtitle_exists and os.path.isfile(subtitle_file):
                    input_ffmpeg = ffmpeg.input(new_media_file_path)
                    input_ffmpeg_subtitle = ffmpeg.input(subtitle_file)
                    input_subtitles = input_ffmpeg_subtitle['s']
                    ffmpeg.output(
                        input_ffmpeg['v'], input_ffmpeg['a'], input_subtitles, temporary_media_file_path,
                        vcodec='copy', acodec='copy', scodec=scodec,
                        **{'metadata:g:0': f"title={new_file_name}", 'metadata:g:1': f"comment={new_file_name}",
                           'metadata:s:s:0': "language=" + "en", 'metadata:s:s:0': "title=" + "English",
                           'metadata:s:s:1': "language=" + "sp", 'metadata:s:s:1': "title=" + "Spanish"}
                    ).overwrite_output().run()
                    os.remove(new_media_file_path)
                    os.rename(temporary_media_file_path, new_media_file_path)
                elif not subtitle_exists and not os.path.isfile(subtitle_file):
                    ffmpeg.input(new_media_file_path) \
                        .output(temporary_media_file_path,
                                map_metadata=0,
                                map=0, vcodec='copy', acodec='copy',
                                **{'metadata:g:0': f"title={new_file_name}",
                                   'metadata:g:1': f"comment={new_file_name}"}) \
                        .overwrite_output() \
                        .run()
                    os.remove(new_media_file_path)
                    os.rename(temporary_media_file_path, new_media_file_path)
                media_file_index += 1
            else:
                media_file_index += 1
            # Rediscover cleaned media
            self.find_media()

    def find_media(self):
        self.reset_media_list()
        files = glob.glob(f"{self.media_directory}/*", recursive = True)
        files = files + glob.glob(f"{self.media_directory}/*/*", recursive = True)
        files = files + glob.glob(f"{self.media_directory}/*/*/*", recursive=True)
        for file in files:
            if file.endswith(".mp4") or file.endswith(".mkv"):
                self.media_files.append(os.path.join(file))
                self.media_file_directories.append(os.path.dirname(file))
                self.media_file_directories = [*set(self.media_file_directories)]
            elif file.endswith(".nfo") or file.endswith(".txt") or file.endswith(".exe"):
                os.remove(file)
        self.media_files.sort()

    def clean_subtitle_directory(self, subtitle_directory):
        subtitle_directories = glob.glob(f"{subtitle_directory}/*/", recursive = True)
        for subtitle_directory_index in range(0, len(subtitle_directories)):
            subtitle_parent_directory = os.path.dirname(os.path.normpath(subtitle_directories[subtitle_directory_index]))
            subtitle_directory = os.path.basename(os.path.normpath(subtitle_directories[subtitle_directory_index]))
            if os.path.isdir(subtitle_directories[subtitle_directory_index]):
                new_folder_name = subtitle_directory
                for key in self.series_filters:
                    new_folder_name = re.sub(str(key), str(self.series_filters[key]), new_folder_name)
                if new_folder_name != subtitle_directory:
                    os.rename(subtitle_directories[subtitle_directory_index], f"{subtitle_parent_directory}/{new_folder_name}")

    def set_media_directory(self, media_directory):
        self.media_directory = media_directory

    def get_media_list(self):
        return self.media_files

    def get_media_directory_list(self):
        return self.media_file_directories

    def reset_media_list(self):
        self.media_files = []
        self.media_file_directories = []

    def move_media(self, target_directory):
        if os.path.isdir(target_directory):
            for media_directory_index in range(0, len(self.media_file_directories)):
                shutil.move(self.media_file_directories[media_directory_index], target_directory)
        else:
            print(f"Directory {target_directory} does not exist")


def media_manager(argv):
    media_manager_instance = MediaManager()
    move_flag = False
    subtitle_flag = False
    move_directory = "~/Downloads"
    media_directory = "~/Downloads"
    try:
        opts, args = getopt.getopt(argv, "hd:m:s", ["help", "move=",  "directory=", "subtitle"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--directory"):
            media_directory = arg
        elif opt in ("-m", "--move"):
            move_flag = True
            move_directory = arg
        elif opt in ("-s", "--subtitle"):
            subtitle_flag = True

    media_manager_instance.set_media_directory(media_directory=media_directory)
    media_manager_instance.find_media()
    media_manager_instance.clean_media(subtitle=subtitle_flag)

    if move_flag:
        media_manager_instance.move_media(target_directory=move_directory)


def usage():
    print(f'Usage:\n'
          f'-h | --help      [ See usage ]\n'
          f'-d | --directory [ Directory to scan for media ]\n'
          f'-m | --move      [ Directory to move media folders ]\n'
          f'-s | --subtitle  [ Apply subtitle in media Sub folder ]\n'
          f'\n'
          f'media-manager -d "~/Downloads" -m "~/User/Media -s"\n')


def main():
    media_manager(sys.argv[1:])


if __name__ == "__main__":
    media_manager(sys.argv[1:])
