import pytest

from job_skill_gap.sources import ADAPTERS


@pytest.mark.parametrize("name", ADAPTERS)
def test_adapter_is_instantiable(name):
    assert ADAPTERS[name]().name == name
