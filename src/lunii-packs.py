import click
from pkg.api.device import LuniiDevice, find_devices, is_device
from pkg.api.stories import story_name


CLI_VERSION = "1.0.0"


@click.command()
@click.version_option(CLI_VERSION, prog_name="Lunii Storyteller CLI application")
@click.option('--find', '-f', "find", is_flag=True, help="Identifying all Lunii storytellers connected")
@click.option('--dev', '-d', "dev", type=click.Path(exists=True, file_okay=False, dir_okay=True), default=None, help="Specifies which drives letter to use for Lunii Storyteller")
@click.option('--info', '-i', "info", is_flag=True, help="Prints informations about the storyteller")
@click.option('--list', '-l', "slist", is_flag=True, help="List all stories available in Lunii Storyteller")
@click.option('--pack-export', '-pe', "exp", type=str, default=None, help="Export selected story to an archive (or use ALL)")
@click.option('--pack-import', '-pi', "imp", type=click.Path(exists=True, file_okay=True, dir_okay=False), default=None, help="Import a story archive in the Lunii")
@click.option('--pack-remove', '-pr', "rem", type=str, default=None, help="Remove a story from the Lunii")
def cli_main(find, info, dev, slist, exp, imp, rem):
    valid_dev_list = find_devices()

    # finding connected devices
    if find:
        print(f"Found {len(valid_dev_list)} connected device(s)")

        for dev in valid_dev_list:
            one_dev = LuniiDevice(dev)
            print(f"  \"{one_dev.mount_point}\" - {len(one_dev.stories)} stories")
        return

    # selecting default lunii dev
    if valid_dev_list and not dev:
        click.echo(f"INFO : using Lunii device on {valid_dev_list[0]}")
        dev = valid_dev_list[0]

    if not dev or not is_device(dev):
        click.echo("ERROR : no Lunii device connected !")
        return

    # using selected device
    my_dev = LuniiDevice(dev)

    if info:
        print(my_dev)
        return
    elif slist:
        print(my_dev)
        for story in my_dev.stories:
            print(f"> {str(story).upper()[28:]} - {story_name(story)}")
    elif exp:
        zip_list = []
        if exp.upper() == "ALL":
            zip_list = my_dev.export_all("./")
        else:
            one_zip = my_dev.export_story(exp, "./")
            if one_zip:
                zip_list.append(one_zip)

        if zip_list:
            click.echo(f"Successfully exported to :")
            for one_zip in zip_list:
                click.echo(f"  {one_zip}")
        else:
            click.echo("ERROR: Failed to export")
        return
    elif imp:
        res = my_dev.import_story(imp)
        if not res:
            click.echo("ERROR: Failed to import")
        else:
            click.echo("Story imported.")
    elif rem:
        res = my_dev.remove_story(rem)
        if not res:
            click.echo("ERROR: Failed to remove")
        else:
            click.echo("Story removed.")

    return


if __name__ == '__main__':
    cli_main()
