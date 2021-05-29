"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Hopscotch."""


if __name__ == "__main__":
    main(prog_name="hopscotch")  # pragma: no cover
