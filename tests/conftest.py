import pytest

# from mcm.adapters import MasterAdapter, SlaveAdapter
# from mock import MagicMock, patch

@pytest.fixture(scope='function')
def masteradapter():
    return MasterAdapter(device=MagicMock())


@pytest.fixture(scope='function')
def path():
    return MagicMock()
