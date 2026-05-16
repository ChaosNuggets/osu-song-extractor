from osu_song_extractor.conf import read_conf_file, MetaWriteMode, BGExportMode
import pytest

def test_normal_cfg():
    conf_info = read_conf_file('tests/normal-test.cfg')
    assert conf_info.input_dir == 'tests'
    assert conf_info.output_dir == 'tests/extracted'

def test_many_spaces_cfg():
    conf_info = read_conf_file('tests/many-spaces-test.cfg')
    assert conf_info.input_dir == '~/Music/Songs'
    assert conf_info.output_dir == r'~\Music\Extracted-Songs'

def test_invalid_general_key_cfg():
    with pytest.raises(KeyError):
        conf_info = read_conf_file('tests/invalid-general-key.cfg')

def test_missing_key_cfg():
    with pytest.raises(KeyError):
        conf_info = read_conf_file('tests/missing-key.cfg')

def test_default_cfg():
    conf = read_conf_file(r'tests/normal-test.cfg')
    assert conf.export_into_subfolders == True
    assert conf.subfolder_name == r'<Artist> - <Title> <BeatmapSetID>'
    assert conf.illegal_char_override == r'-'

    assert conf.one_bg_one_song.export_into_deep_subfolder == False
    assert conf.mult_bg_one_song.export_into_deep_subfolder == False
    assert conf.one_bg_mult_song.export_into_deep_subfolder == False
    assert conf.mult_bg_mult_song.export_into_deep_subfolder == True

    assert conf.mult_bg_mult_song.deep_subfolder_name == r'<Version>'

    assert conf.one_bg_one_song.overrite_existing_files == False
    assert conf.mult_bg_one_song.overrite_existing_files == False
    assert conf.one_bg_mult_song.overrite_existing_files == False
    assert conf.mult_bg_mult_song.overrite_existing_files == False

    assert conf.one_bg_one_song.song_filename == r'<Artist> - <Title>'
    assert conf.mult_bg_one_song.song_filename == r'<Artist> - <Title>'
    assert conf.one_bg_mult_song.song_filename == r'<Artist> - <Title> [<Version>]'
    assert conf.mult_bg_mult_song.song_filename == r'<Artist> - <Version>'

    assert conf.one_bg_one_song.meta_write_mode == MetaWriteMode.IF_MISSING 
    assert conf.mult_bg_one_song.meta_write_mode == MetaWriteMode.IF_MISSING 
    assert conf.one_bg_mult_song.meta_write_mode == MetaWriteMode.IF_MISSING 
    assert conf.mult_bg_mult_song.meta_write_mode == MetaWriteMode.IF_MISSING 

    assert conf.one_bg_one_song.title_meta == r'<Title>'
    assert conf.mult_bg_one_song.title_meta == r'<Title>'
    assert conf.one_bg_mult_song.title_meta == r'<Title> [<Version>]'
    assert conf.mult_bg_mult_song.title_meta == r'<Version>'
    
    assert conf.one_bg_one_song.artist_meta == r'<Artist>'
    assert conf.mult_bg_one_song.artist_meta == r'<Artist>'
    assert conf.one_bg_mult_song.artist_meta == r'<Artist>'
    assert conf.mult_bg_mult_song.artist_meta == r'<Artist>'

    assert conf.one_bg_one_song.bg_export_mode == BGExportMode.AS_SEPARATE
    assert conf.mult_bg_one_song.bg_export_mode == BGExportMode.AS_SEPARATE
    assert conf.one_bg_mult_song.bg_export_mode == BGExportMode.AS_SEPARATE
    assert conf.mult_bg_mult_song.bg_export_mode == BGExportMode.AS_SEPARATE

    assert conf.one_bg_one_song.bg_filename == r'<BackgroundFilename>'
    assert conf.mult_bg_one_song.bg_filename == r'<BackgroundFilename>'
    assert conf.one_bg_mult_song.bg_filename == r'<BackgroundFilename>'
    assert conf.mult_bg_mult_song.bg_filename == r'<BackgroundFilename>'

def test_custom_cfg():
    conf = read_conf_file(r'tests/custom.cfg')
    assert conf.input_dir == r"C:\Users\chaos\AppData\Local\osu!\Songs"
    assert conf.output_dir == r"C:\Users\chaos\Music\Extracted-Songs"
    assert conf.export_into_subfolders == True
    assert conf.subfolder_name == r"<Artist> - <Title> <BeatmapSetID>"
    assert conf.illegal_char_override == "-"

    assert conf.one_bg_one_song.export_into_deep_subfolder == False
    assert conf.one_bg_one_song.deep_subfolder_name == r"<Version>"
    assert conf.one_bg_one_song.overrite_existing_files == False
    assert conf.one_bg_one_song.song_filename == r"<Artist> - <Title>"
    assert conf.one_bg_one_song.meta_write_mode == MetaWriteMode.IF_MISSING 
    assert conf.one_bg_one_song.title_meta == r"<Title>"
    assert conf.one_bg_one_song.artist_meta == r"<Artist>"
    assert conf.one_bg_one_song.bg_export_mode == BGExportMode.AS_SEPARATE
    assert conf.one_bg_one_song.bg_filename == r"<BackgroundFilename>"

    assert conf.mult_bg_one_song.export_into_deep_subfolder == True
    assert conf.mult_bg_one_song.deep_subfolder_name == r"<AudioFilename>"
    assert conf.mult_bg_one_song.overrite_existing_files == True
    assert conf.mult_bg_one_song.song_filename == r" <BackgroundFilename> <BeatmapID>"
    assert conf.mult_bg_one_song.meta_write_mode == MetaWriteMode.ALWAYS
    assert conf.mult_bg_one_song.title_meta == r"EEE <ooga booga>"
    assert conf.mult_bg_one_song.artist_meta == r"< lol"
    assert conf.mult_bg_one_song.bg_export_mode == BGExportMode.AS_META_IF_MISSING

    assert conf.one_bg_mult_song.song_filename == r"<BeatmapSetID> <BeatmapID>"
    
    assert conf.mult_bg_mult_song.song_filename == r"<AudioFilename>"

def test_invalid_x_bg_x_song_key_cfg():
    with pytest.raises(KeyError):
        conf_info = read_conf_file('tests/invalid-x_bg_x_song-key.cfg')

def test_invalid_bool_cfg():
    with pytest.raises(ValueError):
        conf_info = read_conf_file('tests/invalid-bool.cfg')

def test_invalid_enum_cfg():
    with pytest.raises(ValueError):
        conf_info = read_conf_file('tests/invalid-enum.cfg')
