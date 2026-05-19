from osu_song_extractor.extract import extract_beatmap_set_info, BeatmapInfo, extract_all_beatmaps, extract_beatmap
from osu_song_extractor.conf import read_conf_file
from pathlib import Path
import pytest
import shutil
import music_tag

def test_extract_beatmap_set_info():
    # Extract the beatmap infos from the freedom dive beatmap set
    p_in_sub = Path('tests/test_extract/Songs/173612 xi - FREEDOM DiVE')
    beatmap_set_info = extract_beatmap_set_info(p_in_sub)
    assert len(beatmap_set_info) == 9
    for beatmap_info in beatmap_set_info:
        assert beatmap_info.audio_filename == 'Freedom Dive'
        assert beatmap_info.audio_ext == 'mp3'
        assert beatmap_info.title == 'FREEDOM DiVE'
        assert beatmap_info.artist == 'xi'
        assert beatmap_info.bg_filename == 'background desuuu'
        assert beatmap_info.bg_ext == 'jpg'
        assert beatmap_info.beatmap_set_id == 173612

    # check that all versions are present
    assert any(beatmap_info.version == r'4K Another' for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.version == r'4K Hyper' for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.version == r'4K Normal' for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.version == r"Blocko's 7K Another" for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.version == r"Blocko's 7K Black Another" for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.version == r"Blocko's 7K Normal" for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.version == r"Dain's 7K Light" for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.version == r"Fullerene's 4K DIMENSIONS" for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.version == r"Tear's 7K Hyper" for beatmap_info in beatmap_set_info)

    # check that all beatmap_ids are present
    assert any(beatmap_info.beatmap_id == 419485 for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.beatmap_id == 420005 for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.beatmap_id == 423649 for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.beatmap_id == 421369 for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.beatmap_id == 480207 for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.beatmap_id == 420781 for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.beatmap_id == 502132 for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.beatmap_id == 473228 for beatmap_info in beatmap_set_info)
    assert any(beatmap_info.beatmap_id == 420779 for beatmap_info in beatmap_set_info)

def test_extract_beatmap_info_missing_bg():
    # Extract the beatmap info from missing-bg.osu
    beatmap_info = BeatmapInfo()
    with open('tests/test_extract/Songs/Missing Background/missing_bg.osu', 'r') as file:
        beatmap_info.extract_beatmap_info(file)

    assert beatmap_info.audio_filename == 'test'
    assert beatmap_info.audio_ext == ''
    assert beatmap_info.title == 'FREEDOM DiVE'
    assert beatmap_info.artist == 'xi'
    assert beatmap_info.version == '4K Another'
    assert beatmap_info.bg_filename == ''
    assert beatmap_info.bg_ext == ''
    assert beatmap_info.beatmap_id == 419485
    assert beatmap_info.beatmap_set_id == 173612

def test_no_overwrite_existing_files():
    # Delete tmp directory if it exists
    shutil.rmtree('tests/tmp', ignore_errors=True)
    # Create the directory
    Path('tests/tmp/extracted/xi - FREEDOM DiVE 173612').mkdir(parents=True, exist_ok=True)

    # Create an mp3 file with just 'Hello' in it
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/xi - FREEDOM DiVE.mp3', 'wb') as file:
        file.write(b'\x48\x65\x6c\x6c\x6f')
    # Create a jpg file with just 'Hello' in it
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/background desuuu.jpg', 'wb') as file:
        file.write(b'\x48\x65\x6c\x6c\x6f')

    # Call extract_beatmap()
    conf_info = read_conf_file('tests/test_extract/no_overwrite.cfg')
    p_in_sub = Path('tests/test_extract/Songs/173612 xi - FREEDOM DiVE')
    extract_beatmap(p_in_sub, conf_info)

    # Test that both files didn't get overwritten
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/xi - FREEDOM DiVE.mp3', 'rb') as file:
        assert b'\x48\x65\x6c\x6c\x6f' == file.read(5)
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/background desuuu.jpg', 'rb') as file:
        assert b'\x48\x65\x6c\x6c\x6f' == file.read(5)

def test_overwrite_existing_files():
    # Delete tmp directory if it exists
    shutil.rmtree('tests/tmp', ignore_errors=True)
    # Create the directory
    Path('tests/tmp/extracted/xi - FREEDOM DiVE 173612').mkdir(parents=True, exist_ok=True)

    # Create an mp3 file with just 'Hello' in it
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/xi - FREEDOM DiVE.mp3', 'wb') as file:
        file.write(b'\x48\x65\x6c\x6c\x6f')
    # Create a jpg file with just 'Hello' in it
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/background desuuu.jpg', 'wb') as file:
        file.write(b'\x48\x65\x6c\x6c\x6f')

    # Call extract_beatmap()
    conf_info = read_conf_file('tests/test_extract/overwrite.cfg')
    p_in_sub = Path('tests/test_extract/Songs/173612 xi - FREEDOM DiVE')
    extract_beatmap(p_in_sub, conf_info)

    # Test that both files got overwritten
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/xi - FREEDOM DiVE.mp3', 'rb') as file:
        assert b'\x48\x65\x6c\x6c\x6f' != file.read(5)
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/background desuuu.jpg', 'rb') as file:
        assert b'\x48\x65\x6c\x6c\x6f' != file.read(5)

# - export_into_subfolders = False
# - song_filename = "<AudioFilename>"
# - meta_write_mode = ALWAYS
# - title_meta = "<BeatmapID>"
# - bg_export_mode = AS_META_ALWAYS
def test_bg_export_as_meta_always():
    # Delete tmp directory if it exists
    shutil.rmtree('tests/tmp', ignore_errors=True)

    # Call extract_beatmap()
    conf_info = read_conf_file('tests/test_extract/bg_export_as_meta_always.cfg')
    p_in_sub = Path('tests/test_extract/Songs/173612 xi - FREEDOM DiVE')
    extract_beatmap(p_in_sub, conf_info)

    # Assert that the title metadata and background metadata are written correctly
    p_out_song = Path('tests/tmp/extracted/Freedom Dive.mp3')
    with open('tests/test_extract/Songs/173612 xi - FREEDOM DiVE/background desuuu.jpg', 'rb') as file:
        f = music_tag.load_file(p_out_song)
        # assert that one of the beatmap ids got written to the title
        assert f['title'].first in ['419485', '420005', '423649', '421369', '480207', '420781', '502132', '473228', '420779']
        assert f['artwork'].first.data == file.read()

# - meta_write_mode = NEVER test
# - bg_export_mode = NEVER test
def test_only_copy_song():
    # Delete tmp directory if it exists
    shutil.rmtree('tests/tmp', ignore_errors=True)

    # Create a copy of the original beatmap
    p_in_sub = Path('tests/test_extract/Songs/173612 xi - FREEDOM DiVE')
    p_in_sub_copy = Path('tests/tmp/173612 xi - FREEDOM DiVE no meta')
    shutil.copytree(p_in_sub, p_in_sub_copy, dirs_exist_ok=True)

    # Remove all the metadata in the copied audio file
    p_in_song = Path('tests/tmp/173612 xi - FREEDOM DiVE no meta/Freedom Dive.mp3')
    f = music_tag.load_file(p_in_song)
    f.remove_tag('title')
    f.remove_tag('artist')
    f.remove_tag('artwork')
    f.save()

    # Call extract_beatmap()
    conf_info = read_conf_file('tests/test_extract/only_copy_song.cfg')
    extract_beatmap(p_in_sub_copy, conf_info)

    # Check that all the metadata is untouched
    p_out_song = Path('tests/tmp/extracted/Freedom Dive.mp3')
    f = music_tag.load_file(p_out_song)
    assert not f['title'].first
    assert not f['artist'].first
    assert not f['artwork'].first

    # Check that there is no background file
    p_out = Path(conf_info.output_dir)
    assert len(list(p_out.glob('*.osu'))) == 0

# - bg_export_mode = AS_META_IF_MISSING test
# - something surronded with angle brackets but is not a valid replacement field
def test_bg_export_as_meta_if_missing():
    # Delete tmp directory if it exists
    shutil.rmtree('tests/tmp', ignore_errors=True)

    # Call extract_beatmap()
    conf_info = read_conf_file('tests/test_extract/bg_export_as_meta_if_missing.cfg')
    p_in_sub = Path('tests/test_extract/Songs/173612 xi - FREEDOM DiVE')
    extract_beatmap(p_in_sub, conf_info)

    # Check that all the metadata is correct
    p_out_song = Path('tests/tmp/extracted/Freedom Dive.mp3')
    with open('tests/test_extract/Songs/173612 xi - FREEDOM DiVE/background desuuu.jpg', 'rb') as file:
        f = music_tag.load_file(p_out_song)
        assert f['title'].first == r'<oogabooga>'
        assert f['artwork'].first.data != file.read()

# Tests extracting a bunch of invalid osu beatmaps in tests/test_extract/Invalid_Songs
def test_extract_all_invalid_beatmaps():
    shutil.rmtree('tests/tmp', ignore_errors=True)
    conf_info = read_conf_file('tests/test_extract/invalid_songs.cfg')
    extract_all_beatmaps(conf_info)
    for path in Path('tests/tmp/extracted').rglob('*'):
        assert not path.is_file() # Test that nothing got copied

# Tests extracting a bunch of real osu beatmaps in tests/test_extract/Songs
# User has to manually check tests/extracted to see if it's correct
def test_extract_all_beatmaps():
    shutil.rmtree('tests/extracted', ignore_errors=True)
    conf_info = read_conf_file('tests/test_extract/default.cfg')
    extract_all_beatmaps(conf_info)
    print("\033[32mtest_extract_all_beatmaps:\033[0m please manually check tests/extracted to see if it's correct")
