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
        self.links = []
        self.download_directory = f'{os.path.expanduser("~")}/Downloads'

        in_file = ffmpeg.input('input.mp4')
        overlay_file = ffmpeg.input('overlay.png')(ffmpeg.concat(in_file.trim(start_frame=10, end_frame=20),
                                                                 in_file.trim(start_frame=30, end_frame=40), ).overlay(
        overlay_file.hflip()).drawbox(50, 50, 120, 120, color='red', thickness=5).output('out.mp4').run())

    def subtitle_manager(self):
        ffmpeg.input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(width, height)).output(out_filename, pix_fmt='yuv420p').overwrite_output()

    def open_file(self, file):
        youtube_urls = open(file, 'r')
        for url in youtube_urls:
            self.links.append(url)
        self.links = list(dict.fromkeys(self.links))

    def get_save_path(self):
        return self.download_directory

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
    media_manager(sys.argv[1:])
