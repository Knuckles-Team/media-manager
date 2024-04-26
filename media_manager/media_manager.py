#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import getopt
from typing import Optional, List

import ffmpeg
import shutil
import glob
import json
from media_manager.version import __version__, __author__, __credits__

try:
    import music_tag
    from shazamio import Shazam
    import asyncio
    from urllib.request import urlopen

    music_feature = True
except (ModuleNotFoundError, ImportError) as e:
    print("Music managing disabled")
    music_feature = False


class MediaManager:
    """
    Class for managing media files.

    Attributes:
    - media_files: List of media files.
    - completed_media_files: List of completed media files.
    - media_file_directories: List of media file directories.
    - media_directory: Media directory path.
    - directory: Current directory.
    - parent_directory: Parent directory.
    - folder_name: Folder name.
    - media_file: Media file name.
    - file_name: File name.
    - file_extension: File extension.
    - new_file_name: New file name.
    - new_media_file_path: New media file path.
    - temporary_media_file_path: Temporary media file path.
    - quiet: Flag indicating whether to print output.
    - total_media_files: Total number of media files.
    - movie_filters: Dictionary of movie filters.
    - series_filters: Dictionary of series filters.
    - filters: Current set of filters.
    - media_type: Type of media ('media', 'series', 'music').
    - subtitle: Flag indicating whether to include subtitles.
    - optimize: Flag indicating whether to optimize media files.
    - media_file_index: Index of the current media file.
    - audio_tags: Tags for audio files.
    - terminal_width: Width of the terminal.
    - max_file_length: Maximum file length for display.
    - shazam: Shazam instance.
    - supported_audio_types: List of supported audio types.
    - supported_video_types: List of supported video types.
    - video_codec: Video codec for optimization.
    - audio_codec: Audio codec for optimization.
    - output_parameters: Output parameters for media processing.
    - preset: Optimization preset.
    - audio_bitrate: Audio bitrate for optimization.
    - crf: Constant Rate Factor for optimization.
    """

    def __init__(self):
        """
        Initialize the MediaManager class with default values.
        """
        self.media_files = []
        self.completed_media_files = []
        self.media_file_directories = []
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
        self.total_media_files = 0
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
        self.media_type = "media"
        self.subtitle = False
        self.optimize = False
        self.media_file_index = 0
        self.audio_tags = None
        try:
            columns, rows = os.get_terminal_size(0)
        except Exception as e:
            columns = 50
        self.terminal_width = columns
        self.max_file_length = self.terminal_width - 21
        if music_feature:
            self.shazam = Shazam()
        else:
            self.shazam = None
        self.supported_audio_types = ['mp3', 'm4a', 'flac', 'aac', 'aiff', 'dsf', 'ogg', 'opus', 'wav', 'wv']
        self.supported_video_types = ['mp4', 'mkv']
        self.video_codec = "copy"
        self.audio_codec = "copy"
        self.subtitle_codec = "copy"
        self.output_parameters = {}
        self.preset = "medium"
        self.audio_bitrate = '128k'
        self.crf = 28

    def set_verbose(self, quiet=True) -> None:
        """
        Set the verbosity level.

        Args:
        - quiet (bool): Flag indicating whether to print output.
        """
        self.quiet = quiet

    def set_subtitle(self, subtitle: bool) -> None:
        """
        Set the subtitle flag.

        Args:
        - subtitle (bool): Flag indicating whether to include subtitles.
        """
        self.subtitle = subtitle

    def set_optimize(self, optimize: bool) -> None:
        """
        Set the optimization flag.

        Args:
        - optimize (bool): Flag indicating whether to optimize media files.
        """
        self.optimize = optimize
        if self.optimize:
            self.video_codec = "libx265"
            self.audio_codec = "aac"
            self.subtitle_codec = "copy"
            self.output_parameters['crf'] = self.crf
            self.output_parameters['audio_bitrate'] = self.audio_bitrate
            self.output_parameters['preset'] = self.preset
        else:
            self.video_codec = "copy"
            self.audio_codec = "copy"
            self.subtitle_codec = "copy"
            self.output_parameters.pop('crf', None)
            self.output_parameters.pop('audio_bitrate', None)
            self.output_parameters.pop('preset', None)

    def build_output_parameters(self) -> None:
        """
        Build output parameters for media processing.
        """
        self.output_parameters = {
            'map_metadata': 0,
            'map': 0,
            'vcodec': self.video_codec,
            'acodec': self.audio_codec,
            'scodec': self.subtitle_codec,
            'metadata:g:0': f"title={self.new_file_name}",
            'metadata:g:1': f"comment={self.new_file_name}"
        }

    def set_crf(self, crf) -> None:
        """
        Set the Constant Rate Factor (CRF) for optimization.

        Args:
        - crf: Constant Rate Factor value.
        """
        self.crf = crf

    def set_preset(self, preset) -> None:
        """
        Set the optimization preset.

        Args:
        - preset: Optimization preset.
        """
        self.preset = preset

    def set_audio_bitrate(self, audio_bitrate) -> None:
        """
        Set the audio bitrate for optimization.

        Args:
        - audio_bitrate: Audio bitrate value.
        """
        self.audio_bitrate = audio_bitrate

    def set_media_directory(self, media_directory: str) -> None:
        """
        Set the media directory.

        Args:
        - media_directory (str): Media directory path.
        """
        self.media_directory = os.path.normpath(os.path.join(media_directory, ''))
        if not self.media_directory.endswith(os.path.sep):
            self.media_directory += os.path.sep

    def get_media_list(self) -> List[str]:
        """
        Get the list of media files.

        Returns:
        - List of media files.
        """
        return self.media_files

    def get_media_directory_list(self) -> List[str]:
        """
        Get the list of media file directories.

        Returns:
        - List of media file directories.
        """
        return self.media_file_directories

    def print(self, string: str, quiet: Optional[bool], end: Optional[str] = "\n") -> None:
        """
        Print a string.

        Args:
        - string: String to print.
        - end: Ending character for print statement.
        """
        if self.quiet is False or quiet is False:
            print(string, end=end)

    # Detect if series or a movie
    def media_detection(self) -> None:
        """
        Detect the type of media (series, movie, or music).
        """
        self.parent_directory = os.path.dirname(os.path.normpath(self.directory))
        self.folder_name = os.path.basename(os.path.normpath(self.directory))
        if self.file_extension[1:] in self.supported_audio_types and music_feature:
            self.media_type = "music"
            self.audio_tags = None
            try:
                self.audio_tags = music_tag.load_file(os.path.normpath(os.path.join(self.directory, self.media_file)))
            except Exception as e:
                print(f"Unable to open file {os.path.normpath(os.path.join(self.directory, self.media_file))}: \n"
                      f"{e}...\n\n"
                      f"Trying new File Path: {self.new_media_file_path}...")
                try:
                    self.audio_tags = music_tag.load_file(self.new_media_file_path)
                except Exception as e2:
                    print(f"Unable to open new file path: {e2}")
            if not self.audio_tags:
                print("Audio file was not loaded")
                sys.exit(2)
            self.print(f"\tDetected media type: Music")
        elif self.file_extension[1:] in self.supported_video_types:
            if bool(re.search("S[0-9][0-9]*E[0-9][0-9]*", self.file_name)) \
                    or bool(re.search("s[0-9][0-9]*e[0-9][0-9]*", self.file_name)):
                self.filters = self.series_filters
                self.media_type = "series"
                self.print(f"\tDetected media type: Series")
            else:
                self.filters = self.movie_filters
                self.media_type = "media"
                self.print(f"\tDetected media type: Media")

    # Clean filename
    def clean_file_name(self) -> None:
        """
        Clean the file name using specified filters.
        """
        for key in self.filters:
            self.new_file_name = re.sub(str(key), str(self.filters[key]), self.new_file_name)

    def verify_parent_directory(self) -> None:
        """
        Verify and update the parent directory.
        """
        if self.media_type == "series":
            self.folder_name = re.sub(" - S[0-9]+E[0-9]+", "", self.new_file_name)
        elif self.media_type == "media":
            self.folder_name = self.new_file_name
        elif self.media_type == "music":
            if self.audio_tags['artist'].value:
                self.folder_name = self.audio_tags['artist'].value

        # Check if media file does not have it's own folder, and create it if it does not
        self.print(f"\tVerifying Media Parent Directory:\n\t\t"
                   f"Current Directory: {os.path.normpath(os.path.join(self.directory, ''))}\n\t\t"
                   f"Parent Directory: {os.path.normpath(os.path.join(self.media_directory, self.folder_name, ''))}")
        if os.path.normpath(os.path.join(self.directory, '')) == os.path.normpath(
                os.path.join(self.media_directory, '')):
            # If parent folder does not exist, create it
            self.parent_directory = os.path.normpath(os.path.join(self.media_directory, self.folder_name, ''))
            if not os.path.isdir(os.path.normpath(os.path.join(self.parent_directory))):
                os.makedirs(os.path.join(self.parent_directory, ''))
                self.print(f"\tCreated new parent directory: {os.path.join(self.parent_directory, '')}")
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
                self.print(f"\tMerging parent directories: {os.path.join(self.parent_directory, '')}")
            self.directory = self.parent_directory
            self.new_media_file_path = os.path.normpath(
                os.path.join(
                    self.directory,
                    f"{self.new_file_name}{self.file_extension}"))
            self.media_file = self.new_media_file_path
            print(f"New Media Path: {self.new_media_file_path}")
            self.parent_directory = os.path.join(self.parent_directory, os.pardir)
        else:
            self.print(f"\tParent directory already exists: {self.directory}")

    # Rediscover cleaned media
    def find_media(self) -> None:
        """
        Scan for media files in the media directory.
        """
        self.print("\nScanning for media...")
        # Check if running first time to capture the initial total of all files processed
        # (To calculate percentage complete)
        total_media = False
        if not self.media_files:
            total_media = True
            self.total_media_files = 0
        self.media_files = []
        files = glob.glob(f"{self.media_directory}/*", recursive=True)
        files = files + glob.glob(f"{self.media_directory}/*/*", recursive=True)
        files = files + glob.glob(f"{self.media_directory}/*/*/*", recursive=True)
        for file in files:
            file_name, file_extension = os.path.splitext(file)
            if file_extension[1:] in self.supported_video_types or file_extension[1:] in self.supported_audio_types:
                self.media_files.append(os.path.join(file))
                self.media_file_directories.append(os.path.dirname(file))
                self.media_file_directories = [*set(self.media_file_directories)]
            elif file.endswith(".nfo") or file.endswith(".exe"):
                os.remove(file)
        self.media_files.sort()
        for i in self.completed_media_files:
            # print(f"\t\tVerifying completed: {i}")
            if i in self.media_files:
                # print(f"\t\tRemoving completed: {i}")
                self.media_files.remove(i)
        if not self.quiet:
            self.print(
                f"Completed({len(self.completed_media_files)}): {self.completed_media_files}\n"
                f"Detected Remaining({len(self.media_files)}): {self.media_files}")
        if total_media:
            self.total_media_files = len(self.media_files)
        self.print(f"\tMedia Found! ({len(self.media_file_directories)} files)")

    def rename_file(self) -> None:
        """
        Rename the media file based on the cleaned file name.
        """
        self.print("\tRenaming file...")
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
            self.print(f"\tFile Renamed: \n\t\t{old_file_path} \n\t\t➜ \n\t\t{self.new_media_file_path}")

    # Clean Subtitle directories
    def clean_subtitle_directory(self, subtitle_directory: str) -> None:
        """
        Clean subtitle directories.

        Args:
        - subtitle_directory (str): Path to the subtitle directory.
        """

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

    def set_media_metadata(self) -> None:
        """
        Set metadata for the media file.
        """
        if self.media_type == "series" or self.media_type == "media":
            self.set_video_metadata()
        elif self.media_type == "music":
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.set_audio_metadata())

    async def set_audio_metadata(self) -> None:
        """
        Set audio metadata for the media file.
        """
        self.print(f"\tUpdating metadata for {os.path.basename(self.media_file)}...")
        try:
            print("\t", self.audio_tags['artwork'])
            artwork_present = True
        except KeyError:
            artwork_present = False
        # First check if artist - title format matches and if album art exists
        if artwork_present \
                and self.audio_tags['artist'].first == self.media_file.split('-')[0].strip() \
                and f"{self.audio_tags['tracktitle'].first}{self.file_extension}" == self.media_file.split('-')[
            1].strip():
            print("File metadata is already set, moving on...")
            self.media_file_index += 1
            return

        print(f"\t⚡ Shazam ⚡ {self.media_file}...")
        song = await self.shazam.recognize_song(os.path.normpath(os.path.join(self.directory, self.media_file)))
        with open(f"{song['track']['subtitle']} - {song['track']['title']}.json", "w") as outfile:
            outfile.write(json.dumps(song, indent=4))
        self.audio_tags['tracktitle'] = song['track']['title']
        self.audio_tags['albumartist'] = song['track']['subtitle']
        self.audio_tags['artist'] = song['track']['subtitle']
        self.audio_tags['album'] = song['track']['sections'][0]['metadata'][0]['text']
        self.audio_tags['year'] = song['track']['sections'][0]['metadata'][2]['text']
        try:
            self.audio_tags['lyrics'] = song['track']['sections'][1]['text']
            self.audio_tags['comment'] = song['track']['sections'][1]['text']
        except KeyError:
            print("No Lyrics found")
        try:
            self.audio_tags['genre'] = song['track']['genres']['primary']
        except KeyError:
            print("No Genre found")
        try:
            self.audio_tags['composer'] = song['track']['sections'][0]['metadata'][1]['text']
        except KeyError:
            print("No Composer found")
        self.new_file_name = f"{song['track']['subtitle']} - {song['track']['title']}"
        self.folder_name = self.audio_tags['artist']
        album_art = urlopen(song['track']['images']['coverart'])
        self.audio_tags['artwork'] = album_art.read()
        album_art.close()
        self.audio_tags['artwork'].first.thumbnail([64, 64])
        self.audio_tags.save()
        self.completed_media_files.append(self.media_files[self.media_file_index])
        self.print(f"\t\tTrack: {self.audio_tags['title']}\n"
                   f"\t\tArtist:{self.audio_tags['artist']}\n"
                   f"\t\tAlbum: {self.audio_tags['album']}\n"
                   f"\t\tYear: {self.audio_tags['year']}\n"
                   f"\t\tComments: {self.audio_tags['comment']}\n"
                   f"\t\tGenre: {self.audio_tags['genre']}\n"
                   f"\t\tCover Art URL: {song['track']['images']['coverart']}\n"
                   f"\tMetadata Saved Successfully!")
        self.media_file_index = 0

    # Check if media metadata title is the same as what is proposed
    def set_video_metadata(self) -> None:
        """
        Set video metadata for the media file.
        """
        self.print(f"\tUpdating metadata for {os.path.basename(self.new_media_file_path)}...")
        try:
            if "title" in ffmpeg.probe(self.new_media_file_path)['format']['tags']:
                current_title_metadata = ffmpeg.probe(self.new_media_file_path)['format']['tags']['title']
            else:
                current_title_metadata = ""
            video_codec = next(s for s in ffmpeg.probe(self.new_media_file_path)['streams']
                               if s['codec_type'] == 'video')['codec_name']
            self.print(f"Video Codec Detected: {video_codec}")
        except Exception as e:
            current_title_metadata = ""
            video_codec = ""
            self.print(f"Error reading metadata: {e}")
        current_index = self.media_file_index
        if ((current_title_metadata != self.new_file_name or (self.optimize and video_codec != "hevc"))
                and self.subtitle is False):
            failure = False
            try:
                ffmpeg.input(self.new_media_file_path) \
                    .output(self.temporary_media_file_path, **self.output_parameters) \
                    .overwrite_output() \
                    .run(quiet=self.quiet, overwrite_output=True)
            except Exception as e:
                try:
                    self.print(f"\t\tTrying to remap using alternative method...\n\t\tError: {e}")
                    ffmpeg.input(self.new_media_file_path) \
                        .output(self.temporary_media_file_path, **self.output_parameters) \
                        .overwrite_output() \
                        .run(quiet=self.quiet, overwrite_output=True)
                except Exception as e:
                    try:
                        self.print(f"\t\tTrying to remap using alternative optimized method...\n\t\tError: {e}")
                        self.video_codec = "libx265"
                        self.audio_codec = "aac"
                        self.output_parameters['crf'] = self.crf
                        self.output_parameters['audio_bitrate'] = self.audio_bitrate
                        self.output_parameters['preset'] = self.preset
                        output_parameters = {
                            'map_metadata': 0,
                            'map': 0,
                            'vcodec': self.video_codec,
                            'acodec': self.audio_codec,
                            'metadata:g:0': f"title={self.new_file_name}",
                            'metadata:g:1': f"comment={self.new_file_name}",
                            'crf': self.crf,
                            'audio_bitrate': self.audio_bitrate,
                            'preset': self.preset,
                        }
                        ffmpeg.input(self.new_media_file_path) \
                            .output(self.temporary_media_file_path, **output_parameters) \
                            .overwrite_output() \
                            .run(quiet=self.quiet, overwrite_output=True)
                    except Exception as e:
                        self.print(f"\t\tError trying to remap using alternative method...\n\t\tError: {e}")
                        failure = True
            if not failure:
                os.remove(self.new_media_file_path)
                os.rename(self.temporary_media_file_path, self.new_media_file_path)
            self.media_file_index = 0
        elif ((current_title_metadata != self.new_file_name or (self.optimize and video_codec != "hevc"))
              and self.subtitle is True):
            subtitle_file = "English.srt"
            subtitle_files = []
            if self.media_type == "series" and os.path.isdir(f"{self.parent_directory}/{self.folder_name}/Subs"):
                matching_video = 0
                subtitle_directories = glob.glob(f"{self.parent_directory}/{self.folder_name}/Subs/*/",
                                                 recursive=True)
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

            failure = False
            if not subtitle_exists and os.path.isfile(subtitle_file):
                input_ffmpeg = ffmpeg.input(self.new_media_file_path)
                input_ffmpeg_subtitle = ffmpeg.input(subtitle_file)
                input_subtitles = input_ffmpeg_subtitle['s']
                try:
                    (ffmpeg.output(
                        input_ffmpeg['v'], input_ffmpeg['a'], input_subtitles,
                        self.temporary_media_file_path, scodec=scodec, **self.output_parameters)
                     .overwrite_output().run(quiet=self.quiet, overwrite_output=True))
                except Exception as e:
                    failure = True
                if not failure:
                    os.remove(self.new_media_file_path)
                    os.rename(self.temporary_media_file_path, self.new_media_file_path)
            elif not subtitle_exists and not os.path.isfile(subtitle_file):
                try:
                    ffmpeg.input(self.new_media_file_path) \
                        .output(self.temporary_media_file_path, **self.output_parameters) \
                        .overwrite_output() \
                        .run(quiet=self.quiet, overwrite_output=True)
                except Exception as e:
                    failure = True
                if not failure:
                    os.remove(self.new_media_file_path)
                    os.rename(self.temporary_media_file_path, self.new_media_file_path)
            self.media_file_index = 0
        else:
            self.media_file_index += 1
        self.completed_media_files.append(self.media_files[current_index])
        self.print(f"Completed File: {self.completed_media_files[len(self.completed_media_files) - 1]}\n"
                   f"All Completed Files: {self.completed_media_files}")
        self.print(f"\tMetadata Updated: {os.path.basename(self.new_media_file_path)}")

    # Rename directory
    def rename_directory(self) -> None:
        """
        Rename the media directory.
        """
        if self.media_type == "music":
            self.folder_name = self.folder_name
        elif self.media_type == "series":
            self.folder_name = re.sub(" - S[0-9]+E[0-9]+", "", self.new_file_name)
        elif self.media_type == "media":
            self.folder_name = self.new_file_name
        # self.parent_directory = os.path.dirname(os.path.normpath(self.directory))
        # Check if media folder name is the same as what is proposed
        if os.path.normpath(os.path.join(self.directory, '')) != os.path.normpath(
                os.path.join(self.parent_directory, self.folder_name, '')):
            self.print(
                f"\tRenaming directory: \n\t\t{os.path.normpath(os.path.join(self.directory, ''))} \n\t\t➜\n\t\t"
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
            self.print(f"\tRenaming directory not needed: {os.path.normpath(os.path.join(self.directory, ''))}")

    # Cleanup Variables
    def reset_variables(self) -> None:
        """
        Reset class variables to their initial state.
        """
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
    def clean_media(self) -> None:
        """
        Process and clean all media files found.
        """
        while self.media_file_index < len(self.media_files):
            file_length = len(str(os.path.basename(self.media_files[self.media_file_index])))
            truncate_amount = 0
            if file_length > self.max_file_length:
                truncate_amount = abs(self.max_file_length - file_length)
            pretty_print_filename = str(os.path.basename(self.media_files[self.media_file_index]))
            pretty_print_filename = pretty_print_filename[truncate_amount:file_length]
            processing_message = (f"Processing ({self.media_file_index + 1}/"
                                  f"{self.total_media_files}): {pretty_print_filename}")
            max_line_length = max(self.max_file_length, len(processing_message))
            padding = ' ' * (max_line_length - len(processing_message))
            processing_message = (f"Processing ({self.media_file_index + 1}/"
                                  f"{self.total_media_files}): {pretty_print_filename}{padding}")
            processing_message = processing_message.ljust(self.terminal_width)
            self.print(processing_message, end='\r', quiet=False)
            sys.stdout.flush()
            self.directory = os.path.normpath(os.path.dirname(self.media_files[self.media_file_index]))
            if not self.directory.endswith(os.path.sep):
                self.directory += os.path.sep
            self.media_file = os.path.basename(self.media_files[self.media_file_index])
            self.file_name, self.file_extension = os.path.splitext(self.media_file)
            self.new_file_name = self.file_name
            self.build_output_parameters()
            self.media_detection()
            if self.file_extension[1:] in self.supported_video_types:
                self.clean_file_name()
            # For Videos, rename the file before setting the metadata,
            # For Audio, set the metadata first, then rename the file
            if self.file_extension[1:] in self.supported_video_types:
                self.verify_parent_directory()
                self.rename_file()
                self.clean_subtitle_directory(subtitle_directory=f"{self.parent_directory}/{self.folder_name}/Subs")
                self.set_media_metadata()
            elif self.file_extension[1:] in self.supported_audio_types:
                self.verify_parent_directory()
                self.set_media_metadata()
                self.rename_file()
            self.rename_directory()
        self.reset_variables()

    # Move media to new destination
    def move_media(self, target_directory: str, media_type="media") -> None:
        """
        Move media files to a new destination.

        Args:
        - target_directory (str): The target directory for moving media files.
        - media_type (str): The type of media files to move (default is "media").
        """
        if not os.path.isdir(target_directory):
            self.print(f"\nDirectory {target_directory} does not exist")
            return
        self.completed_media_files = []
        self.find_media()
        self.print(f"\nMoving {media_type} ({len(self.media_file_directories)})...")
        for media_directory_index in range(0, len(self.media_file_directories)):
            # Find if file inside this directory is named as a series
            move = False
            files = glob.glob(f"{self.media_file_directories[media_directory_index]}/*", recursive=True)
            for file in files:
                move = False
                if not os.path.exists(file):
                    continue
                if media_type == "series" and (bool(re.search("S[0-9][0-9]*E[0-9][0-9]*", file))
                                               or bool(re.search("s[0-9][0-9]*e[0-9][0-9]*", file))):
                    move = True
                    break
                if media_type == "media" and re.search("S[0-9][0-9]*E[0-9][0-9]*", file) is None \
                        and re.search("s[0-9][0-9]*e[0-9][0-9]*", file) is None:
                    move = True
                    break
                if media_type == "music" and (bool(re.search(".mp3", file))
                                              or bool(re.search(".m4a", file))):
                    move = True
                    break
            file_length = len(str(os.path.basename(self.media_file_directories[media_directory_index])))
            truncate_amount = 0
            if file_length > self.max_file_length:
                truncate_amount = abs(self.max_file_length - file_length)
            if move:
                if os.path.isdir(
                        os.path.join(
                            target_directory,
                            os.path.basename(self.media_file_directories[media_directory_index])
                        )
                ):
                    media_directory = str(os.path.basename(self.media_file_directories[media_directory_index]))[
                                      truncate_amount:file_length]
                    merging_message = f"Merging {media_type} " \
                                      f"({media_directory_index + 1}/{self.total_media_files}) " \
                                      f"{media_directory} " \
                                      f"➜ {target_directory}"
                    merging_message = merging_message.ljust(self.terminal_width)
                    self.print(merging_message, end='\r')
                    for file_name in os.listdir(self.media_file_directories[media_directory_index]):
                        # construct full file path
                        source = os.path.normpath(
                            os.path.join(self.media_file_directories[media_directory_index], file_name))
                        destination = os.path.normpath(os.path.join(target_directory, os.path.basename(
                            self.media_file_directories[media_directory_index])))
                        # move only files
                        if os.path.isfile(source):
                            if os.path.isfile(destination):
                                self.print(f"\t\tFile already exists {destination}, skipping...")
                            else:
                                try:
                                    shutil.move(source, destination)
                                except Exception as e:
                                    self.print(f"\t\tUnable to move to target directory: {target_directory}]\n\t\t"
                                               f"Error: {e}")
                    if os.path.isdir(
                            os.path.normpath(
                                os.path.join(
                                    self.media_file_directories[media_directory_index],
                                    "Subs")
                            )
                    ):
                        subtitles = glob.glob(f"{self.media_file_directories[media_directory_index]}/Subs/*/",
                                              recursive=True)
                        for subtitle_directory in subtitles:
                            shutil.move(
                                f"{subtitle_directory}",
                                os.path.normpath(
                                    os.path.join(
                                        target_directory,
                                        os.path.basename(self.media_file_directories[media_directory_index]),
                                        "Subs"
                                    )
                                )
                            )
                        shutil.rmtree(
                            os.path.normpath(
                                os.path.join(
                                    self.media_file_directories[media_directory_index],
                                    "Subs"
                                )
                            ),
                            ignore_errors=True
                        )
                    try:
                        os.rmdir(f"{self.media_file_directories[media_directory_index]}")
                    except OSError:
                        self.print(f"\t\tSkipping removal of "
                                   f"{self.media_file_directories[media_directory_index]}...")
                else:
                    media_directory = str(os.path.basename(self.media_file_directories[media_directory_index]))[
                                      truncate_amount:file_length]
                    moving_message = f"Moving {media_type} " \
                                     f"({len(self.media_file_directories)}/{self.total_media_files}) " \
                                     f"{media_directory} " \
                                     f"➜ {target_directory}"
                    moving_message = moving_message.ljust(self.terminal_width)
                    self.print(moving_message, end='\r')
                    try:
                        shutil.move(self.media_file_directories[media_directory_index], target_directory)
                    except Exception as e:
                        self.print(f"\nUnable to move to target directory: {target_directory}]\n\t\tError: {e}")


def media_manager(argv):
    """
    Main function for managing media files.

    Args:
    - argv (list): Command-line arguments.

    """
    media_manager_instance = MediaManager()
    media_flag = False
    music_flag = False
    tv_flag = False
    subtitle_flag = False
    optimize_flag = False
    audio_bitrate = '128k'
    preset = 'medium'
    crf = 28
    tv_directory = os.path.join(os.path.expanduser('~'), "Downloads")
    media_directory = os.path.join(os.path.expanduser('~'), "Downloads")
    music_directory = os.path.join(os.path.expanduser('~'), "Downloads")
    source_directory = os.path.join(os.path.expanduser('~'), "Downloads")
    try:
        opts, args = getopt.getopt(argv, "hvd:a:m:t:s",
                                   ["help", "crf=", "audio-bitrate=", "media-directory=", "tv-directory=",
                                    "music-directory", "directory=", "preset=",
                                    "subtitle", "verbose", "optimize"])
    except getopt.GetoptError as e:
        print(f"Argument Error: {e}")
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("--audio-bitrate"):
            audio_bitrate = arg
        elif opt in ("--crf"):
            crf = arg
        elif opt in ("-d", "--directory"):
            source_directory = arg
        elif opt in ("-a", "--music-directory"):
            music_flag = True
            music_directory = arg
        elif opt in ("-m", "--media-directory"):
            media_flag = True
            media_directory = arg
        elif opt in ("-o", "--optimize"):
            optimize_flag = True
        elif opt in ("--preset"):
            preset = arg.lower()
        elif opt in ("-t", "--tv-directory"):
            tv_flag = True
            tv_directory = arg
        elif opt in ("-s", "--subtitle"):
            subtitle_flag = True
        elif opt in ("-v", "--verbose"):
            media_manager_instance.set_verbose(quiet=False)

    media_manager_instance.set_media_directory(media_directory=source_directory)
    media_manager_instance.find_media()
    media_manager_instance.set_crf(crf=crf)
    media_manager_instance.set_preset(preset=preset)
    media_manager_instance.set_audio_bitrate(audio_bitrate=audio_bitrate)
    media_manager_instance.set_optimize(optimize=optimize_flag)
    media_manager_instance.set_subtitle(subtitle=subtitle_flag)
    media_manager_instance.clean_media()

    if tv_flag:
        media_manager_instance.move_media(target_directory=tv_directory, media_type="series")
    if media_flag:
        media_manager_instance.move_media(target_directory=media_directory, media_type="media")
    if music_flag:
        media_manager_instance.move_media(target_directory=music_directory, media_type="music")
    print("Complete!")


def usage():
    """
    Display usage information.
    """
    print(f'Media-Manager: A tool to manage all your media!\n'
          f'Version: {__version__}\n'
          f'Author: {__author__}\n'
          f'Credits: {__credits__}\n'
          f'\nUsage:\n'
          f'-h | --help            [ See usage ]\n'
          f'-d | --directory       [ Directory to scan for media ]\n'
          f'--media-directory      [ Directory to move Media ]\n'
          f'--music-directory      [ Directory to move Music ]\n'
          f'--tv-directory         [ Directory to move Series ]\n'
          f'--subtitle             [ Apply subtitle in media Sub folder ]\n'
          f'--optimize             [ Optimize video for streaming in HEVC ]\n'
          f'-v | --verbose         [ Show Output of FFMPEG ]\n'
          f'\nExample:\n'
          f'media-manager -d "~/Downloads" -m "~/User/Media/Movies" -t "~/User/Media/TV" -s\n')


def main():
    media_manager(sys.argv[1:])


if __name__ == "__main__":
    media_manager(sys.argv[1:])
