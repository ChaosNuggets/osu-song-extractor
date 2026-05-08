from pathlib import Path

audio_filename_pat = re.compile(r'^AudioFilename:')
title_pat = re.compile(r'^Title:')
artist_pat = re.compile(r'^Artist:')
version_pat = re.compile(r'^Version:')
events_pat = re.compile(r'^\[Events\]')
blank_line_pat = re.compile(r'^\s*$')
bg_filename_pat = re.compile(r'^0,0,([^,]*)')

def copy_audio(p_in_sub: Path, p_out_sub: Path):
    prev_audio_filenames = set()
    for osu_file in list(p_in_sub.glob('*.osu')):
        extract_beatmap_info()

def extract_beatmap_info(osu_file: Path):
    audio_filename = ''
    title = ''
    artist = ''
    version = ''
    bg_filename = ''
    is_events_section = false
    with open(osu_file, 'r') as file:
        for line in file:
            if audio_filename_pat.search(line):
                audio_filename = audio_filename_pat.sub('', line).strip('\n \"\'')
            elif title_pat.search(line):
                title = title_pat.sub('', line).strip('\n \"\'')
            elif artist_pat.search(line):
                artist = artist_pat.sub('', line).strip('\n \"\'')
            elif version_pat.search(line):
                version = version_pat.sub('', line).strip('\n \"\'')
            elif events_pat.search(line):
                is


