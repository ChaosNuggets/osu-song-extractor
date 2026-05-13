import sys
import os
sys.path.append(os.path.expanduser(r'~/Projects/Osu-Song-Extractor'))
from read_conf_file import read_conf_file, MetaWriteMode, BGExportMode
import pytest

def test_normal_cfg():
    conf_values = read_conf_file('tests/normal-test.cfg')
    assert conf_values.input_dir == '~/Music/Songs'
    assert conf_values.output_dir == '~/Music/Extracted-Songs'

def test_many_spaces_cfg():
    conf_values = read_conf_file('tests/many-spaces-test.cfg')
    assert conf_values.input_dir == '~/Music/Songs'
    assert conf_values.output_dir == r'~\Music\Extracted-Songs'

def test_invalid_key_cfg():
    with pytest.raises(KeyError):
        conf_values = read_conf_file('tests/invalid-key.cfg')

def test_missing_key_cfg():
    with pytest.raises(KeyError):
        conf_values = read_conf_file('tests/missing-key.cfg')

def test_defaults():
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
