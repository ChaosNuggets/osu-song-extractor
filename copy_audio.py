from pathlib import Path
import re

audio_filename_pat = re.compile(r'^AudioFilename:')
title_pat = re.compile(r'^Title:')
artist_pat = re.compile(r'^Artist:')
version_pat = re.compile(r'^Version:')
events_pat = re.compile(r'^\[Events\]')
blank_line_pat = re.compile(r'^\s*$')
bg_filename_pat = re.compile(r'^0,0,([^,]*),\d+,\d+')
forbidden_pat = re.compile(r'[<>:"\/\\|?*]')

def copy_audio(p_in_sub: Path, p_out_sub: Path):
    prev_audio_filenames = set()
    for osu_file in list(p_in_sub.glob('*.osu')):
        extract_beatmap_info(osu_file)

# Looks at .osu file and returns audio_filename, title,
# artist, version, and background filename (if it exists)
def extract_beatmap_info(osu_file: Path):
    audio_filename = ''
    title = ''
    artist = ''
    version = ''
    bg_filename = ''
    legal_title = ''
    legal_artist = ''
    legal_version = ''
    is_events_section = False
    with open(osu_file, 'r') as file:
        for line in file:
            if audio_filename_pat.search(line):
                audio_filename = audio_filename_pat.sub('', line).strip('\n \"\'')
            elif title_pat.search(line):
                title = title_pat.sub('', line).strip('\n \"\'')
                legal_title = forbidden_pat.sub(r'-', title)
            elif artist_pat.search(line):
                artist = artist_pat.sub('', line).strip('\n \"\'')
                legal_artist = forbidden_pat.sub(r'-', artist)
            elif version_pat.search(line):
                version = version_pat.sub('', line).strip('\n \"\'')
                legal_version = forbidden_pat.sub(r'-', version)
            elif events_pat.search(line):
                is_events_section = True
            elif blank_line_pat.search(line):
                is_events_section = False
            elif is_events_section and bg_filename_pat.search(line):
                bg_filename = bg_filename_pat.sub(r'\1', line).strip('\n \"\'')

            if audio_filename and title and artist and version and bg_filename:
                break

    # print(audio_filename)
    # print(title)
    # print(artist)
    # print(version)
    # print(bg_filename)
    # print(legal_title)
    # print(legal_artist)
    # print(legal_version)
    # print()

    if not audio_filename or not title or not artist or not version:
        raise KeyError(f"{str(osu_file)} is missing AudioFilename, Title, Artist, or Version")

    return audio_filename, title, artist, version, bg_filename

# Testing code
p_in_sub = Path('/home/stanley/Music/Songs/1816915 Sayuri - Hana no Tou/')
copy_audio(p_in_sub, p_in_sub)
