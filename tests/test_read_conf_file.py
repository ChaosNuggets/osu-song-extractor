import sys
import os
sys.path.append(os.path.expanduser(r'~/Projects/Osu-Song-Extractor'))
from main import read_conf_file
import pytest

def test_normal_cfg():
    conf_values = read_conf_file('tests/normal-test.cfg')
    assert conf_values.input_dir == '~/Music/Songs'
    assert conf_values.output_dir == '~/Music/Extracted-Songs'

def test_many_spaces_cfg():
    conf_values = read_conf_file('tests/many-spaces-test.cfg')
    assert conf_values.input_dir == '~/Music/Songs'
    assert conf_values.output_dir == r'~\Music\Extracted-Songs'
