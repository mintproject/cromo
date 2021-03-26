from pathlib import Path

import cromo
import semver
import click
from cromo import _utils
from cromo._utils import get_cromo_logger

logging = get_cromo_logger()


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
You should consider upgrading via 'pip install --upgrade cromo' command.""",
            fg="yellow",
        )


@cli.command(short_help="Find appropriate models for a particular region")
@click.argument(
    "region_bounding_box",
    default=Path('10.2,45.4,10.23,49.4'),
    required=True
)
def start(region_bounding_box):
    print(region_bounding_box)
    