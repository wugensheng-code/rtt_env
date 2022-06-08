from env import __version__
from env.main import app
from typer.testing import CliRunner

runner = CliRunner()


def test_version():
    assert __version__ == '0.1.1'
