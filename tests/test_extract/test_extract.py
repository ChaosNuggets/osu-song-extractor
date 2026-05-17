from osu_song_extractor.extract import extract_beatmap_set_info, BeatmapInfo, extract_all_beatmaps, extract_beatmap
from osu_song_extractor.conf import read_conf_file
from pathlib import Path
import pytest
import shutil

def test_extract_beatmap_set_info():
    # Extract the beatmap infos from the freedom dive beatmap set
    p_in_sub = Path('tests/test_extract/173612 xi - FREEDOM DiVE')
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
    with open('tests/test_extract/missing_bg.osu', 'r') as file:
        beatmap_info.extract_beatmap_info(file)

    assert beatmap_info.audio_filename == 'Freedom Dive'
    assert beatmap_info.audio_ext == ''
    assert beatmap_info.title == 'FREEDOM DiVE'
    assert beatmap_info.artist == 'xi'
    assert beatmap_info.version == '4K Another'
    assert beatmap_info.bg_filename == ''
    assert beatmap_info.bg_ext == ''
    assert beatmap_info.beatmap_id == 419485
    assert beatmap_info.beatmap_set_id == 173612

def test_no_overwrite_existing_files():
    # Delete directory if it exists
    shutil.rmtree('tests/tmp/extracted', ignore_errors=True)
    # Create the directory
    Path('tests/tmp/extracted/xi - FREEDOM DiVE 173612').mkdir(parents=True, exist_ok=True)

    # Create an mp3 file with just 'Hello' in it
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/xi - FREEDOM DiVE.mp3', 'wb') as file:
        file.write(b'\x48\x65\x6c\x6c\x6f')
    # Ensure that the write succeeded
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/xi - FREEDOM DiVE.mp3', 'rb') as file:
        assert b'\x48\x65\x6c\x6c\x6f' == file.read(5)

    # Call extract_beatmap()
    conf_info = read_conf_file('tests/test_extract/tmp_no_overwrite.cfg')
    p_in_sub = Path('tests/test_extract/173612 xi - FREEDOM DiVE')
    extract_beatmap(p_in_sub, conf_info)

    # Test that it didn't get overwritten
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/xi - FREEDOM DiVE.mp3', 'rb') as file:
        assert b'\x48\x65\x6c\x6c\x6f' == file.read(5)

def test_overwrite_existing_files():
    # Delete directory if it exists
    shutil.rmtree('tests/tmp/extracted', ignore_errors=True)
    # Create the directory
    Path('tests/tmp/extracted/xi - FREEDOM DiVE 173612').mkdir(parents=True, exist_ok=True)

    # Create an mp3 file with just 'Hello' in it
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/xi - FREEDOM DiVE.mp3', 'wb') as file:
        file.write(b'\x48\x65\x6c\x6c\x6f')
    # Ensure that the write succeeded
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/xi - FREEDOM DiVE.mp3', 'rb') as file:
        assert b'\x48\x65\x6c\x6c\x6f' == file.read(5)

    # Call extract_beatmap()
    conf_info = read_conf_file('tests/test_extract/tmp_overwrite.cfg')
    p_in_sub = Path('tests/test_extract/173612 xi - FREEDOM DiVE')
    extract_beatmap(p_in_sub, conf_info)

    # Test that it got overwritten
    with open('tests/tmp/extracted/xi - FREEDOM DiVE 173612/xi - FREEDOM DiVE.mp3', 'rb') as file:
        assert b'\x48\x65\x6c\x6c\x6f' != file.read(5)

def test_extract_all_beatmaps():
    shutil.rmtree('tests/extracted', ignore_errors=True)
    conf_info = read_conf_file('tests/test_extract/default.cfg')
    extract_all_beatmaps(conf_info)
    print("test_extract_all_beatmaps: please manually check tests/extracted to see if it's correct")
