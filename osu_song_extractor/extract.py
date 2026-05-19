from pathlib import Path
import re
import shutil
import music_tag
from dataclasses import dataclass, astuple, asdict
from osu_song_extractor.parse_utils import parse_string, parse_filename
from osu_song_extractor.conf import ConfInfo, XBGXSongConfInfo, MetaWriteMode, BGExportMode
from typing import TextIO

# Looks for a configuration option in the form "<option>:<value>", puts
# option into group 1, and puts value into group 2. This works for 
# AudioFilename, Title, Artist, Version, BeatmapID, and BeatmapSetID.
osu_conf_pat = re.compile(r'^([^\n\r:]*):(.*)')

# Finds section headers in the form [<header>] and puts header in group 1
osu_section_pat = re.compile(r'^\[(.*)\]')

# Finds the background filename and puts it into group 1
bg_filename_pat = re.compile(r'^0,0,([^,]*),[-\d]+,[-\d]+')

# Looks for something surrounded by angle brackets
replacement_field_pat = re.compile(r'<[^\n\r<>]+>')

@dataclass
class BeatmapInfo:
    audio_filename: str = ''
    title: str = ''
    artist: str = ''
    version: str = ''
    bg_filename: str = ''
    beatmap_id: int = 0
    beatmap_set_id: int = 0
    osu_filename: str = ''

    # Looks at .osu file and initializes all the member variables
    def extract_beatmap_info(self, file: TextIO) -> bool:
        self.osu_filename = file.name
        is_events_section = False

        # Iterate through each line in the .osu file
        for line in file:
            # Break if all the member variables have been initialized
            if all(astuple(self)):
                break

            # Search for section header pattern in line
            section_match = osu_section_pat.search(line)
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
                # Strips string and replaces apostrophe with underscore
                # Why the fuck does an apostrophe get replaced with an underscore here Peppy
                self.bg_filename = parse_string(value).replace("'", "_")
                continue

            # Look pattern "<option>:<value>" in line
            conf_match = osu_conf_pat.search(line)
            if not conf_match:
                continue

            # If there's a match, initialize the corresponding member variable
            option = conf_match.group(1)
            value = conf_match.group(2)
            match option:
                case 'AudioFilename':
                    # Strips string and replaces apostrophe with underscore
                    # Why the fuck does an apostrophe get replaced with an underscore here Peppy
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

        # Return False if crucial key is missing from .osu file
        for key, value in asdict(self).items():
            if not value and key != 'bg_filename': # and key != 'beatmap_id' and key != 'beatmap_set_id':
                print(f"\033[33mWarning:\033[0m {self.osu_filename} is missing {key}, skipping")
                return False

        return True # Return True otherwise

    # Replaces the replacement fields in value with the info in beatmap_info
    def parse_replacement_fields(self, value: str) -> str:
        # Find something that is surrounded by angle brackets and call the
        # callback function to determine what to replace it with
        return replacement_field_pat.sub(self._replacement_field_callback, value)
    
    # Returns the corresponding information from beatmap_info based on the replacement field in m
    def _replacement_field_callback(self, m: re.Match[str]) -> str:
        match m.group():
            case r'<AudioFilename>':
                return parse_filename(self.audio_filename)[0]
            case r'<Title>':
                return self.title
            case r'<Artist>':
                return self.artist
            case r'<Version>':
                return self.version
            case r'<BackgroundFilename>':
                return parse_filename(self.bg_filename)[0]
            case r'<BeatmapID>':
                return str(self.beatmap_id)
            case r'<BeatmapSetID>':
                return str(self.beatmap_set_id)
    
        return m.group()

# Searches all the beatmap folders, creates a corresponding subfolder if
# export_into_subfolders = True, and calls extract_beatmap to do the rest
def extract_all_beatmaps(conf_info: ConfInfo) -> None:
    # Search each subfolder of the songs folder
    p_in = Path(conf_info.input_dir)
    for p_in_sub in p_in.iterdir():
        if not p_in_sub.is_dir():
            continue

        # Extract the audio from that beatmap set
        extract_beatmap(p_in_sub, conf_info)

def extract_beatmap(p_in_sub: Path, conf_info: ConfInfo) -> None:
    # Extract the beatmap info from all the .osu files in that subfolder
    beatmap_set_info = extract_beatmap_set_info(p_in_sub)
    if not beatmap_set_info:
        return # Return if no .osu files in folder

    # Create the output subfolder if the user wants it
    p_out_sub = Path(conf_info.output_dir)
    if conf_info.export_into_subfolders:
        # Parse the replacement fields of subfolder_name using the first .osu file in beatmap_set_info
        out_sub = beatmap_set_info[0].parse_replacement_fields(conf_info.subfolder_name)
        out_sub = conf_info.replace_illegal_chars(out_sub)
        p_out_sub = Path(rf'{conf_info.output_dir}/{out_sub}')
    p_out_sub.mkdir(parents=True, exist_ok=True)

    # Count the number of audio files and backgrounds and categorize the beatmap set
    audio_filenames = {beatmap_info.audio_filename for beatmap_info in beatmap_set_info if beatmap_info.audio_filename}
    bg_filenames = {beatmap_info.bg_filename for beatmap_info in beatmap_set_info if beatmap_info.bg_filename}
    match (len(bg_filenames), len(audio_filenames)):
        case (1, 1) | (0, 1) | (1, 0) | (0, 0):
            x_bg_x_song_conf_info = conf_info.one_bg_one_song
        case (_, 1) | (_, 0):
            x_bg_x_song_conf_info = conf_info.mult_bg_one_song
        case (1, _) | (0, _):
            x_bg_x_song_conf_info = conf_info.one_bg_mult_song
        case (_, _):
            x_bg_x_song_conf_info = conf_info.mult_bg_mult_song

    copied_audio: set[str] = set()
    copied_bgs: set[str] = set()
    # Iterate through each beatmap's info
    for beatmap_info in beatmap_set_info:
        # Create a deeper subdirectory if x_bg_x_song.export_into_deep_subfolder is True
        p_out_deep = p_out_sub
        if x_bg_x_song_conf_info.export_into_deep_subfolder:
            deep_sub = beatmap_info.parse_replacement_fields(x_bg_x_song_conf_info.deep_subfolder_name)
            deep_sub = conf_info.replace_illegal_chars(deep_sub)
            p_out_deep = Path(f'{p_out_sub}/{deep_sub}')
            p_out_deep.mkdir(parents=True, exist_ok=True)

        # Copy the song to the output folder if it hasn't been copied yet
        p_out_song = None
        if beatmap_info.audio_filename not in copied_audio:
            copied_audio.add(beatmap_info.audio_filename)
            p_out_song = copy_song(p_in_sub, p_out_deep, beatmap_info, conf_info, x_bg_x_song_conf_info)

        # Copy the background to output folder / metadata if it hasn't been copied yet
        # TODO: fix this, the user will want multiple exported backgrounds when exporting as metadata
        if beatmap_info.bg_filename not in copied_bgs:
            copied_bgs.add(beatmap_info.bg_filename)
            copy_bg(p_in_sub, p_out_deep, p_out_song, beatmap_info, conf_info, x_bg_x_song_conf_info)

# Extract the beatmap info from all the .osu files in a directory and return them in a list
def extract_beatmap_set_info(path: Path) -> list[BeatmapInfo]:
    # Iterate through all .osu files
    beatmap_set_info: list[BeatmapInfo] = []
    for osu_file in list(path.glob('*.osu')):

        # Extract the beatmap info from a single .osu file
        beatmap_info = BeatmapInfo()
        with open(osu_file, 'r') as file:
            is_valid_beatmap = beatmap_info.extract_beatmap_info(file)

        # If no crucial fields are missing from .osu file, append to return list
        if is_valid_beatmap:
            beatmap_set_info.append(beatmap_info)

    return beatmap_set_info

# Copies the audio file and writes the metadata
# Returns the path to the copied song
def copy_song(p_in_sub: Path, p_out_deep: Path,
              beatmap_info: BeatmapInfo, conf_info: ConfInfo, x_bg_x_song_conf_info: XBGXSongConfInfo) -> Path:
    # Locate the source and destination paths of song copy process
    out_song = beatmap_info.parse_replacement_fields(x_bg_x_song_conf_info.song_filename) # Parse replacement fields
    audio_ext = parse_filename(beatmap_info.audio_filename)[1] # Get audio extension
    out_song = fr'{conf_info.replace_illegal_chars(out_song)}{audio_ext}' # Re-add audio extension
    p_in_song = Path(fr'{p_in_sub}/{beatmap_info.audio_filename}') # Get source path
    p_out_song = Path(fr'{p_out_deep}/{out_song}') # Get destination path

    # If audio file is not found, attempt to find a file with the same name but doesn't match case.
    # If that fails, print warning and return None to signal that no copy happened
    if not p_in_song.is_file():
        p_in_song = find_case_insensitive_file(p_in_sub, p_in_song)
        if not p_in_song:
            # If no match, then print a warning and return None
            print(f"\033[33mWarning:\033[0m the audio file from {beatmap_info.osu_filename} was listed but couldn't be found.")
            return None

    # If overwrite_existing_files is True or the destination file doesn't exist, copy
    if not (x_bg_x_song_conf_info.overwrite_existing_files or not p_out_song.is_file()):
        return None # Return None to signal that no copy happened
    shutil.copy2(p_in_song, p_out_song)

    # No need to write metadata if meta_write_mode is NEVER, so return
    if x_bg_x_song_conf_info.meta_write_mode == MetaWriteMode.NEVER:
        return p_out_song # Return path to copied song

    # Fill in the title and artist metadata if it's missing or if meta_write_mode is ALWAYS
    f = music_tag.load_file(p_out_song)
    if not f['title'].value or x_bg_x_song_conf_info.meta_write_mode == MetaWriteMode.ALWAYS:
        f['title'] = beatmap_info.parse_replacement_fields(x_bg_x_song_conf_info.title_meta)
    if not f['artist'].value or x_bg_x_song_conf_info.meta_write_mode == MetaWriteMode.ALWAYS:
        f['artist'] = beatmap_info.parse_replacement_fields(x_bg_x_song_conf_info.artist_meta)
    f.save()
    return p_out_song # Return path to copied song

# Copy the background to the output folder / metadata
def copy_bg(p_in_sub: Path, p_out_deep: Path, p_out_song: Path | None,
            beatmap_info: BeatmapInfo, conf_info: ConfInfo, x_bg_x_song_conf_info: XBGXSongConfInfo) -> None:
    # No need to copy background if bg_export_mode is NEVER
    if x_bg_x_song_conf_info.bg_export_mode == BGExportMode.NEVER:
        return

    # If background wasn't listed in .osu file, return
    if not beatmap_info.bg_filename:
        return

    # Locate the background source path
    p_in_bg = Path(fr'{p_in_sub}/{beatmap_info.bg_filename}') # Get source path

    # If background file is not found, attempt to find a file with the same name but doesn't match case.
    # If that fails, print warning and return None to signal that no copy happened
    if not p_in_bg.is_file():
        p_in_bg = find_case_insensitive_file(p_in_sub, p_in_bg)
        if not p_in_bg:
            print(f"\033[33mWarning:\033[0m the background file from {beatmap_info.osu_filename} was listed but couldn't be found.")
            return

    # Export background as metadata if the user wants that
    if x_bg_x_song_conf_info.bg_export_mode != BGExportMode.AS_SEPARATE:
        # If audio file was never copied, return
        if not p_out_song:
            return

        # If the artwork metadata exists and bg_export_mode is not AS_META_ALWAYS, return
        f = music_tag.load_file(p_out_song)
        if not (not f['artwork'].value or x_bg_x_song_conf_info.bg_export_mode == BGExportMode.AS_META_ALWAYS):
            return

        # Copy the background as metadata
        with open(p_in_bg, 'rb') as img_in:
            f['artwork'] = img_in.read()
        f.save()
        return

    # Export background as separate if the user wants that
    # If overwrite_existing_files is True or the destination file doesn't exist, copy
    out_bg = beatmap_info.parse_replacement_fields(x_bg_x_song_conf_info.bg_filename) # Parse replacement fields
    bg_ext = parse_filename(beatmap_info.bg_filename)[1] # Get image extension
    out_bg = fr'{conf_info.replace_illegal_chars(out_bg)}{bg_ext}' # Re-add image extension
    p_out_bg = Path(fr'{p_out_deep}/{out_bg}') # Get destination path
    if not p_out_bg.is_file() or x_bg_x_song_conf_info.overwrite_existing_files:
        shutil.copy2(p_in_bg, p_out_bg)

# WHY DO YOU ALLOW CASE INSENSITIVE FILENAMES IN YOUR .OSU FILE PEPPY WTF
def find_case_insensitive_file(p_in_sub: Path, p_in_file: Path) -> Path | None:
    # Look through every path recursively and return the match if found
    for sub_path in p_in_sub.rglob('*'):
        if sub_path.is_file() and str(sub_path.resolve()).lower() == str(p_in_file.resolve()).lower():
            return sub_path

    return None # If no match, return None
