import click
from pkg.api.device import LuniiDevice, find_devices
from pkg.api.stories import story_name


CLI_VERSION = "0.9.0"

@click.command()
@click.version_option(CLI_VERSION, prog_name="Lunii Storyteller CLI application")
@click.option('--find', '-f', "find", is_flag=True, help="Identifying all Lunii storytellers connected")
@click.option('--dev', '-d', "dev", type=click.Path(exists=True, file_okay=False, dir_okay=True), default=None, help="Specifies which drives letter to use for Lunii Storyteller")
@click.option('--info', '-i', "info", is_flag=True, help="Prints informations about the storyteller")
@click.option('--list', '-l', "list", is_flag=True, help="List all stories available in Lunii Storyteller")
@click.option('--pack-export', '-pe', "exp", type=str, default=None, help="Export selected story to an archive")
@click.option('--pack-import', '-pi', "imp", type=str, default=None, help="Import a story archive in the Lunii")
@click.option('--pack-remove', '-pr', "rem", type=str, default=None, help="Remove a story from the Lunii")
def cli_main(find, info, dev, list, exp, imp, rem):
    dev_list = find_devices()

    # finding connected devices
    if find:
        print(f"Found {len(dev_list)} connected device(s)")

        for dev in dev_list:
            one_dev = LuniiDevice(dev)
            print(f"  \"{one_dev.mount_point}\" - {len(one_dev.stories)} stories")
        return

    # selecting default lunii dev
    if dev_list and not dev:
        click.echo(f"INFO : using Lunii device on {dev_list[0]}")
        dev = dev_list[0]

    if not dev:
        click.echo("ERROR : no Lunii device connected !")
        return

    # using selected device
    my_dev = LuniiDevice(dev)


    if info:
        print(my_dev)
        return
    elif list:
        print(my_dev)
        for story in my_dev.stories:
            print(f"> {str(story).upper()[28:]} - {story_name(story)}")
    elif exp:
        return
    elif imp:
        return
    elif rem:
        return

    return


if __name__ == '__main__':
    cli_main()