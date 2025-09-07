import os.path
import shutil
import zipfile
import binascii
import logging
from tqdm import tqdm
from uuid import UUID

import psutil
import py7zr

from pkg.api import stories
from pkg.api.constants import *
from pkg.api.device_lunii import secure_filename
from pkg.api.stories import StoryList, Story, story_is_studio, story_is_lunii

LIB_BASEDIR = "etc/library/"


class FlamDevice:
    STORIES_BASEDIR = "str/"

    stories: StoryList

    def __init__(self, mount_point):
        super().__init__()
        self.mount_point = mount_point

        # dummy values
        self.lunii_version = 0
        self.UUID = ""
        self.snu = b""
        self.fw_main = "?.?.?"
        self.fw_comm = "?.?.?"
        self.memory_left = 0

        self.abort_process = False

        # Get logger
        self.logger = logging.getLogger(LUNII_LOGGER)

        # internal device details
        if not self.__feed_device():
            return

        # loading internal stories + pi update for duplicates filtering
        self.stories = feed_stories(self.mount_point)
        self.update_pack_index()

    @property
    def snu_str(self):
        return self.snu.hex().upper().lstrip("0")

    @property
    def snu_hex(self):
        return self.snu

    def __repr__(self):
        repr_str = f"Flam device on \"{self.mount_point}\"\n"
        repr_str += f"- Main firmware : v{self.fw_main}\n"
        repr_str += f"- Comm firmware : v{self.fw_comm}\n"
        repr_str += f"- SNU      : {binascii.hexlify(self.snu_hex, ' ')}\n"
        repr_str += f"- stories  : {len(self.stories)}x"
        return repr_str

    # opens the .mdf file to read all information related to device
    def __feed_device(self):

        mount_path = Path(self.mount_point)
        mdf_path = mount_path.joinpath(".mdf")

        # checking if specified path is acceptable
        if not os.path.isfile(mdf_path):
            return False

        with open(mdf_path, "rb") as fp_mdf:
            mdf_version = int.from_bytes(fp_mdf.read(2), 'little')

            if mdf_version == 1:
                self.__md1_parse(fp_mdf)

        return True

    def __md1_parse(self, fp_mdf):
        fp_mdf.seek(2)

        # parsing firmware versions
        raw = fp_mdf.read(48)
        raw_str = raw.decode('utf-8').strip('\x00')
        raw_str = raw_str.replace("main: ", "").replace("comm: ", "")
        versions = raw_str.splitlines()

        self.fw_main = versions[0].split("-")[0]
        if len(versions) > 1:
            self.fw_comm = versions[1].split("-")[0]

        # parsing snu
        snu_str = fp_mdf.read(24).decode('utf-8').rstrip('\x00')
        self.snu = binascii.unhexlify(snu_str)

        # parsing VID/PID
        vid = int.from_bytes(fp_mdf.read(2), 'little')
        pid = int.from_bytes(fp_mdf.read(2), 'little')

        if (vid, pid) == FLAM_USB_VID_PID:
            self.device_version = FLAM_V1
        else:
            self.device_version = UNDEF_DEV

        self.logger.log(logging.DEBUG, f"\n"
                                       f"SNU : {self.snu_str}\n"
                                       f"HW  : v{self.device_version-(FLAM_V1-1)}\n"
                                       f"FW (main) : {self.fw_main}\n"
                                       f"FW (comm) : {self.fw_comm}\n"
                                       f"VID/PID : 0x{vid:04X} / 0x{pid:04X}")

    def update_pack_index(self):
        lib_path = Path(self.mount_point).joinpath(LIB_BASEDIR)
        list_path = lib_path.joinpath("list")
        list_hidden_path = lib_path.joinpath("list.hidden")
        list_path.unlink(missing_ok=True)
        list_hidden_path.unlink(missing_ok=True)
        lib_path.mkdir(parents=True, exist_ok=True)
        with open(list_path, "w", newline='\n') as fp, open(list_hidden_path, "w", newline='\n') as fp_hidden:
            for story in self.stories:
                if story.hidden:
                    fp_hidden.write(str(story.uuid) + "\n")
                else:
                    fp.write(str(story.uuid) + "\n")
        return

    def __valid_story(self, story_dir):
        return True

    def recover_stories(self, dry_run: bool):
        recovered = 0

        # getting all stories
        content_dir = os.path.join(self.mount_point, self.STORIES_BASEDIR)
        stories_dir = [entry for entry in os.listdir(content_dir) if os.path.isdir(os.path.join(content_dir, entry))]

        pbar = tqdm(iterable=stories_dir, total=len(stories_dir), bar_format=TQDM_BAR_FORMAT)
        for story in pbar:
            # directory is a partial UUID
            pbar.set_description(f"Processing {story}")

            str_uuid = None
            # looking complete UUID in official DB
            if not str_uuid:
                str_uuid = next((uuid for uuid in stories.DB_OFFICIAL if story.upper() in uuid.upper()), None)
            # looking complete UUID in third party DB
            if not str_uuid:
                str_uuid = next((uuid for uuid in stories.DB_THIRD_PARTY if story.upper() in uuid.upper()), None)
            if not str_uuid:
                str_uuid = story

            # prepare for story analysis
            try:
                full_uuid = UUID(str_uuid)
            except (TypeError, ValueError) as e:
                self.logger.log(logging.DEBUG, f"Not a valid UUID - {str_uuid}")
                continue

            one_story = Story(full_uuid)
            story_dir = os.path.join(content_dir, story)

            if str_uuid not in self.stories:
                # Lost Story
                if self.__valid_story(story_dir):

                    # is it a dry run ?
                    if not dry_run:
                        self.logger.log(logging.INFO, f"Recovered - {str(full_uuid).upper()} - {one_story.name}")
                        self.stories.append(Story(full_uuid))
                    else:
                        self.logger.log(logging.INFO, f"Found - {str(full_uuid).upper()} - {one_story.name}")
                    recovered += 1
                else:
                    self.logger.log(logging.INFO, f"Skipping lost story (seems broken/incomplete) - {str(full_uuid).upper()} - {one_story.name}")
            else:
                # In DB story
                if not self.__valid_story(story_dir):
                    self.logger.log(logging.WARNING, f"Already in list but invalid - {str(full_uuid).upper()} - {one_story.name}")
                else:
                    self.logger.log(logging.DEBUG, f"Already in list - {str(full_uuid).upper()} - {one_story.name}")

        return recovered

    def cleanup_stories(self):
        removed = 0
        recovered_size = 0

        # getting all stories
        content_dir = os.path.join(self.mount_point, self.STORIES_BASEDIR)
        stories_dir = [entry for entry in os.listdir(content_dir) if os.path.isdir(os.path.join(content_dir, entry))]

        # Manage the progress bar
        pbar = tqdm(iterable=stories_dir, total=len(stories_dir), bar_format=TQDM_BAR_FORMAT)
        for story in pbar:
            # directory is a partial UUID
            pbar.set_description(f"Processing {story}")

            if story not in self.stories:
                # remove it
                try:
                    lost_story_path = os.path.join(content_dir, story)

                    # computing lost size
                    for parent_dir, _, files in os.walk(lost_story_path):
                        for file in files:
                            recovered_size += os.path.getsize(os.path.join(parent_dir, file))

                    # removing whole directory
                    self.logger.log(logging.INFO, f"Deleting - {lost_story_path}")
                    shutil.rmtree(lost_story_path)
                    removed += 1
                except (OSError, PermissionError) as e:
                    self.logger.log(logging.WARN, f"Failed to delete - {lost_story_path}")
                    self.logger.log(logging.ERROR, e)

        return removed, recovered_size//1024//1024

    def import_story(self, story_path):
        archive_type = TYPE_UNK

        self.logger.log(logging.INFO, f"🚧 Loading {story_path}...")

        archive_size = os.path.getsize(story_path)
        free_space = psutil.disk_usage(str(self.mount_point)).free
        if archive_size >= free_space:
            self.logger.log(logging.ERROR, f"Not enough space left on Flam (only {free_space//1024//1024}MB)")
            return False

        # identifying based on filename
        if story_path.lower().endswith(EXT_ZIP):
            archive_type = TYPE_FLAM_ZIP
        elif story_path.lower().endswith(EXT_7z):
            archive_type = TYPE_FLAM_7Z

        # processing story
        if archive_type in [TYPE_FLAM_ZIP, TYPE_FLAM_7Z]:
            self.logger.log(logging.WARN, "😮‍💨 This process is veeeeeeeeery long due to Flam firmware. 😴 Be patient ...")

        if archive_type == TYPE_FLAM_ZIP:
            self.logger.log(logging.DEBUG, "Archive => TYPE_FLAM_ZIP")
            return self.import_flam_zip(story_path)
        elif archive_type == TYPE_FLAM_7Z:
            self.logger.log(logging.DEBUG, "Archive => TYPE_FLAM_7Z")
            return self.import_flam_7z(story_path)

    def import_flam_zip(self, story_path):
        # checking if archive is OK
        try:
            with zipfile.ZipFile(file=story_path):
                pass  # If opening succeeds, the archive is valid
        except zipfile.BadZipFile as e:
            self.logger.log(logging.ERROR, e)
            return False

        # opening zip file
        with zipfile.ZipFile(file=story_path) as zip_file:
            # reading all available files
            zip_contents = zip_file.namelist()

            if story_is_lunii(zip_contents) or story_is_studio(zip_contents):
                self.logger.log(logging.ERROR, f"Archive seems to be made of Lunii story (not compatible with Flam)")
                return False

            # getting UUID from path
            uuid_path = Path(zip_contents[0])
            uuid_str = uuid_path.parents[0].name if uuid_path.parents[0].name else uuid_path.name

            if len(uuid_str) >= 16:  # long enough to be a UUID
                # self.signal_logger.emit(logging.DEBUG, uuid_str)
                try:
                    if "-" not in uuid_str:
                        new_uuid = UUID(bytes=binascii.unhexlify(uuid_str))
                    else:
                        new_uuid = UUID(uuid_str)
                except ValueError as e:
                    self.logger.log(logging.ERROR, f"UUID parse error {e}")
                    return False
            else:
                self.logger.log(logging.ERROR, "UUID directory is missing in archive !")
                return False

            # checking if UUID already loaded
            if str(new_uuid) in self.stories:
                self.logger.log(logging.WARNING, f"'{self.stories.get_story(new_uuid).name}' is already loaded, aborting !")
                return False

            # decompressing story contents
            short_uuid = str(new_uuid).upper()[28:]
            output_path = Path(self.mount_point).joinpath(f"{self.STORIES_BASEDIR}")
            if not output_path.exists():
                output_path.mkdir(parents=True)

            # Loop over each file
            # Manage the progress bar
            pbar = tqdm(iterable=zip_contents, total=len(zip_contents), bar_format=TQDM_BAR_FORMAT)
            for file in pbar:
                if self.abort_process:
                    self.logger.log(logging.WARNING, f"Import aborted, performing cleanup on current story...")
                    self.__clean_up_story_dir(new_uuid)
                    return False

                if file.endswith("/"):
                    continue

                pbar.set_description(f"Processing {file}")

                # Extract each zip file
                data = zip_file.read(file)

                target: Path = output_path.joinpath(file)

                # create target directory
                if not target.parent.exists():
                    target.parent.mkdir(parents=True)
                # write target file
                with open(target, "wb") as f_dst:
                    f_dst.write(data)

        # updating .pi file to add new UUID
        self.stories.append(Story(new_uuid))
        self.update_pack_index()

        return True
    
    def import_flam_7z(self, story_path):
        # checking if archive is OK
        try:
            with py7zr.SevenZipFile(story_path, mode='r'):
                pass  # If opening succeeds, the archive is valid
        except py7zr.exceptions.Bad7zFile as e:
            self.logger.log(logging.ERROR, e)
            return False

        # opening zip file
        with py7zr.SevenZipFile(story_path, mode='r') as zip:
            # reading all available files
            zip_contents = zip.getnames()
            if story_is_lunii(zip_contents) or story_is_studio(zip_contents):
                self.logger.log(logging.ERROR, f"Archive seems to be made of Lunii story (not compatible with Flam)")
                return False

            # reading all available files
            zip_contents = zip.list()
            # getting UUID from path
            uuid_path = Path(zip_contents[0].filename)
            uuid_str = uuid_path.parents[0].name if uuid_path.parents[0].name else uuid_path.name
            if len(uuid_str) >= 16:  # long enough to be a UUID
                # self.signal_logger.emit(logging.DEBUG, uuid_str)
                try:
                    if "-" not in uuid_str:
                        new_uuid = UUID(bytes=binascii.unhexlify(uuid_str))
                    else:
                        new_uuid = UUID(uuid_str)
                except ValueError as e:
                    self.logger.log(logging.ERROR, f"UUID parse error {e}")
                    return False
            else:
                self.logger.log(logging.ERROR, "UUID directory is missing in archive !")
                return False

            # checking if UUID already loaded
            if str(new_uuid) in self.stories:
                self.logger.log(logging.WARNING, f"'{self.stories.get_story(new_uuid).name}' is already loaded, aborting !")
                return False

            # decompressing story contents
            short_uuid = str(new_uuid).upper()[28:]
            output_path = Path(self.mount_point).joinpath(f"{self.STORIES_BASEDIR}")
            if not output_path.exists():
                output_path.mkdir(parents=True)

            # Loop over each file
            self.logger.log(logging.INFO, "Reading 7zip archive... (takes time)")
            contents = zip.readall().items()
            pbar = tqdm(iterable=enumerate(contents), total=len(contents), bar_format=TQDM_BAR_FORMAT)
            for index, (fname, bio) in pbar:
                # abort requested ? early exit
                if self.abort_process:
                    self.logger.log(logging.WARNING, f"Import aborted, performing cleanup on current story...")
                    self.__clean_up_story_dir(new_uuid)
                    return False

                pbar.set_description(f"Processing {fname}")

                if zip_contents[index].is_directory:
                    continue

                # Extract each zip file
                target: Path = output_path.joinpath(fname)

                # create target directory
                if not target.parent.exists():
                    target.parent.mkdir(parents=True)
                # write target file
                with open(target, "wb") as f_dst:
                    f_dst.write(bio.read())

        # updating .pi file to add new UUID
        self.stories.append(Story(new_uuid))
        self.update_pack_index()

        return True

    def export_story(self, uuid, out_path):
        # is UUID part of existing stories
        if uuid not in self.stories:
            return None

        slist = self.stories.matching_stories(uuid)
        if len(slist) > 1:
            self.logger.log(logging.ERROR, f"at least {len(slist)} match your pattern. Try a longer UUID.")
            for st in slist:
                self.logger.log(logging.ERROR, f"[{st.str_uuid} - {st.name}]")
            return None

        one_story = slist[0]

        # checking that .content dir exist
        content_path = Path(self.mount_point).joinpath(self.STORIES_BASEDIR)
        if not content_path.is_dir():
            return None
        story_path = content_path.joinpath(str(one_story.uuid))
        if not story_path.is_dir():
            return None

        self.logger.log(logging.INFO, f"🚧 Exporting {one_story.short_uuid} - {one_story.name}")

        # Preparing zip file
        sname = one_story.name
        sname = secure_filename(sname)

        zip_path = Path(out_path).joinpath(f"{sname}.{one_story.short_uuid}.zip")
        # if os.path.isfile(zip_path):
        #     self.signal_logger.emit(logging.WARNING, f"Already exported")
        #     return None

        # preparing file list
        story_flist = []
        story_arcnames = []
        for root, _, filenames in os.walk(story_path):
            for filename in filenames:
                abs_file = os.path.join(root, filename)
                story_flist.append(abs_file)

                index = abs_file.find(str(one_story.uuid))
                story_arcnames.append(abs_file[index:])

        try:
            with zipfile.ZipFile(zip_path, 'w') as zip_out:
                self.logger.log(logging.DEBUG, "> Zipping story ...")
                pbar = tqdm(iterable=enumerate(story_flist), total=len(story_flist), bar_format=TQDM_BAR_FORMAT)
                for index, file in pbar:
                    # abort requested ? early exit
                    if self.abort_process:
                        return None

                    pbar.set_description(f"Processing {file}")
                    zip_out.write(file, story_arcnames[index])

        except PermissionError as e:
            self.logger.log(logging.ERROR, f"failed to create ZIP - {e}")
            return None

        return zip_path

    def __clean_up_story_dir(self, story_uuid: UUID):
        story_dir = Path(self.mount_point).joinpath(f"{self.STORIES_BASEDIR}{str(story_uuid)}")
        if os.path.isdir(story_dir):
            try:
                shutil.rmtree(story_dir)
            except OSError as e:
                self.logger.emit(logging.ERROR, e)
                return False
            except PermissionError as e:
                self.logger.emit(logging.ERROR, e)
                return False
        return True

    def remove_story(self, short_uuid):
        if short_uuid not in self.stories:
            self.logger.log(logging.ERROR, "This story is not present on your storyteller")
            return False

        slist = self.stories.matching_stories(short_uuid)
        if len(slist) > 1:
            self.logger.log(logging.ERROR, f"at least {len(slist)} match your pattern. Try a longer UUID.")
            return False
        uuid = slist[0].str_uuid

        self.logger.log(logging.INFO, f"🚧 Removing {uuid[28:]} - {self.stories.get_story(uuid).name}...")

        # asking for confirmation
        answer = input("Are you sure ? [y/N] ")
        if answer.lower() not in ["y", "yes"]:
            return False

        # removing story contents
        if not self.__clean_up_story_dir(slist[0].uuid):
            return False

        # removing story from class
        self.stories.remove(slist[0])
        # updating pack index file
        self.update_pack_index()

        return True

    #TODO
    def factory_reset(self):
        print("factory_reset")
        pass


# opens the .pi file to read all installed stories
def feed_stories(root_path) -> StoryList[UUID]:
    logger = logging.getLogger(LUNII_LOGGER)

    mount_path = Path(root_path)
    list_path = mount_path.joinpath(LIB_BASEDIR + "list")
    list_hidden_path = mount_path.joinpath(LIB_BASEDIR + "list.hidden")

    story_list = StoryList()

    logger.log(logging.INFO, f"Reading Flam loaded stories...")

    # if there is a list
    if os.path.isfile(list_path):
        with open(list_path, "r") as fp_list:
            lines = fp_list.read().splitlines()
            for uuid_str in lines:
                one_uuid = UUID(uuid_str.strip())
                logger.log(logging.DEBUG, f"> {str(one_uuid)}")
                if one_uuid in story_list:
                    logger.log(logging.WARNING, f"Found duplicate story, cleaning...")
                else:
                    story_list.append(Story(one_uuid))

    story_count = len(story_list)
    logger.log(logging.INFO, f"Read {len(story_list)} stories")

    # if there is a hidden list
    if os.path.isfile(list_hidden_path):
        with open(list_hidden_path, "r") as fp_list:
            lines = fp_list.read().splitlines()
            for uuid_str in lines:
                one_uuid = UUID(uuid_str.strip())
                logger.log(logging.DEBUG, f"> {str(one_uuid)}")
                if one_uuid in story_list:
                    logger.log(logging.WARNING, f"Found duplicate story, cleaning...")
                else:
                    story_list.append(Story(one_uuid, True))

    logger.log(logging.INFO, f"Read {len(story_list) - story_count} hidden stories")
    return story_list


def is_flam(root_path):
    MDF_FILE = os.path.join(root_path, ".mdf")

    try:
        if os.path.isfile(MDF_FILE):
            return True
    except PermissionError:
        pass
    return False


