import pytest

from mixer import Mixer


@pytest.fixture()
def mixer_commit():
    return False


@pytest.fixture()
def mixer(mixer_commit):
    return Mixer(commit=mixer_commit)
