from osu_song_extractor.extract import extract_beatmap_set_info, BeatmapInfo
from pathlib import Path
import pytest

def test_extract_beatmap_set_info():
    # Extract the beatmap infos from the freedom dive beatmap set
    p_in_sub = Path('tests/173612 xi - FREEDOM DiVE')
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
    with open('tests/missing-bg.osu', 'r') as file:
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

def test_extract_beatmap_info_missing_title():
    # Extract the beatmap info from missing-title.osu
    beatmap_info = BeatmapInfo()
    with open('tests/missing-title.osu', 'r') as file:
        with pytest.raises(KeyError):
            beatmap_info.extract_beatmap_info(file)
