from dataclasses import dataclass, asdict, field
import re
from enum import Enum, auto
from osu_song_extractor.parse_utils import parse_string, parse_bool, parse_enum
import os

# Matches with any illegal filename chars
illegal_pat = re.compile(r'[<>:"\/\\|?*]')

# Enum that stores whether the user wants to always write the song metadata,
# write the metadata only if missing, or never write the metadata
class MetaWriteMode(Enum):
    NEVER = auto()
    IF_MISSING = auto()
    ALWAYS = auto()

# Stores how the user wants to export their backgrounds (never,
# as a separate file in the same directory, or as metadata inside of the audio file)
class BGExportMode(Enum):
    NEVER = auto()
    AS_SEPARATE = auto()
    AS_META_IF_MISSING = auto()
    AS_META_ALWAYS = auto()

# Stores configuration options for a specific type of beatmap. See the "[x_bg_x_song] Options" section in docs/configuration.md for more info.
@dataclass
class BeatmapTypeConfInfo:
    export_into_deep_subfolder: bool = False
    deep_subfolder_name: str = r'<Version>'
    overwrite_existing_files: bool = False
    song_filename: str = r'<Artist> - <Title> <BeatmapID>'
    meta_write_mode: MetaWriteMode = MetaWriteMode.IF_MISSING 
    title_meta: str = r'<Title>'
    artist_meta: str = r'<Artist>'
    bg_export_mode: BGExportMode = BGExportMode.AS_META_IF_MISSING
    bg_filename: str = r'<BackgroundFilename>'

    # Parse option and modify the correct member variables for the [x_bg_x_song] sections
    def init_from_conf(self, option: str, value: str) -> None:
        match option:
            case 'export_into_deep_subfolder':
                self.export_into_deep_subfolder = parse_bool(value)
            case 'deep_subfolder_name':
                self.deep_subfolder_name = parse_string(value)
            case 'overwrite_existing_files':
                self.overwrite_existing_files = parse_bool(value)
            case 'song_filename':
                self.song_filename = parse_string(value)
            case 'meta_write_mode':
                self.meta_write_mode = parse_enum(value, MetaWriteMode)
            case 'title_meta':
                self.title_meta = parse_string(value)
            case 'artist_meta':
                self.artist_meta = parse_string(value)
            case 'bg_export_mode':
                self.bg_export_mode = parse_enum(value, BGExportMode)
            case 'bg_filename':
                self.bg_filename = parse_string(value)
            case _:
                raise KeyError(f'Unknown configuration option "{option}" in section [x_bg_x_song]')

# The different sections of the configuration file
class ConfSection(Enum):
    GENERAL  = auto()
    ONE_SONG = auto()
    RATES    = auto()
    MAP_PACK = auto()

# Stores all the configuration options. See the "Configuration Options" section in docs/configuration.md for more info.
@dataclass
class ConfInfo:
    # General configuration options. See the "[General] Options" section in docs/configuration.md for more info.
    input_dir: str = ''
    output_dir: str = ''
    export_into_subfolders: bool = False # TODO: CHANGE IN DOCUMENTATION
    subfolder_name: str = r'<Artist> - <Title> <BeatmapSetID>'
    illegal_char_override: str = '-'
    beatmap_type_cutoff: float = 0.7

    # Configuration options for each type of beatmap.
    one_song: BeatmapTypeConfInfo = field(default_factory=BeatmapTypeConfInfo)
    rates:    BeatmapTypeConfInfo = field(default_factory=BeatmapTypeConfInfo)
    map_pack: BeatmapTypeConfInfo = field(default_factory=BeatmapTypeConfInfo)

    # Fills in the special defaults for rates and map_pack
    def __post_init__(self):
        self.rates.song_filename = r'<Artist> - <Title> [<Version>] <BeatmapID>'
        self.rates.title_meta = r'<Title> [<Version>]'

        self.map_pack.song_filename = r'<Artist> - <Version> <BeatmapID>'
        self.map_pack.title_meta = r'<Version>'

    # Fills in ConfInfo based on the option and value specified
    # in the config file
    def init_from_conf(self, option: str, value: str, section: ConfSection) -> None:
        # Parse section so we modify the correct XBGXSongConfInfo instance
        match section:
            case ConfSection.ONE_SONG:
                beatmap_type = self.one_song
            case ConfSection.RATES:
                beatmap_type = self.rates
            case ConfSection.MAP_PACK:
                beatmap_type = self.map_pack
            case _:
                beatmap_type = None

        # Call the correct initialization function based on section
        if beatmap_type == None:
            self.init_general_conf(option, value)
        else:
            beatmap_type.init_from_conf(option, value)

    # Parse option and modify the correct member variables for the General section
    def init_general_conf(self, option: str, value: str) -> None:
        match option:
            case 'input_dir':
                self.input_dir = os.path.expanduser(parse_string(value).rstrip('/\\'))
            case 'output_dir':
                self.output_dir = os.path.expanduser(parse_string(value).rstrip('/\\'))
            case 'export_into_subfolders':
                self.export_into_subfolders = parse_bool(value)
            case 'subfolder_name':
                self.subfolder_name = parse_string(value)
            case 'illegal_char_override':
                self.illegal_char_override = parse_string(value)
            case 'beatmap_type_cutoff':
                self.beatmap_type_cutoff = float(value)
            case _:
                raise KeyError(fr'Unknown configuration option "{option}" in section [General]')

    def replace_illegal_chars(self, value: str) -> str:
        return illegal_pat.sub(self.illegal_char_override, value)

# Returns the input_dir and output_dir entries in osu-song-extractor.cfg
def read_conf_file(conf_file: str) -> ConfInfo:
    conf_info = ConfInfo()

    # Compiling is efficient for loops
    # Pattern looks for "<config_option>=<value>" and places
    # config option in first group and value in second group
    conf_pat = re.compile(r'^([^=#\n\r]*)=([^#\n\r]*)')

    # Looks for something surrounded by square brackets [] and puts the inside text into group 1
    section_pat = re.compile(r'^\[(.*)\]')

    # Read configuration file
    with open(conf_file, 'r') as file:
        section = ConfSection.GENERAL
        for line in file:
            # Search for section header pattern in file
            section_match = section_pat.search(line)
            if section_match:
                section = parse_enum(section_match.group(1), ConfSection)
                continue

            # Search for configuration option pattern in file
            conf_match = conf_pat.search(line)
            if not conf_match:
                continue

            # Parse the configuration option
            option = conf_match.group(1).strip()
            value = conf_match.group(2).strip()
            conf_info.init_from_conf(option, value, section)

    # Raise an error if options with no defaults are missing from the config file
    for key, value in asdict(conf_info).items():
        if not value and type(value) is str:
            raise KeyError(f'Please specify {key} in the configuration file')
    return conf_info
