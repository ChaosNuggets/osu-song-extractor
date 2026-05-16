from pathlib import Path
import re
import shutil
import music_tag
from dataclasses import dataclass, astuple, asdict
from parse_utils import parse_string
from typing import TextIO

# Looks for a configuration option in the form "<option>:<value>", puts
# option into group 1, and puts value into group 2. This works for 
# AudioFilename, Title, Artist, Version, BeatmapID, and BeatmapSetID.
conf_pat = re.compile(r'^(.*):(.*)')

# Finds section headers in the form [<header>] and puts header in group 1
section_pat = re.compile(r'^\[(.*)\]')

# Finds the background filename and puts it into group 1
bg_filename_pat = re.compile(r'^0,0,([^,]*),\d+,\d+')

forbidden_pat = re.compile(r'[<>:"\/\\|?*]') # Looks for forbidden filename chars

# Puts the filename without the extension in group 1 and the extension in group 2
filename_pat = re.compile(r'(.*)\.([^\.]+)$')

@dataclass
class BeatmapInfo:
    audio_filename: str = ''
    title: str = ''
    artist: str = ''
    version: str = ''
    bg_filename: str = ''
    beatmap_id: int = 0
    beatmap_set_id: int = 0

    # Looks at .osu file and initializes all the member variables
    def extract_beatmap_info(self, file: TextIO) -> None:
        is_events_section = False
        for line in file:
            # Break if all the member variables have been initialized
            if all(astuple(self)):
                break

            # Search for section header pattern in line
            section_match = section_pat.search(line)
            if section_match:
                # If the section is Events, set the flag to True,
                # otherwise, set it to False
                if section_match.group(1) == 'Events':
                    is_events_section = True
                else:
                    is_events_section = False
                continue

            # Search for background filename in line
            bg_match = bg_filename_pat.search(line)
            if is_events_section and bg_match:
                value = bg_match.group(1)
                # Why the fuck does an apostrophe get replaced with an underscore here
                self.bg_filename = parse_string(value).replace("'", "_")
                continue

            # Look pattern "<option>:<value>" in line
            conf_match = conf_pat.search(line)
            if not conf_match:
                continue

            # If there's a match, initialize the corresponding member variable
            option = conf_match.group(1)
            value = conf_match.group(2)
            match option:
                case 'AudioFilename':
                    # Why the fuck does an apostrophe get replaced with an underscore here
                    self.audio_filename = parse_string(value).replace("'", "_")
                case 'Title':
                    self.title = value.strip()
                case 'Artist':
                    self.artist = value.strip()
                case 'Version':
                    self.version = value.strip()
                case 'BeatmapID':
                    self.beatmap_id = int(value)
                case 'BeatmapSetID':
                    self.beatmap_set_id = int(value)

# Searches all the beatmap folders, creates a corresponding subfolder if
# export_into_subfolders = True, and calls copy_audio to do the rest
def write_output(conf_values: ConfValues) -> None:
    # Search each subfolder of the songs folder
    p_in = Path(conf_values.input_dir)
    for p_in_sub in p_in.iterdir():
        if not p_in_sub.is_dir():
            continue
        
        # Extract the beatmap info from all the .osu files in that subfolder
        beatmap_infos = extract_beatmap_infos(p_in_sub)

        # TODO: continue
        # # Create the output subfolder
        # input_subfolder = str(p_in_sub)
        # output_subfolder = conf_values.output_dir + subfolder_pattern.sub(r'\1\3 \2', input_subfolder)
        # p_out_sub = Path(output_subfolder)
        # p_out_sub.mkdir(parents=True, exist_ok=True)

        # # Copy all the audio
        # copy_audio(p_in_sub, p_out_sub)

# Extract the beatmap info from all the .osu files in a directory and return them in a list
def extract_beatmap_infos(path: Path) -> list[BeatmapInfo]:
    # Iterate through all .osu files
    beatmap_infos: list[BeatmapInfo] = []
    for osu_file in list(path.glob('*.osu')):

        # Extract the beatmap info from a single .osu file
        beatmap_info = BeatmapInfo()
        with open(osu_file, 'r') as file:
            beatmap_info.extract_beatmap_info(file)

        # Throw error if crucial key is missing from .osu file
        for key, value in asdict(beatmap_info).items():
            if not value and key != 'bg_filename':
                raise KeyError(f"{osu_file} is missing {key}!")

        beatmap_infos.append(beatmap_info) # add to return list

    return beatmap_infos

def copy_audio(p_in_sub: Path, p_out_sub: Path) -> None:
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

            # Fill in the metadata if it's missing 
            f = music_tag.load_file(str(p_out_song))
            if not f['title'].value:
                # modify the metadata
                f['title'] = title if not is_various_artists else version
            if not f['artist'].value and not is_various_artists:
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



# # Testing code
# p_in_sub = Path('/home/stanley/Music/Songs/1441640 DJ SHARPNEL - FAKE PROMISE/')
# p_out_sub = Path('/home/stanley/Music/Extracted-Songs/DJ SHARPNEL - FAKE PROMISE 1441640/')
# copy_audio(p_in_sub, p_out_sub)
