import xxtea
import binascii
from pathlib import Path
from uuid import UUID
from typing import List
from pkg.api.constants import *

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
        self.stories = feed_stories(self.mount_point)


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
        repr_str =  f"Lunii device on {self.mount_point} :\n"
        repr_str += f"- firmware : v{self.fw_vers_major}.{self.fw_vers_minor}\n"
        repr_str += f"- snu      : {binascii.hexlify(self.snu_hex, ' ')}\n"
        repr_str += f"- dev key  : {binascii.hexlify(self.device_key, ' ')}\n"
        repr_str += f"- stories  : {len(self.stories)}x\n"
        return repr_str

    def export_story(self, uuid, out_path):
        # is UUID part of existing stories

        # checking that .content dir exist

        # adding a dedicated file for story UUID

        # creating zip 

        return

    def import_story(self, story_path):
        # opening zip file

        # getting UUID file

        # checking if UUID already loaded

        # uncompressing contents

        # updating .pi file to add new UUID
        
        return

# opens the .pi file to read all installed stories
def feed_stories(root_path) -> List[UUID]:
    
    mount_path = Path(root_path)
    pi_path = mount_path.joinpath(".pi")

    story_list = []
    with open(pi_path, "rb") as fp_pi:
        loop_again = True
        while loop_again:
            next_uuid = fp_pi.read(16)
            if next_uuid:
                story_list.append(UUID(bytes=next_uuid))
            else:
                loop_again = False
    return story_list