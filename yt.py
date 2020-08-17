import subprocess
import logging
import os
import json


supported_formats = ['240p', '360p', '480p', '720p', '1080p']


def pull_formats(url):
    logging.info(f'Polling format information from video: {url}')
    video_info = subprocess.check_output(
        f"youtube-dl '{url}' -j", shell=True).decode('utf-8').strip()
    video_info = json.loads(video_info)

    formats = {}
    for format in video_info['formats']:
        if format['ext'] == "mp4" and format['acodec'] != 'none' and format['format_note'] in supported_formats:
            formats[format['format_note']] = {
                'filesize': format['filesize'] or 0,
                'format_id': format['format_id']
            }

    return formats


def download_video(url, format_id):
    logging.info(f'Downloading {url}...')

    # Pull the title first
    title = subprocess.check_output(
        f"youtube-dl --get-title '{url}'", shell=True).decode('utf-8').strip()

    logging.info(f'Downloading video with format {format_id} and title: {title}')
    file_name = abs(hash(url))

    format_flag = ''
    if format_id is not None:
        format_flag = f' -f {format_id}'

    subprocess.check_output(f"youtube-dl '{url}' {format_flag} -o {file_name}", shell=True)
    logging.info(f'Downloaded {url} as {file_name}')

    for root, dirs, files in os.walk("."):
        for file in files:
            if file.startswith(str(file_name)):
                return (title, file)

    return None
