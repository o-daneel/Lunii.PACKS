import os
import click
import logging

from lunii_logging import initialize_logger
from pkg.api.constants import LUNII_V3, V3_KEYS, LUNII_LOGGER
from pkg.api.device_lunii import LuniiDevice, is_lunii
from pkg.api.device_flam import FlamDevice, is_flam
from pkg.api.devices import find_devices
from pkg.api.stories import story_load_db


CLI_VERSION = "2.1.1"


def exit_help():
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    ctx.exit()

@click.command()
@click.version_option(CLI_VERSION, prog_name="Lunii Storyteller - Pack Manager (CLI)")
@click.option('--verbose', '-v', "verbose", is_flag=True, help="Verbose mode")
@click.option('--find', '-f', "find", is_flag=True, help="Identifying all Lunii storytellers connected")
@click.option('--dev', '-d', "dev", type=click.Path(exists=True, file_okay=False, dir_okay=True), default=None, help="Specifies which drives letter to use for Lunii Storyteller")
@click.option('--refresh', '-r', "refresh", is_flag=True, help="Refresh official db from Lunii")
@click.option('--info', '-i', "info", is_flag=True, help="Prints informations about the storyteller")
@click.option('--list', '-l', "slist", is_flag=True, help="List all stories available in Lunii Storyteller")
@click.option('--key',  '-k', "key_v3", type=click.Path(exists=False, file_okay=True, dir_okay=False), default=V3_KEYS, help="Device Key file for Lunii v3")
@click.option('--pack-export', '-pe', "exp", type=str, default=None, help="Export selected story to an archive (or use ALL)")
@click.option('--pack-import', '-pi', "imp", type=click.Path(exists=True, file_okay=True, dir_okay=True), default=None, help="Import a story archive in the Lunii")
@click.option('--pack-remove', '-pr', "rem", type=str, default=None, help="Remove a story from the Lunii")
def cli_main(verbose, find, dev, refresh, info, slist, key_v3, exp, imp, rem):
    
    # Initialize logger
    initialize_logger(logging.INFO)

    # Get main logger
    main_logger = logging.getLogger(LUNII_LOGGER)

    valid_dev_list = find_devices()

    # at least one command is required
    if not any([find, info, slist, exp, imp, rem]):
        exit_help()

    # finding connected devices
    if find:
        main_logger.log(logging.INFO, f"Found {len(valid_dev_list)} connected device(s)")

        for dev in valid_dev_list:
            if is_lunii(dev):
                one_dev = LuniiDevice(dev, key_v3)
            elif is_flam(dev):
                one_dev = FlamDevice(dev)
            else:
                main_logger.log(logging.ERROR, f"This device is not supported: '{dev}'")
                return
            
            main_logger.log(logging.INFO, f"\"{one_dev.mount_point}\" - {len(one_dev.stories)} stories")
        return

    # selecting default lunii dev
    if valid_dev_list and not dev:
        click.echo(f"INFO : using Lunii device on {valid_dev_list[0]}")
        dev = valid_dev_list[0]

    if not dev or (not is_lunii(dev) and not is_flam(dev)):
        click.echo("ERROR : no supported device connected !")
        return
    
    device_type = "LUNII"

    # using selected device
    if is_lunii(dev):
        my_dev = LuniiDevice(dev, key_v3)
    elif is_flam(dev):
        my_dev = FlamDevice(dev)
        device_type = "FLAM"
    else: 
        main_logger.log(logging.ERROR, f"This device is not supported: '{dev}'")
        return

    # feeding official db (from cache or live)
    story_load_db(refresh)

    if info:
        print(my_dev)
        return
    elif slist:
        print(my_dev)
        if verbose:
            print("{:36} | {:<60} | {:6}".format("UUID", "Name", "Source"))
            print("{} | {:<60} | {:6}".format("-"*36, "-"*60, "-"*6 ))
            for story in my_dev.stories:
                print("{} | {:<60} | {:6}".format(story.str_uuid, story.name, " "))
        else:
            for story in my_dev.stories:
                print(f"> {story.short_uuid} - {story.name}")
    elif exp:
        zip_list = []
        if exp.upper() == "ALL":
            if device_type == "LUNII":
                # full export
                zip_list = my_dev.export_all("./")
            else:
                main_logger.log(logging.ERROR, f"The '{device_type}' device does not support the 'export all' feature")
                return
        else:
            # single to export
            one_zip = my_dev.export_story(exp, "./")
            if one_zip:
                zip_list.append(one_zip)

        if zip_list:
            click.echo(f"Successfully exported to :")
            for one_zip in zip_list:
                click.echo(f"  {one_zip}")
        else:
            click.echo("   ERROR: Failed to export")
        return
    elif imp:
        # checking for v3 without key
        if is_lunii(dev) and my_dev.device_version == LUNII_V3 and not my_dev.story_key:
            main_logger.log(logging.ERROR, "🛑 Lunii v3 device (fw 3.2.2+) without story keys")
            return

        if os.path.isfile(imp):
            # single story to import
            res = my_dev.import_story(imp)
        elif device_type == "LUNII":
            # directory to import
            res = my_dev.import_dir(imp)
        else:
            main_logger.log(logging.ERROR, f"The '{device_type}' device does not support the 'import directory' feature")
            return
        
        if not res:
            click.echo("ERROR: Failed to import")
        else:
            click.echo("Stories imported.")

    
    elif rem:
        res = my_dev.remove_story(rem)
        if not res:
            click.echo("ERROR: Failed to remove")
        else:
            click.echo("Story removed.")

    return


if __name__ == '__main__':
    cli_main()
