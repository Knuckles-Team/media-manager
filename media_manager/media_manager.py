#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import getopt
import ffmpeg
import shutil
import glob


class MediaManager:

    def __init__(self):
        self.media_files = []
        self.completed_media_files = []
        self.media_file_directories = []
        self.completed_media_file_directories = []
        self.media_directory = ""
        self.directory = ""
        self.parent_directory = ""
        self.folder_name = ""
        self.media_file = ""
        self.file_name = ""
        self.file_extension = ""
        self.new_file_name = ""
        self.new_media_file_path = ""
        self.temporary_media_file_path = ""
        self.quiet = True
        self.movie_filters = {
            f"2160p.*$": f"2160p",
            f"1080p.*$": f"1080p",
            f"720p.*$": f"720p",
            f"480p.*$": f"480p",
            f"ARROW.": f"",
            f"REMASTERED.": f"",
            f"REMASTER.": f"",
            f"REMASTED.": f"",            
            f"RESTORED.": f"",
            f"UNCUT.": f"",
            f"UNRATED.": f"",
            f"EXTENDED.": f"",
            f"IMAX.": f"",
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
            f"REMASTED.": f"",      
            f"RESTORED.": f"",
            f"UNCUT.": f"",
            f"UNRATED.": f"",
            f"EXTENDED.": f"",
            f"IMAX.": f"",
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
        self.filters = self.movie_filters
        self.series = False
        self.subtitle = False
        self.media_file_index = 0

    def set_verbose(self, quiet=True):
        self.quiet = quiet

    def set_subtitle(self, subtitle: bool):
        self.subtitle = subtitle

    def set_media_directory(self, media_directory: str):
        self.media_directory = os.path.normpath(os.path.join(media_directory, ''))
        if not self.media_directory.endswith(os.path.sep):
            self.media_directory += os.path.sep

    def get_media_list(self):
        return self.media_files

    def get_media_directory_list(self):
        return self.media_file_directories

    # Detect if series or a movie
    def media_detection(self):
        self.parent_directory = os.path.dirname(os.path.normpath(self.directory))
        self.folder_name = os.path.basename(os.path.normpath(self.directory))
        if bool(re.search("S[0-9][0-9]*E[0-9][0-9]*", self.file_name)) \
                or bool(re.search("s[0-9][0-9]*e[0-9][0-9]*", self.file_name)):
            self.filters = self.series_filters
            self.series = True
            print(f"\tDetected media type: Series")
        else:
            self.filters = self.movie_filters
            self.series = False
            print(f"\tDetected media type: Media")

    # Clean filename
    def clean_file_name(self):
        for key in self.filters:
            self.new_file_name = re.sub(str(key), str(self.filters[key]), self.new_file_name)

    def verify_parent_directory(self):
        if self.series:
            self.folder_name = re.sub(" - S[0-9]+E[0-9]+", "", self.new_file_name)
        else:
            self.folder_name = self.new_file_name
        # Check if media file does not have it's own folder, and create it if it does not
        # print(f"\tVerifying Media Parent Directory:\n\t\t"
        #       f"Current Directory: {os.path.normpath(os.path.join(self.directory, ''))}\n\t\t"
        #       f"Parent Directory: {os.path.normpath(os.path.join(self.media_directory, self.folder_name, ''))}")
        if os.path.normpath(os.path.join(self.directory, '')) == os.path.normpath(
                os.path.join(self.media_directory, '')):
            # If parent folder does not exist, create it
            self.parent_directory = os.path.normpath(os.path.join(self.media_directory, self.folder_name, ''))
            if not os.path.isdir(os.path.normpath(os.path.join(self.parent_directory))):
                os.makedirs(os.path.join(self.parent_directory, ''))
                print(f"\tCreated new parent directory: {os.path.join(self.parent_directory, '')}")
            for file_name in os.listdir(self.directory):
                if self.folder_name in file_name:
                    # construct full file path
                    source = os.path.normpath(os.path.join(self.directory, file_name))
                    destination = os.path.normpath(os.path.join(self.parent_directory, file_name))
                    # move only files
                    if os.path.isfile(source):
                        shutil.move(source, destination)
                if os.path.isdir(os.path.normpath(os.path.join(self.directory, "Subs"))):
                    subtitles = glob.glob(f"{self.directory}/Subs/*/", recursive=True)
                    for subtitle_directory in subtitles:
                        shutil.move(f"{subtitle_directory}",
                                    os.path.normpath(os.path.join(self.parent_directory, "Subs")))
                    os.rmdir(os.path.normpath(os.path.join(self.directory, "Subs")))
                    os.rmdir(f"{self.directory}")
                print(f"\tMerging parent directories: {os.path.join(self.parent_directory, '')}")
            self.directory = self.parent_directory
            self.parent_directory = os.path.join(self.parent_directory, os.pardir)
        else:
            print(f"\tParent directory already exists: {self.directory}")

    # Rediscover cleaned media
    def find_media(self):
        print("\nScanning for media...")
        self.media_files = []
        files = glob.glob(f"{self.media_directory}/*", recursive=True)
        files = files + glob.glob(f"{self.media_directory}/*/*", recursive=True)
        files = files + glob.glob(f"{self.media_directory}/*/*/*", recursive=True)
        for file in files:
            if file.endswith(".mp4") or file.endswith(".mkv"):
                self.media_files.append(os.path.join(file))
                self.media_file_directories.append(os.path.dirname(file))
                self.media_file_directories = [*set(self.media_file_directories)]
            elif file.endswith(".nfo") or file.endswith(".txt") or file.endswith(".exe"):
                os.remove(file)
        self.media_files.sort()
        for i in self.completed_media_files:
            if i in self.media_files:
                self.media_files.remove(i)
        for i in self.completed_media_file_directories:
            if i in self.media_file_directories:
                self.media_file_directories.remove(i)
        print(f"\tMedia Found! ({len(self.media_file_directories)} files)")

    # Rename file
    def rename_file(self):
        #print("\tRenaming file...")
        old_file_path = os.path.normpath(os.path.join(self.directory,
                                                      f"{self.file_name}{self.file_extension}"))
        self.new_media_file_path = os.path.normpath(os.path.join(self.directory,
                                                                 f"{self.new_file_name}{self.file_extension}"))
        self.temporary_media_file_path = os.path.normpath(
            os.path.join(
                self.directory,
                f"temp-{self.new_file_name}{self.file_extension}"
            )
        )
        # Check if media file name is the same as what is proposed
        self.file_name, self.file_extension = os.path.splitext(self.media_file)
        if old_file_path != f"{self.new_media_file_path}" and os.path.isfile(old_file_path):
            os.rename(old_file_path, self.new_media_file_path)
            self.file_name = self.new_file_name
            self.media_files[self.media_file_index] = self.new_media_file_path
            self.media_file_index = 0
            print(f"\tFile Renamed: {old_file_path} ==> {self.new_media_file_path}")

    # Clean Subtitle directories
    def clean_subtitle_directory(self, subtitle_directory: str):
        subtitle_directories = glob.glob(f"{subtitle_directory}/*/", recursive=True)
        for subtitle_directory_index in range(0, len(subtitle_directories)):
            subtitle_parent_directory = os.path.dirname(
                os.path.normpath(subtitle_directories[subtitle_directory_index]))
            subtitle_directory = os.path.basename(os.path.normpath(subtitle_directories[subtitle_directory_index]))
            if os.path.isdir(subtitle_directories[subtitle_directory_index]):
                new_folder_name = subtitle_directory
                for key in self.series_filters:
                    new_folder_name = re.sub(str(key), str(self.series_filters[key]), new_folder_name)
                if new_folder_name != subtitle_directory:
                    os.rename(subtitle_directories[subtitle_directory_index],
                              os.path.normpath(os.path.join(subtitle_parent_directory, new_folder_name)))

    # Check if media metadata title is the same as what is proposed
    def set_media_metadata(self):
        print(f"\tUpdating metadata for {os.path.basename(self.new_media_file_path)}...")
        if "title" in ffmpeg.probe(self.new_media_file_path)['format']['tags']:
            current_title_metadata = ffmpeg.probe(self.new_media_file_path)['format']['tags']['title']
        else:
            current_title_metadata = ""
        if current_title_metadata != self.new_file_name and self.subtitle is False:
            ffmpeg.input(self.new_media_file_path) \
                .output(self.temporary_media_file_path,
                        map_metadata=0,
                        map=0, vcodec='copy', acodec='copy',
                        **{'metadata:g:0': f"title={self.new_file_name}",
                           'metadata:g:1': f"comment={self.new_file_name}"}) \
                .overwrite_output() \
                .run(quiet=self.quiet)
            os.remove(self.new_media_file_path)
            os.rename(self.temporary_media_file_path, self.new_media_file_path)
            self.media_file_index = 0
        elif current_title_metadata != self.new_file_name and self.subtitle is True:
            subtitle_file = "English.srt"
            subtitle_files = []
            if self.series and os.path.isdir(f"{self.parent_directory}/{self.folder_name}/Subs"):
                matching_video = 0
                subtitle_directories = glob.glob(f"{self.parent_directory}/{self.folder_name}/Subs/*/", recursive=True)
                subtitle_directories.sort()
                for subtitle_directory_index in range(0, len(subtitle_directories)):
                    if self.new_file_name in subtitle_directories[subtitle_directory_index]:
                        matching_video = subtitle_directory_index
                for file in os.listdir(f"{subtitle_directories[matching_video]}"):
                    if os.path.isfile(file) and (file.endswith("English.srt") or file.endswith("Eng.srt")):
                        subtitle_files.append(os.path.join(subtitle_directories[matching_video], file))
                        subtitle_file = subtitle_files[0]
            elif os.path.isdir(os.path.normpath(os.path.join(self.parent_directory, self.folder_name, "Subs", ""))):
                for file in os.listdir(
                        os.path.normpath(os.path.join(self.parent_directory, self.folder_name, "Subs", ""))):
                    if os.path.isfile(file) and (file.endswith("English.srt") or file.endswith("Eng.srt")):
                        subtitle_files.append(
                            os.path.normpath(os.path.join(self.parent_directory, self.folder_name, "Subs", file)))
                        subtitle_file = subtitle_files[0]
            if self.file_extension == ".mkv":
                scodec = "srt"
            elif self.file_extension == ".mp4":
                scodec = "mov_text"
            else:
                scodec = "srt"

            subtitle_exists = False
            for stream in ffmpeg.probe(self.new_media_file_path)['streams']:
                if "subtitle" in stream['codec_type']:
                    subtitle_exists = True

            if not subtitle_exists and os.path.isfile(subtitle_file):
                input_ffmpeg = ffmpeg.input(self.new_media_file_path)
                input_ffmpeg_subtitle = ffmpeg.input(subtitle_file)
                input_subtitles = input_ffmpeg_subtitle['s']
                ffmpeg.output(
                    input_ffmpeg['v'], input_ffmpeg['a'], input_subtitles, self.temporary_media_file_path,
                    vcodec='copy', acodec='copy', scodec=scodec,
                    **{'metadata:g:0': f"title={self.new_file_name}", 'metadata:g:1': f"comment={self.new_file_name}",
                       'metadata:s:s:0': "language=" + "en", 'metadata:s:s:0': "title=" + "English",
                       'metadata:s:s:1': "language=" + "sp", 'metadata:s:s:1': "title=" + "Spanish"}
                ).overwrite_output().run(quiet=self.quiet)
                os.remove(self.new_media_file_path)
                os.rename(self.temporary_media_file_path, self.new_media_file_path)
            elif not subtitle_exists and not os.path.isfile(subtitle_file):
                ffmpeg.input(self.new_media_file_path) \
                    .output(self.temporary_media_file_path,
                            map_metadata=0,
                            map=0, vcodec='copy', acodec='copy',
                            **{'metadata:g:0': f"title={self.new_file_name}",
                               'metadata:g:1': f"comment={self.new_file_name}"}) \
                    .overwrite_output() \
                    .run(quiet=self.quiet)
                os.remove(self.new_media_file_path)
                os.rename(self.temporary_media_file_path, self.new_media_file_path)
            self.media_file_index += 1
        else:
            self.media_file_index += 1
        print(f"\tMetadata Updated: {os.path.basename(self.new_media_file_path)}")

    # Rename directory
    def rename_directory(self):
        if self.series:
            self.folder_name = re.sub(" - S[0-9]+E[0-9]+", "", self.new_file_name)
        else:
            self.folder_name = self.new_file_name
        # self.parent_directory = os.path.dirname(os.path.normpath(self.directory))
        # Check if media folder name is the same as what is proposed
        if os.path.normpath(os.path.join(self.directory, '')) != os.path.normpath(
                os.path.join(self.parent_directory, self.folder_name, '')):
            print(f"\tRenaming directory: {os.path.normpath(os.path.join(self.directory, ''))} ==> "
                  f"{os.path.normpath(os.path.join(self.parent_directory, self.folder_name, ''))}")
            if os.path.isdir(os.path.normpath(os.path.join(self.parent_directory, self.folder_name))):
                for file_name in os.listdir(self.directory):
                    # construct full file path
                    source = os.path.normpath(os.path.join(self.directory, file_name))
                    destination = os.path.normpath(os.path.join(self.parent_directory, self.folder_name, file_name))
                    # move only files
                    if os.path.isfile(source):
                        shutil.move(source, destination)
                if os.path.isdir(os.path.normpath(os.path.join(self.directory, "Subs"))):
                    subtitles = glob.glob(f"{self.directory}/Subs/*/", recursive=True)
                    for subtitle_directory in subtitles:
                        shutil.move(f"{subtitle_directory}", os.path.normpath(os.path.join(self.parent_directory,
                                                                                           self.folder_name,
                                                                                           "Subs")))
                    os.rmdir(os.path.normpath(os.path.join(self.directory, "Subs")))
                os.rmdir(f"{self.directory}")
            else:
                os.rename(os.path.normpath(os.path.join(self.directory, '')),
                          os.path.normpath(os.path.join(self.parent_directory, self.folder_name)))
            self.find_media()
            self.media_file_index = 0
        else:
            print(f"\tRenaming directory not needed: {os.path.normpath(os.path.join(self.directory, ''))}")

    # Cleanup Variables
    def reset_variables(self):
        self.media_file = ""
        self.media_file_index = 0
        self.new_file_name = ""
        self.new_media_file_path = ""
        self.temporary_media_file_path = ""
        self.file_name = ""
        self.file_extension = ""
        self.media_files = []
        self.media_file_directories = []

    # Iterate through all media files found
    def clean_media(self):
        while self.media_file_index < len(self.media_files):
            print(
                f"\nProcessing ({self.media_file_index + 1}/{len(self.media_files)}): "
                f"{self.media_files[self.media_file_index]}")
            self.directory = os.path.normpath(os.path.dirname(self.media_files[self.media_file_index]))
            if not self.directory.endswith(os.path.sep):
                self.directory += os.path.sep
            self.media_file = os.path.basename(self.media_files[self.media_file_index])
            self.file_name, self.file_extension = os.path.splitext(self.media_file)
            self.new_file_name = self.file_name
            self.media_detection()
            self.clean_file_name()
            self.verify_parent_directory()
            self.rename_file()
            self.clean_subtitle_directory(subtitle_directory=f"{self.parent_directory}/{self.folder_name}/Subs")
            self.set_media_metadata()
            self.rename_directory()
            self.completed_media_files.append(self.media_files[self.media_file_index])
            self.completed_media_file_directories.append(self.media_file_directories[self.media_file_index])
        self.reset_variables()

    # Move media to new destination
    def move_media(self, target_directory: str, type="media"):
        if not os.path.isdir(target_directory):
            print(f"\nDirectory {target_directory} does not exist")
            return
        # self.completed_media_files = []
        # self.completed_media_file_directories = []
        #self.find_media()
        print(f"\nMoving {type}...")
        for media_directory_index in range(0, len(self.completed_media_file_directories)):
            # Find if file inside this directory is named as a series
            move = False
            files = glob.glob(f"{self.completed_media_file_directories[media_directory_index]}/*", recursive=True)
            for file in files:
                move = False
                if not os.path.exists(file):
                    continue
                if type == "series" and (bool(re.search("S[0-9][0-9]*E[0-9][0-9]*", file))
                                         or bool(re.search("s[0-9][0-9]*e[0-9][0-9]*", file))):
                    move = True
                    break
                if type == "media" and re.search("S[0-9][0-9]*E[0-9][0-9]*", file) is None \
                        and re.search("s[0-9][0-9]*e[0-9][0-9]*", file) is None:
                    move = True
                    break
            if move:
                if os.path.isdir(
                        os.path.join(
                            target_directory,
                            os.path.basename(self.completed_media_file_directories[media_directory_index])
                        )
                ):
                    print(f"\tMerging {type} ({media_directory_index + 1}/{len(self.completed_media_file_directories)}) "
                          f"{self.completed_media_file_directories[media_directory_index]} to {target_directory}")
                    for file_name in os.listdir(self.completed_media_file_directories[media_directory_index]):
                        # construct full file path
                        source = os.path.normpath(
                            os.path.join(self.completed_media_file_directories[media_directory_index], file_name))
                        destination = os.path.normpath(os.path.join(target_directory, os.path.basename(
                            self.completed_media_file_directories[media_directory_index])))
                        # move only files
                        if os.path.isfile(source):
                            if os.path.isfile(destination):
                                print(f"\t\tFile already exists {destination}, skipping...")
                            else:
                                try:
                                    shutil.move(source, destination)
                                except Exception as e:
                                    print(f"\t\tUnable to move to target directory: {target_directory}]\n\t\t"
                                          f"Error: {e}")
                    if os.path.isdir(
                            os.path.normpath(
                                os.path.join(
                                    self.completed_media_file_directories[media_directory_index],
                                    "Subs")
                            )
                    ):
                        subtitles = glob.glob(f"{self.completed_media_file_directories[media_directory_index]}/Subs/*/",
                                              recursive=True)
                        for subtitle_directory in subtitles:
                            shutil.move(
                                f"{subtitle_directory}",
                                os.path.normpath(
                                    os.path.join(
                                        target_directory,
                                        os.path.basename(self.completed_media_file_directories[media_directory_index]),
                                        "Subs"
                                    )
                                )
                            )
                        shutil.rmtree(
                            os.path.normpath(
                                os.path.join(
                                    self.completed_media_file_directories[media_directory_index],
                                    "Subs"
                                )
                            ), 
                            ignore_errors=True
                        )
                    try:
                        os.rmdir(f"{self.completed_media_file_directories[media_directory_index]}")
                    except OSError:
                        print(f"\t\tSkipping removal of "
                              f"{self.completed_media_file_directories[media_directory_index]}...")
                else:
                    print(f"\tMoving {type}({media_directory_index + 1}/{len(self.completed_media_file_directories)}) "
                          f"{self.completed_media_file_directories[media_directory_index]} to {target_directory}")
                    try:
                        shutil.move(self.completed_media_file_directories[media_directory_index], target_directory)
                    except Exception as e:
                        print(f"\nUnable to move to target directory: {target_directory}]\n\t\tError: {e}")


def media_manager(argv):
    media_manager_instance = MediaManager()
    media_flag = False
    tv_flag = False
    subtitle_flag = False
    tv_directory = os.path.join(os.path.expanduser('~'), "Downloads")
    media_directory = os.path.join(os.path.expanduser('~'), "Downloads")
    source_directory = os.path.join(os.path.expanduser('~'), "Downloads")
    try:
        opts, args = getopt.getopt(argv, "hd:m:t:sv",
                                   ["help", "media-directory=", "tv-directory=", "directory=", "subtitle", "verbose"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--directory"):
            source_directory = arg
        elif opt in ("-m", "--media-directory"):
            media_flag = True
            media_directory = arg
        elif opt in ("-t", "--tv-directory"):
            tv_flag = True
            tv_directory = arg
        elif opt in ("-s", "--subtitle"):
            subtitle_flag = True
        elif opt in ("-v", "--verbose"):
            media_manager_instance.set_verbose(quiet=False)

    media_manager_instance.set_media_directory(media_directory=source_directory)
    media_manager_instance.find_media()
    media_manager_instance.set_subtitle(subtitle=subtitle_flag)
    media_manager_instance.clean_media()

    if tv_flag:
        media_manager_instance.move_media(target_directory=tv_directory, type="series")
    if media_flag:
        media_manager_instance.move_media(target_directory=media_directory, type="media")
    print("Complete!")


def usage():
    print(f'Usage:\n'
          f'-h | --help            [ See usage ]\n'
          f'-d | --directory       [ Directory to scan for media ]\n'
          f'-m | --media-directory [ Directory to move Media ]\n'
          f'-t | --tv-directory    [ Directory to move Series ]\n'
          f'-s | --subtitle        [ Apply subtitle in media Sub folder ]\n'
          f'\n'
          f'media-manager -d "~/Downloads" -m "~/User/Media/Movies" -t "~/User/Media/TV" -s\n')


def main():
    media_manager(sys.argv[1:])


if __name__ == "__main__":
    media_manager(sys.argv[1:])
