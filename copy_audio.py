from pathlib import Path
import re
import shutil
import music_tag
import warnings

audio_filename_pat = re.compile(r'^AudioFilename:')
title_pat = re.compile(r'^Title:')
artist_pat = re.compile(r'^Artist:')
version_pat = re.compile(r'^Version:')
events_pat = re.compile(r'^\[Events\]')
blank_line_pat = re.compile(r'^\s*$')
bg_filename_pat = re.compile(r'^0,0,([^,]*),\d+,\d+')
forbidden_pat = re.compile(r'[<>:"\/\\|?*]')
underscore_pat = re.compile(r"'")
extension_pat = re.compile(r'\.[^\.]+$')
not_extension_pat = re.compile(r'^.[^\.]*')

def copy_audio(p_in_sub: Path, p_out_sub: Path):
    prev_audio_filenames = set()
    for osu_file in list(p_in_sub.glob('*.osu')):
        # extract a bunch of stuff from the .osu file
        audio_filename, title, artist, version, bg_filename, legal_title, legal_artist, legal_version = extract_beatmap_info(osu_file)

        # skip this osu file if audio_filename was already copied
        if audio_filename in prev_audio_filenames:
            continue
        else:
            prev_audio_filenames.add(audio_filename)

        # Don't change the song's filename if the artist is various artists
        is_various_artists = artist.lower() == 'various artists'
        audio_extension = not_extension_pat.sub('', audio_filename)
        song_filename = (audio_filename
                         if is_various_artists 
                         else fr'{legal_artist} - {legal_title} [{legal_version}]{audio_extension}')

        # Create a deeper subdirectory if the artist is various artists
        p_real_out_sub = p_out_sub
        if (is_various_artists):
            deep_dir = extension_pat.sub('', song_filename)
            p_real_out_sub = Path(f'{p_out_sub}/{deep_dir}')
            p_real_out_sub.mkdir(parents=True, exist_ok=True)

        # Copy the song to the output folder
        p_in_song = Path(fr'{p_in_sub}/{audio_filename}')
        p_out_song = Path(fr'{p_real_out_sub}/{song_filename}')
        if not p_in_song.is_file():
            print(f"\033[33mWarning:\033[0m the audio file from {str(osu_file)} couldn't be found, skipping")
        if not p_out_song.is_file() and p_in_song.is_file():
            shutil.copy(p_in_song, p_out_song)

            # Don't modify the metadata if the artist is various artists
            if not is_various_artists:
                # modify the metadata
                f = music_tag.load_file(str(p_out_song))
                f['title'] = title
                f['artist'] = artist
                f.save()

        # Copy the background to the output folder
        p_in_bg = Path(fr'{p_in_sub}/{bg_filename}')
        # If the artist is various artists, copy to a deeper subdirectory
        p_out_bg = Path(fr'{p_real_out_sub}/{bg_filename}')
        if not p_in_bg.is_file() and bg_filename:
            print(f"\033[33mWarning:\033[0m the background file from {str(osu_file)} couldn't be found, skipping")
            
        if not p_out_bg.is_file() and p_in_bg.is_file():
            shutil.copy(p_in_bg, p_out_bg)

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
                # Why the fuck does an apostrophe get replaced with an underscore here
                audio_filename = underscore_pat.sub('_', audio_filename) 
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
                bg_filename = underscore_pat.sub('_', bg_filename)

            if audio_filename and title and artist and version and bg_filename:
                break

    if not audio_filename or not title or not artist or not version:
        raise KeyError(f"{str(osu_file)} is missing AudioFilename, Title, Artist, or Version")

    return audio_filename, title, artist, version, bg_filename, legal_title, legal_artist, legal_version

# # Testing code
# p_in_sub = Path('/home/stanley/Music/Songs/1441640 DJ SHARPNEL - FAKE PROMISE/')
# p_out_sub = Path('/home/stanley/Music/Extracted-Songs/DJ SHARPNEL - FAKE PROMISE 1441640/')
# copy_audio(p_in_sub, p_out_sub)
