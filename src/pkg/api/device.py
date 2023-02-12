import os
import shutil
import tempfile
import zipfile
import xxtea
import binascii
from pathlib import Path
from uuid import UUID
from typing import List
from pkg.api.constants import *
from pkg.api.stories import StoryList

class LuniiDevice:
    def __init__(self, mount_point):
        self.mount_point = mount_point

        # dummy values
        self.UUID = ""
        self.device_key = ""
        self.snu = ""
        self.fw_vers_major = 0
        self.fw_vers_minor = 0
        self.memory_left = 0

        # internal device details
        self.__feed_device()

        # internal stories
        self.stories: StoryList[UUID] = feed_stories(self.mount_point)

    # opens the .pi file to read all installed stories
    def __feed_device(self):
        
        mount_path = Path(self.mount_point)
        md_path = mount_path.joinpath(".md")

        story_list = []
        with open(md_path, "rb") as fp_md:
            fp_md.seek(fp_md.tell() + 6)
            self.fw_vers_major = int.from_bytes(fp_md.read(2), 'little')
            self.fw_vers_minor = int.from_bytes(fp_md.read(2), 'little')
            self.snu = int.from_bytes(fp_md.read(8), 'little')
            
            fp_md.seek(0x100)
            self.raw_devkey = fp_md.read(0x100)
            dec = xxtea.decrypt(self.raw_devkey, lunii_generic_key, padding=False, rounds=lunii_tea_rounds(self.raw_devkey))
            self.device_key = dec[:16]

    @property
    def snu_hex(self):
        return self.snu.to_bytes(8, 'little')
    
    def __repr__(self):
        repr_str =  f"Lunii device on \"{self.mount_point}\"\n"
        repr_str += f"- firmware : v{self.fw_vers_major}.{self.fw_vers_minor}\n"
        repr_str += f"- snu      : {binascii.hexlify(self.snu_hex, ' ')}\n"
        repr_str += f"- dev key  : {binascii.hexlify(self.device_key, ' ')}\n"
        repr_str += f"- stories  : {len(self.stories)}x\n"
        return repr_str

    def export_all(self, out_path):
        archives = []
        for count, story in enumerate(self.stories):
            print(f"{count+1:>2}/{len(self.stories)} ", end="")
            one_zip = self.export_story(str(story)[28:], out_path)
            if one_zip:
                archives.append(one_zip)
        return archives

    def update_pack_index(self):
        pi_path = Path(self.mount_point).joinpath(".pi")
        pi_path.unlink()
        with open(pi_path, "wb") as fp:
            st_uuid: UUID
            for st_uuid in self.stories:
                fp.write(st_uuid.bytes)
        return

    def export_story(self, uuid, out_path):
        # is UUID part of existing stories
        if uuid not in self.stories:
            return None

        ulist = self.stories.full_uuid(uuid)
        if len(ulist) > 1:
            print(f"ERROR: at least {len(ulist)} match your pattern. Try a longer UUID.")
            for st in ulist:
                print(f"[{st} - {self.stories.name(str(st))}]")
            return None
        uuid = str(ulist[0])[28:]

        # checking that .content dir exist
        content_path = Path(self.mount_point).joinpath(".content")
        if not content_path.is_dir():
            return None
        story_path = content_path.joinpath(uuid)
        if not story_path.is_dir():
            return None
        
        print(f"[{uuid} - {self.stories.name(uuid)}]")

        # Preparing zip file
        zip_path = Path(out_path).joinpath(f"{uuid} - {self.stories.name(uuid)}.zip")
        with tempfile.TemporaryDirectory() as tmpdirname:
            # creating zip 
            print("> Zipping story ...")
            temp_zip = Path(tmpdirname).joinpath("story")
            shutil.make_archive(temp_zip, 'zip', story_path)
            temp_zip = f"{temp_zip}.zip"

            # adding a dedicated file for story UUID
            print("> Adding story UUID ...")
            temp_uuid = Path(tmpdirname).joinpath("uuid.bin")
            ulist = self.stories.full_uuid(uuid)
            if len(ulist) > 1:
                return None
            full_uuid = ulist[0]

            with open(temp_uuid, "wb") as fp:
                fp.write(full_uuid.bytes)

            zip = zipfile.ZipFile(temp_zip,'a')
            zip.write(temp_uuid, os.path.basename(temp_uuid))
            zip.close()

            # removing bt file
            print("> Removing auth file ...")
            zin = zipfile.ZipFile (temp_zip, 'r')
            zout = zipfile.ZipFile (zip_path, 'w')
            for item in zin.infolist():
                buffer = zin.read(item.filename)
                if item.filename != 'bt':
                    zout.writestr(item, buffer)
            zout.close()
            zin.close()

        return zip_path

    def import_story(self, story_path):
        # opening zip file

        # getting UUID file

        # checking if UUID already loaded

        # uncompressing contents

        # updating .pi file to add new UUID
        
        return

    def remove_story(self, short_uuid):
        if short_uuid not in self.stories:
            print("ERROR: This story is not present on your storyteller")
            return False

        ulist = self.stories.full_uuid(short_uuid)
        if len(ulist) > 1:
            print(f"ERROR: at least {len(ulist)} match your pattern. Try a longer UUID.")
        uuid = str(ulist[0])

        print(f"Removing {uuid[28:]} - {self.stories.name(uuid)}...")
        self.stories.remove(ulist[0])

        # asking for confirmation
        answer = input("Are you sure ? [y/n] ")
        if answer.lower() not in ["y","yes"]:
            return False

        # removing story contents
        st_path = Path(self.mount_point).joinpath(f".content/{uuid[28:]}")
        shutil.rmtree(st_path)

        # updating pack index file
        self.update_pack_index()

        return True


# opens the .pi file to read all installed stories
def feed_stories(root_path) -> StoryList[UUID]:
    
    mount_path = Path(root_path)
    pi_path = mount_path.joinpath(".pi")

    story_list = StoryList()
    with open(pi_path, "rb") as fp_pi:
        loop_again = True
        while loop_again:
            next_uuid = fp_pi.read(16)
            if next_uuid:
                story_list.append(UUID(bytes=next_uuid))
            else:
                loop_again = False
    return story_list


def find_devices(extra_path=None):
    lunii_dev = []

    # checking all drive letters
    for drive in range(ord('A'), ord('Z')+1):
        drv_str = f"{chr(drive)}:/"
        lunii_path = Path(drv_str)
        
        if is_device(lunii_path):
            lunii_dev.append(lunii_path)

    # checking for extra path
    if extra_path:
        lunii_path = Path(extra_path)
        
        if is_device(lunii_path):
            lunii_dev.append(lunii_path)

    # done
    return lunii_dev


def is_device(root_path):
    pi_path = root_path.joinpath(".pi")
    md_path = root_path.joinpath(".md")
    cfg_path = root_path.joinpath(".cfg")
    content_path = root_path.joinpath(".content")

    if pi_path.is_file() and md_path.is_file() and cfg_path.is_file() and content_path.is_dir():
        return True
    return False