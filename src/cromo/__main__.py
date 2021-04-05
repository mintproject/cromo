import collections
import sys
from pathlib import Path

import cromo
import semver
import click

from cromo import _utils
from cromo.click_encapsulate.commands import start
from modelcatalog import Configuration

from cromo.constants import ONTOLOGY_DIR, RULES_DIR


@click.group()
@click.option("--verbose", "-v", default=0, count=True)
def cli(verbose):
    _utils.init_logger()
    try:
        lv = ".".join(_utils.get_latest_version().split(".")[:3])
    except Exception as e:
        click.secho(
            f"""WARNING: Unable to check if cromo is updated""",
            fg="yellow",
        )
        return

    cv = ".".join(cromo.__version__.split(".")[:3])

    if semver.compare(lv, cv) > 0:
        click.secho(
            f"""WARNING: You are using cromo version {cromo.__version__}, however version {lv} is available.
You should consider upgrading via the 'pip install --upgrade cromo' command.""",
            fg="yellow",
        )


@cli.command(short_help="Show cromo version")
def version(debug=False):
    click.echo(f"{Path(sys.argv[0]).name} v{cromo.__version__}")


class OrderedGroup(click.Group):
    def __init__(self, name=None, commands=None, **attrs):
        super(OrderedGroup, self).__init__(name, commands, **attrs)
        #: the registered subcommands by their exported names.
        self.commands = commands or collections.OrderedDict()

    def list_commands(self, ctx):
        return self.commands

@cli.group(cls=OrderedGroup)
def search():
    """Command to search models for a region"""
search.add_command(start)
