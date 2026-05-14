from dataclasses import dataclass, asdict, field
import re
from enum import Enum, auto

# Looks for something surrounded by quotation marks and puts it into group 1
string_pattern = re.compile(r'"(.*)"')

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
    AS_META = auto()

# Stores configuration options for a specific type of beatmap. See the "[x_bg_x_song] Options" section in docs/configuration.md for more info.
@dataclass
class BeatmapTypeConf:
    export_into_deep_subfolder: bool = False
    deep_subfolder_name: str = r'<Version>'
    overrite_existing_files: bool = False
    song_filename: str = r'<Artist> - <Title>'
    meta_write_mode: MetaWriteMode = MetaWriteMode.IF_MISSING 
    title_meta: str = r'<Title>'
    artist_meta: str = r'<Artist>'
    bg_export_mode: BGExportMode = BGExportMode.AS_SEPARATE
    bg_filename: str = r'<BackgroundFilename>'

    # Parse option and modify the correct member variables for the [x_bg_x_song] sections
    def init_from_conf(self, option: str, value: str) -> None:
        match option:
            case 'export_into_deep_subfolder':
                self.export_into_deep_subfolder = parse_bool(value)
            case 'deep_subfolder_name':
                self.deep_subfolder_name = parse_string(value)
            case 'overrite_existing_files':
                self.overrite_existing_files = parse_bool(value)
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
    GENERAL = auto()
    ONE_BG_ONE_SONG = auto()
    MULT_BG_ONE_SONG = auto()
    ONE_BG_MULT_SONG = auto()
    MULT_BG_MULT_SONG = auto()

# Stores all the configuration options. See the "Configuration Options" section in docs/configuration.md for more info.
@dataclass
class ConfValues:
    # General configuration options. See the "[General] Options" section in docs/configuration.md for more info.
    input_dir: str = ''
    output_dir: str = ''
    export_into_subfolders: bool = True
    subfolder_name: str = r'<Artist> - <Title> <BeatmapSetID>'
    illegal_char_override: str = '-'

    # Configuration options for each type of beatmap. 
    one_bg_one_song: BeatmapTypeConf = field(default_factory=BeatmapTypeConf)
    mult_bg_one_song: BeatmapTypeConf = field(default_factory=BeatmapTypeConf)
    one_bg_mult_song: BeatmapTypeConf = field(default_factory=BeatmapTypeConf)
    mult_bg_mult_song: BeatmapTypeConf = field(default_factory=BeatmapTypeConf)

    # Fills in the special defaults for one_bg_mult_song and mult_bg_mult_song
    def __post_init__(self):
        self.one_bg_mult_song.song_filename = r'<Artist> - <Title> [<Version>]'
        self.one_bg_mult_song.title_meta = r'<Title> [<Version>]'

        self.mult_bg_mult_song.export_into_deep_subfolder = True
        self.mult_bg_mult_song.song_filename = r'<Artist> - <Version>'
        self.mult_bg_mult_song.title_meta = r'<Version>'

    # Fills in ConfValues based on the option and value specified
    # in the config file
    def init_from_conf(self, option: str, value: str, section: ConfSection) -> None:
        # Parse section so we modify the correct BeatmapTypeConf instance
        match section:
            case ConfSection.ONE_BG_ONE_SONG:
                x_bg_x_song = self.one_bg_one_song
            case ConfSection.MULT_BG_ONE_SONG:
                x_bg_x_song = self.mult_bg_one_song
            case ConfSection.ONE_BG_MULT_SONG:
                x_bg_x_song = self.one_bg_mult_song
            case ConfSection.MULT_BG_MULT_SONG:
                x_bg_x_song = self.mult_bg_mult_song
            case _:
                x_bg_x_song = None

        # Call the correct initialization function based on section
        if x_bg_x_song == None:
            init_general_conf(option, value)
        else:
            x_bg_x_song.init_from_conf(option, value)

    # Parse option and modify the correct member variables for the General section
    def init_general_conf(self, option: str, value: str) -> None:
        match option:
            case 'input_dir':
                self.input_dir = parse_string(value).rstrip('/\\')
            case 'output_dir':
                self.output_dir = parse_string(value).rstrip('/\\')
            case 'export_into_subfolders':
                self.export_into_subfolders = parse_bool(value)
            case 'subfolder_name':
                self.subfolder_name = parse_string(value)
            case 'illegal_char_override':
                    self.illegal_char_override = parse_string(value)
            case _:
                raise KeyError(fr'Unknown configuration option "{option}" in section [General]')

# Strips the string of its quotation marks
def parse_string(value: str) -> str:
    string_match = string_pattern.search()
    if string_match:
        return string_match.group(1)

    return value.strip('\n\r\t \"')

# Turns a string ("True" or "False") into a bool
def parse_bool(value: str) -> bool:
    match value.strip().lower():
        case 'true':
            return True
        case 'false':
            return False
        case _:
            raise ValueError(f'Cannot parse {value} as bool')

# Turns a string into an enum member
def parse_enum(value: str, EnumCls: type[Enum]) -> Enum:
    for member in EnumCls:
        if value.strip().lower() == member.name.lower():
            return member

    raise ValueError(f'Cannot parse {value} as {EnumCls}')

# Returns the input_dir and output_dir entries in osu-song-extractor.cfg
def read_conf_file(conf_file: str) -> ConfValues:
    conf_values = ConfValues()

    # Compiling is efficient for loops
    # Pattern looks for "<config_option>=<value>" and places
    # config option in first group and value in second group
    conf_pattern = re.compile(r'^([^=#]*)=([^#\n]*)')

    # Search for configuration option pattern in file
    with open(conf_file, 'r') as file:
        for line in file:
            conf_match = conf_pattern.search(line)
            if not conf_match:
                continue

            # Parse the configuration option
            option = conf_match.group(1).strip()
            value = conf_match.group(2).strip()
            # TODO: add section code here
            conf_values.init_from_conf(option, value)

    # Raise an error if something is missing from the config file
    for key, value in asdict(conf_values).items():
        if not value:
            raise KeyError(f'Please specify {key} in the configuration file')
    return conf_values
