import click
from pkg.api.device import LuniiDevice


CLI_VERSION = "0.9.0"

@click.command()
@click.version_option(CLI_VERSION, prog_name="Lunii Storyteller CLI application")
@click.option('--find', '-f', "find", is_flag=True, help="Identifying all Lunii storytellers connected")
@click.option('--dev', '-d', "dev", type=str, default=None, help="Specifies which drives letter to use for Lunii Storyteller")
@click.option('--info', '-i', "info", is_flag=True, help="Prints informations about the storyteller")
@click.option('--list', '-l', "list", is_flag=True, help="List all stories available in Lunii Storyteller")
@click.option('--pack-export', '-pe', "exp", type=str, default=None, help="Export selected story to an archive")
@click.option('--pack-import', '-pi', "imp", type=str, default=None, help="Import a story archive in the Lunii")
def cli_main(find, info, dev, list, exp, imp):

    my_dev = LuniiDevice(dev)
    if info:
        print(my_dev)
        return
    
    return


if __name__ == '__main__':
    cli_main()
