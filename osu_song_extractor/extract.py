from pathlib import Path
import re
import shutil
import music_tag
from dataclasses import dataclass, astuple, asdict
from osu_song_extractor.parse_utils import parse_string, parse_filename
from osu_song_extractor.conf import ConfInfo, BeatmapTypeConfInfo, MetaWriteMode, BGExportMode
from typing import TextIO
from collections import deque

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

# Stores the stuff that we read from each .osu file
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
    def read_beatmap_info(self, file: TextIO) -> bool:
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
            if not value and key != 'bg_filename' and key != 'beatmap_id' and key != 'beatmap_set_id':
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

# Stores the information we need in order to perform an extraction
# used by copy_bg(...), copy_song(...), extract_beatmap(...)
@dataclass
class ExtractionInfo:
    p_in: Path
    p_out: Path
    beatmap_info: BeatmapInfo
    conf_info: ConfInfo
    beatmap_type_conf_info: BeatmapTypeConfInfo

    # astuple(...) function but non-recursive
    def unpack(self) -> tuple[Path, Path, BeatmapInfo, ConfInfo, BeatmapTypeConfInfo]:
        return self.p_in, self.p_out, self.beatmap_info, self.conf_info, self.beatmap_type_conf_info

# Searches all the beatmap folders, creates a corresponding subfolder if
# export_into_subfolders = True, and calls extract_beatmap_set to do the rest
def extract_all_beatmap_sets(conf_info: ConfInfo) -> None:
    # Search each subfolder of the songs folder
    p_in = Path(conf_info.input_dir)
    for p_in_sub in p_in.iterdir():
        if not p_in_sub.is_dir():
            continue

        # Extract the audio from that beatmap set
        extract_beatmap_set(p_in_sub, conf_info)

def extract_beatmap_set(p_in_sub: Path, conf_info: ConfInfo) -> None:
    # Extract the beatmap info from all the .osu files in that subfolder
    beatmap_set_info = read_beatmap_set_info(p_in_sub)
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
    num_audio_filenames = len({beatmap_info.audio_filename for beatmap_info in beatmap_set_info if beatmap_info.audio_filename})
    num_bg_filenames = len({beatmap_info.bg_filename for beatmap_info in beatmap_set_info if beatmap_info.bg_filename})
    if num_audio_filenames <= 1:
        beatmap_type_conf_info = conf_info.one_song
    # If the number of backgrounds is less than the number of audio files * beatmap_type_cutoff (0.7 default),
    # it's probably a pack with rates. I don't know how to write a better predictor than this lol
    elif num_bg_filenames < num_audio_filenames * conf_info.beatmap_type_cutoff:
        beatmap_type_conf_info = conf_info.rates
    else:
        beatmap_type_conf_info = conf_info.map_pack

    # Iterate through each beatmap's info
    copied_audio: set[str] = set()
    copied_bgs: set[str] = set()
    for beatmap_info in beatmap_set_info:
        extraction_info = ExtractionInfo(p_in_sub, p_out_sub, beatmap_info, conf_info, beatmap_type_conf_info)
        extract_beatmap(extraction_info, copied_audio, copied_bgs)

# Extract the beatmap info from all the .osu files in a directory and return them in a deque
def read_beatmap_set_info(path: Path) -> deque[BeatmapInfo]:
    # Iterate through all .osu files
    beatmap_set_info: deque[BeatmapInfo] = deque()
    for osu_file in list(path.glob('*.osu')):

        # Extract the beatmap info from a single .osu file
        beatmap_info = BeatmapInfo()
        with open(osu_file, 'r') as file:
            is_valid_beatmap = beatmap_info.read_beatmap_info(file)

        # If no crucial fields are missing from .osu file, append to return list
        if not is_valid_beatmap:
            continue

        # If the osu file has a background, add it to the front of the list.
        # Otherwise, add it to the back of the list. This ensures tha tbeatmaps with
        # backgrounds are prioritized and exporting background as metadata always works.
        if beatmap_info.bg_filename:
            beatmap_set_info.appendleft(beatmap_info)
        else:
            beatmap_set_info.append(beatmap_info)

    return beatmap_set_info

# Extracts a single beatmap using extraction_info. copied_audio and copied_bgs
# are sets of audio filenames and background filenames that have alaready been copied.
def extract_beatmap(extraction_info: ExtractionInfo, copied_audio: set[str], copied_bgs: set[str]) -> None:
    # Unpack everything
    p_in_sub, p_out_sub, beatmap_info, conf_info, beatmap_type_conf_info = extraction_info.unpack()

    # Create a deeper subdirectory if beatmap_type_conf_info.export_into_deep_subfolder is True
    p_out_deep = p_out_sub
    if beatmap_type_conf_info.export_into_deep_subfolder:
        deep_sub = beatmap_info.parse_replacement_fields(beatmap_type_conf_info.deep_subfolder_name)
        deep_sub = conf_info.replace_illegal_chars(deep_sub)
        p_out_deep = Path(f'{p_out_sub}/{deep_sub}')
        p_out_deep.mkdir(parents=True, exist_ok=True)

    # Copy the song to the output folder if it hasn't been copied yet
    p_out_song = None
    copy_info = ExtractionInfo(p_in_sub, p_out_deep, beatmap_info, conf_info, beatmap_type_conf_info)
    if beatmap_info.audio_filename not in copied_audio and beatmap_info.audio_filename:
        copied_audio.add(beatmap_info.audio_filename)
        p_out_song = copy_song(copy_info)

    # Copy the background to output folder / metadata if it hasn't been copied yet
    # If exporting all bgs as separate, proceed if bg wasn't exported
    # If exporting one bg as meta, proceed if audio file was copied
    # Unimplemented:
    # If exporting one bg per audio file as separate, proceed if bg wasn't exported and audio file was copied
    # If exporting all bgs as meta, proceed if either bg wasn't exported or audio file was copied
    match (beatmap_type_conf_info.bg_export_mode):
        case BGExportMode.AS_SEPARATE:
            if beatmap_info.bg_filename not in copied_bgs and beatmap_info.bg_filename:
                copied_bgs.add(beatmap_info.bg_filename)
                copy_bg_as_separate(copy_info)
        case BGExportMode.AS_META_IF_MISSING | BGExportMode.AS_META_ALWAYS:
            if p_out_song:
                copy_bg_as_meta(copy_info, p_out_song)

# Copies the audio file and writes the metadata
# Returns the path to the copied song
def copy_song(copy_info: ExtractionInfo) -> Path:
    # Unpack everything
    p_in_sub, p_out_deep, beatmap_info, conf_info, beatmap_type_conf_info = copy_info.unpack()

    # Locate the source and destination paths of song copy process
    out_song = beatmap_info.parse_replacement_fields(beatmap_type_conf_info.song_filename) # Parse replacement fields
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
    if not (beatmap_type_conf_info.overwrite_existing_files or not p_out_song.is_file()):
        return None # Return None to signal that no copy happened
    shutil.copy2(p_in_song, p_out_song)

    # No need to write metadata if meta_write_mode is NEVER, so return
    if beatmap_type_conf_info.meta_write_mode == MetaWriteMode.NEVER:
        return p_out_song # Return path to copied song

    # Fill in the title and artist metadata if it's missing or if meta_write_mode is ALWAYS
    f = music_tag.load_file(p_out_song)
    if not f['title'].values or beatmap_type_conf_info.meta_write_mode == MetaWriteMode.ALWAYS:
        f['title'] = beatmap_info.parse_replacement_fields(beatmap_type_conf_info.title_meta)
    if not f['artist'].values or beatmap_type_conf_info.meta_write_mode == MetaWriteMode.ALWAYS:
        f['artist'] = beatmap_info.parse_replacement_fields(beatmap_type_conf_info.artist_meta)
    f.save()
    return p_out_song # Return path to copied song

# Copies the background as a separate file
def copy_bg_as_separate(copy_info: ExtractionInfo) -> None:
    # Unpack everything
    p_in_sub, p_out_deep, beatmap_info, conf_info, beatmap_type_conf_info = copy_info.unpack()

    # Locate the source and destination paths of background copy process
    out_bg = beatmap_info.parse_replacement_fields(beatmap_type_conf_info.bg_filename) # Parse replacement fields
    bg_ext = parse_filename(beatmap_info.bg_filename)[1] # Get image extension
    out_bg = fr'{conf_info.replace_illegal_chars(out_bg)}{bg_ext}' # Re-add image extension
    p_in_bg = Path(fr'{p_in_sub}/{beatmap_info.bg_filename}') # Get source path
    p_out_bg = Path(fr'{p_out_deep}/{out_bg}') # Get destination path

    # If background file is not found, attempt to find a file with the same name but doesn't match case.
    # If that fails, print warning and return
    if not p_in_bg.is_file():
        p_in_bg = find_case_insensitive_file(p_in_sub, p_in_bg)
        if not p_in_bg:
            print(f"\033[33mWarning:\033[0m the background file from {beatmap_info.osu_filename} was listed but couldn't be found.")
            return

    # If overwrite_existing_files is True or the destination file doesn't exist, copy
    if not p_out_bg.is_file() or beatmap_type_conf_info.overwrite_existing_files:
        shutil.copy2(p_in_bg, p_out_bg)

# Copies the background to the song's metadata
def copy_bg_as_meta(copy_info: ExtractionInfo, p_out_song: Path) -> None:
    # Unpack everything
    p_in_sub, p_out_deep, beatmap_info, conf_info, beatmap_type_conf_info = copy_info.unpack()

    # Locate the source path of background
    p_in_bg = Path(fr'{p_in_sub}/{beatmap_info.bg_filename}')

    if p_out_song.name == r'DJ Sharpnel - TAKECORE OF YOURSELF [#Marathon] 1625737.mp3':
        breakpoint()

    # If background file is not found, attempt to find a file with the same name but doesn't match case.
    # If that fails, print warning and return
    if not p_in_bg.is_file():
        p_in_bg = find_case_insensitive_file(p_in_sub, p_in_bg)
        if not p_in_bg:
            print(f"\033[33mWarning:\033[0m the background file from {beatmap_info.osu_filename} was listed but couldn't be found.")
            return

    # If the artwork metadata exists and bg_export_mode is not AS_META_ALWAYS, return
    f = music_tag.load_file(p_out_song)
    if not (not f['artwork'].values or beatmap_type_conf_info.bg_export_mode == BGExportMode.AS_META_ALWAYS):
        return

    # Copy the background as metadata
    with open(p_in_bg, 'rb') as img_in:
        f['artwork'] = img_in.read()
    f.save()

# WHY DO YOU ALLOW CASE INSENSITIVE FILENAMES IN YOUR .OSU FILE PEPPY WTF
def find_case_insensitive_file(p_in_sub: Path, p_in_file: Path) -> Path | None:
    # Look through every path recursively and return the match if found
    for sub_path in p_in_sub.rglob('*'):
        if sub_path.is_file() and str(sub_path.resolve()).lower() == str(p_in_file.resolve()).lower():
            return sub_path

    return None # If no match, return None
