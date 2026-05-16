from write_output import extract_beatmap_infos
from pathlib import Path

def test_extract_beatmap_infos():
    p_in_sub = Path('tests/173612 xi - FREEDOM DiVE')
    beatmap_infos = extract_beatmap_infos(p_in_sub)
    assert len(beatmap_infos) == 9
    for beatmap_info in beatmap_infos:
        assert beatmap_info.audio_filename == 'Freedom Dive.mp3'
        assert beatmap_info.title == 'FREEDOM DiVE'
        assert beatmap_info.artist == 'xi'
        assert beatmap_info.bg_filename == 'background desuuu.jpg'
        assert beatmap_info.beatmap_set_id == 173612

    # check that all versions are present
    assert any(beatmap_info.version == r'4K Another' for beatmap_info in beatmap_infos)
    assert any(beatmap_info.version == r'4K Hyper' for beatmap_info in beatmap_infos)
    assert any(beatmap_info.version == r'4K Normal' for beatmap_info in beatmap_infos)
    assert any(beatmap_info.version == r"Blocko's 7K Another" for beatmap_info in beatmap_infos)
    assert any(beatmap_info.version == r"Blocko's 7K Black Another" for beatmap_info in beatmap_infos)
    assert any(beatmap_info.version == r"Blocko's 7K Normal" for beatmap_info in beatmap_infos)
    assert any(beatmap_info.version == r"Dain's 7K Light" for beatmap_info in beatmap_infos)
    assert any(beatmap_info.version == r"Fullerene's 4K DIMENSIONS" for beatmap_info in beatmap_infos)
    assert any(beatmap_info.version == r"Tear's 7K Hyper" for beatmap_info in beatmap_infos)

    # check that all beatmap_ids are present
    assert any(beatmap_info.beatmap_id == 419485 for beatmap_info in beatmap_infos)
    assert any(beatmap_info.beatmap_id == 420005 for beatmap_info in beatmap_infos)
    assert any(beatmap_info.beatmap_id == 423649 for beatmap_info in beatmap_infos)
    assert any(beatmap_info.beatmap_id == 421369 for beatmap_info in beatmap_infos)
    assert any(beatmap_info.beatmap_id == 480207 for beatmap_info in beatmap_infos)
    assert any(beatmap_info.beatmap_id == 420781 for beatmap_info in beatmap_infos)
    assert any(beatmap_info.beatmap_id == 502132 for beatmap_info in beatmap_infos)
    assert any(beatmap_info.beatmap_id == 473228 for beatmap_info in beatmap_infos)
    assert any(beatmap_info.beatmap_id == 420779 for beatmap_info in beatmap_infos)
