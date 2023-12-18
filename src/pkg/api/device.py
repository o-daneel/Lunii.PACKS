import glob
import os
import shutil
import zipfile
import xxtea
import binascii
from pathlib import Path
from uuid import UUID

from tqdm import tqdm

from pkg.api.aes_keys import dev_iv, dev_key
from pkg.api.constants import *
from pkg.api.stories import StoryList


class LuniiDevice:
    stories: StoryList

    def __init__(self, mount_point):
        self.mount_point = mount_point

        # dummy values
        self.lunii_version = 0
        self.UUID = ""
        self.device_key = ""
        self.device_iv = ""
        self.snu = ""
        self.fw_vers_major = 0
        self.fw_vers_minor = 0
        self.fw_vers_subminor = 0
        self.memory_left = 0
        self.bt = b""

        # internal device details
        self.__feed_device()

        # internal stories
        self.stories = feed_stories(self.mount_point)

    # opens the .pi file to read all installed stories
    def __feed_device(self):
        
        mount_path = Path(self.mount_point)
        md_path = mount_path.joinpath(".md")

        with open(md_path, "rb") as fp_md:
            md_version = int.from_bytes(fp_md.read(2), 'little')

            if md_version == 6:
                self.__v3_parse(fp_md)
            elif md_version == 3:
                self.__v2_parse(fp_md)

    def __v2_parse(self, fp_md):
        self.lunii_version = LUNII_V2
        fp_md.seek(6)
        self.fw_vers_major = int.from_bytes(fp_md.read(2), 'little')
        self.fw_vers_minor = int.from_bytes(fp_md.read(2), 'little')
        self.snu = fp_md.read(8)
        
        fp_md.seek(0x100)
        self.raw_devkey = fp_md.read(0x100)
        dec = xxtea.decrypt(self.raw_devkey, lunii_generic_key, padding=False, rounds=lunii_tea_rounds(self.raw_devkey))
        # Reordering Key components
        self.device_key = dec[8:16] + dec[0:8]


    def __v3_parse(self, fp_md):
        self.lunii_version = LUNII_V3
        fp_md.seek(2)
        # reading fw version
        self.fw_vers_major = int.from_bytes(fp_md.read(1), 'little') - 0x30
        fp_md.read(1)
        self.fw_vers_minor = int.from_bytes(fp_md.read(1), 'little') - 0x30
        fp_md.read(1)
        self.fw_vers_subminor = int.from_bytes(fp_md.read(1), 'little') - 0x30
        # reading SNU
        fp_md.seek(0x1A)
        self.snu = binascii.unhexlify(fp_md.read(14).decode('utf-8'))
        # getting candidated for story bt file
        fp_md.seek(0x40)
        self.bt = fp_md.read(0x20)
        # forging keys based on md ciphered part
        self.fake_story_key = self.snu + b"\x00\x00"
        self.fake_story_iv = b"\x00\x00\x00\x00\x00\x00\x00\x00\x32\x33\x30\x32\x33\x30\x33\x30"
        # real keys if available
        self.device_key = dev_key
        self.device_iv = dev_iv

    def __v2_decipher(self, buffer, key, offset, dec_len):
        # checking offset
        if offset > len(buffer):
            offset = len(buffer)
        # checking len
        if offset + dec_len > len(buffer):
            dec_len = len(buffer) - offset
        # if something to be done
        if offset < len(buffer) and offset + dec_len <= len(buffer):
            plain = xxtea.decrypt(buffer[offset:dec_len], key, padding=False, rounds=lunii_tea_rounds(buffer[offset:dec_len]))
            ba_buffer = bytearray(buffer)
            ba_buffer[offset:dec_len] = plain
            buffer = bytes(ba_buffer)
        return buffer

    def __v3_decipher(self, buffer, key, iv, offset, len):
        pass

    def decipher(self, buffer, key, iv=None, offset=0, dec_len=512):
        if self.lunii_version == LUNII_V2:
            return self.__v2_decipher(buffer, key, offset, dec_len)
        else:
            return self.__v3_decipher(buffer, key, iv, offset, dec_len)

    def __v2_cipher(self, buffer, key, offset, enc_len):
        # checking offset
        if offset > len(buffer):
            offset = len(buffer)
        # checking len
        if offset + enc_len > len(buffer):
            enc_len = len(buffer) - offset
        # if something to be done
        if offset < len(buffer) and offset + enc_len <= len(buffer):
            ciphered = xxtea.encrypt(buffer[offset:enc_len], key, padding=False, rounds=lunii_tea_rounds(buffer[offset:enc_len]))
            ba_buffer = bytearray(buffer)
            ba_buffer[offset:enc_len] = ciphered
            buffer = bytes(ba_buffer)
        return buffer

    def __v3_cipher(self, buffer, key, iv, offset, len):
        pass

    def cipher(self, buffer, key, iv=None, offset=0, enc_len=512):
        if self.lunii_version == LUNII_V2:
            return self.__v2_cipher(buffer, key, offset, enc_len)
        else:
            return self.__v3_cipher(buffer, key, iv, offset, enc_len)

    @property
    def snu_hex(self):
        return self.snu
    
    def __repr__(self):
        repr_str  = f"Lunii device on \"{self.mount_point}\"\n"
        if self.lunii_version == LUNII_V2:
            repr_str += f"- firmware : v{self.fw_vers_major}.{self.fw_vers_minor}\n"
        else:
            repr_str += f"- firmware : v{self.fw_vers_major}.{self.fw_vers_minor}.{self.fw_vers_subminor}\n"
        repr_str += f"- snu      : {binascii.hexlify(self.snu_hex, ' ')}\n"
        repr_str += f"- dev key  : {binascii.hexlify(self.device_key, ' ')}\n"
        if self.lunii_version == LUNII_V3:
            repr_str += f"- dev iv   : {binascii.hexlify(self.device_iv, ' ')}\n"
        repr_str += f"- stories  : {len(self.stories)}x\n"
        return repr_str

    def export_all(self, out_path):
        if self.lunii_version == LUNII_V3:
            return
        
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
        # TO REMOVE SOON
        if self.lunii_version == LUNII_V3:
            return

        # is UUID part of existing stories
        if uuid not in self.stories:
            return None

        ulist = self.stories.full_uuid(uuid)
        if len(ulist) > 1:
            print(f"ERROR: at least {len(ulist)} match your pattern. Try a longer UUID.")
            for st in ulist:
                print(f"[{st} - {self.stories.name(str(st))}]")
            return None

        full_uuid = ulist[0]
        uuid = str(full_uuid).upper()[28:]

        # checking that .content dir exist
        content_path = Path(self.mount_point).joinpath(".content")
        if not content_path.is_dir():
            return None
        story_path = content_path.joinpath(uuid)
        if not story_path.is_dir():
            return None
        
        print(f"[{uuid} - {self.stories.name(uuid)}]")

        # Preparing zip file
        zip_path = Path(out_path).joinpath(f"{self.stories.name(uuid)}.{uuid}.plain.pk")
        # preparing file list
        story_flist = []
        for root, dirnames, filenames in os.walk(story_path):
            for filename in filenames:
                if filename == "bt":
                    continue
                story_flist.append(os.path.join(root, filename))

        with zipfile.ZipFile(zip_path, 'w') as zip_out:
            print("> Zipping story ...")
            pbar = tqdm(iterable=story_flist, total=len(story_flist), bar_format=TQDM_BAR_FORMAT)
            for file in pbar:
                target_name = Path(file).relative_to(story_path)
                pbar.set_description(f"Processing {target_name}")

                # Extract each file to another directory
                # decipher if necessary (mp3 / bmp / li / ri / si)
                data_plain = self.__get_plain_data(file)
                file_newname = self.__get_plain_name(file, uuid)
                zip_out.writestr(file_newname, data_plain)

            # adding uuid file
            print("> Adding UUID ...")
            zip_out.writestr("uuid.bin", full_uuid.bytes)

        return zip_path
    
    def import_dir(self, story_path):
        if self.lunii_version == LUNII_V3:
            return False
        
        print(story_path + "**/*.plain.pk")
        pkplain_list = glob.glob(os.path.join(story_path, "**/*.plain.pk"), recursive=True)
        pkv2_list = glob.glob(os.path.join(story_path, "**/*.v2.pk"), recursive=True)
        pk_list = list(pkplain_list)
        pk_list.append(pkv2_list)
        print(f"Importing {len(pk_list)} archives...")
        for pk in pk_list:
            print(f"> {pk}")
            self.import_story(pk)
        
        return True
    
    def import_story(self, story_path):
        # TO REMOVE SOON
        if self.lunii_version == LUNII_V3:
            return

        type = TYPE_UNK
        
        # identifying based on filename
        if story_path.lower().endswith('.plain.pk'):
            type = TYPE_PLAIN
        elif story_path.lower().endswith('.v2.pk'):
            type = TYPE_V2
        elif story_path.lower().endswith('.zip'):
            type = TYPE_ZIP
        else:
            # trying to figure out based on zip contents
            with zipfile.ZipFile(file=story_path) as zip_file:
                # reading all available files
                zip_contents = zip_file.namelist()
                bt_files = [entry for entry in zip_contents if entry.endswith("bt")]
                if bt_files:
                    bt_size = zip_file.getinfo(bt_files[0]).file_size
                    if bt_size == 0x20:
                        type = TYPE_V3
                    else:
                        type = TYPE_V2

        # processing story
        if type == TYPE_PLAIN:
            return self.import_story_plain(story_path)
        elif type == TYPE_ZIP:
            return self.import_story_zip(story_path)
        elif type == TYPE_V2:
            return self.import_story_v2(story_path)
        elif type == TYPE_V3:
            return self.import_story_v3(story_path)


    def import_story_plain(self, story_path):
        # opening zip file
        with zipfile.ZipFile(file=story_path) as zip_file:
            # reading all available files
            zip_contents = zip_file.namelist()
            if "uuid.bin" not in zip_contents:
                print("ERROR: No UUID file found in archive. Unable to add this story.")
                return False

            # getting UUID file
            new_uuid = UUID(bytes=zip_file.read("uuid.bin"))

            # checking if UUID already loaded
            if str(new_uuid) in self.stories:
                print("ERROR: This story is already loaded, aborting !")
                return False

            # decompressing story contents
            output_path = Path(self.mount_point).joinpath(f".content/{str(new_uuid).upper()[28:]}")
            if not output_path.exists():
                output_path.mkdir(parents=True)

            # Loop over each file
            count = 0
            pbar = tqdm(iterable=zip_contents, total=len(zip_contents), bar_format=TQDM_BAR_FORMAT)
            for file in pbar:
                count += 1
                if file == "uuid.bin":
                    continue
                pbar.set_description(f"Processing {file}")

                # Extract each zip file
                data_plain = zip_file.read(file)

                # updating filename, and ciphering header if necessary
                data = self.__get_ciphered_data(file, data_plain)
                file_newname = self.__get_ciphered_name(file)

                target: Path = output_path.joinpath(file_newname)

                # create target directory
                if not target.parent.exists():
                    target.parent.mkdir(parents=True)
                # write target file
                with open(target, "wb") as f_dst:
                    f_dst.write(data)

                # in case of v2 device, we need to prepare bt file 
                if self.lunii_version == LUNII_V2 and file.endswith("ri"):
                    self.bt = self.cipher(data[0:0x41], self.device_key)

        # creating authorization file : bt
        print("INFO : Authorization file creation...")
        bt_path = output_path.joinpath("bt")
        with open(bt_path, "wb") as fp_bt:
            fp_bt.write(self.bt)

        # updating .pi file to add new UUID
        self.stories.append(new_uuid)
        self.update_pack_index()

        return True

    def import_story_zip(self, story_path):
        # opening zip file
        with zipfile.ZipFile(file=story_path) as zip_file:
            # reading all available files
            zip_contents = zip_file.namelist()
            if "uuid.bin" not in zip_contents:
                print("ERROR: No UUID file found in archive. Unable to add this story.")
                return False

            # getting UUID file
            new_uuid = UUID(bytes=zip_file.read("uuid.bin"))

            # checking if UUID already loaded
            if str(new_uuid) in self.stories:
                print("ERROR: This story is already loaded, aborting !")
                return False

            # decompressing story contents
            output_path = Path(self.mount_point).joinpath(f".content/{str(new_uuid).upper()[28:]}")
            if not output_path.exists():
                output_path.mkdir(parents=True)

            # Loop over each file
            count = 0
            pbar = tqdm(iterable=zip_contents, total=len(zip_contents), bar_format=TQDM_BAR_FORMAT)
            for file in pbar:
                count += 1
                if file == "uuid.bin" or file.endswith("bt"):
                    continue
                pbar.set_description(f"Processing {file}")

                # Extract each zip file
                data_v2 = zip_file.read(file)

                if file.endswith("ni") or file.endswith("nm"):
                    data_plain = data_v2
                else:
                    data_plain = self.__v2_decipher(data_v2, lunii_generic_key, 0, 512)
                # updating filename, and ciphering header if necessary
                data = self.__get_ciphered_data(file, data_plain)
                file_newname = self.__get_ciphered_name(file)

                target: Path = output_path.joinpath(file_newname)

                # create target directory
                if not target.parent.exists():
                    target.parent.mkdir(parents=True)
                # write target file
                with open(target, "wb") as f_dst:
                    f_dst.write(data)

                # in case of v2 device, we need to prepare bt file 
                if self.lunii_version == LUNII_V2 and file.endswith("ri"):
                    self.bt = self.cipher(data[0:0x40], self.device_key)

        # creating authorization file : bt
        print("INFO : Authorization file creation...")
        bt_path = output_path.joinpath("bt")
        with open(bt_path, "wb") as fp_bt:
            fp_bt.write(self.bt)

        # updating .pi file to add new UUID
        self.stories.append(new_uuid)
        self.update_pack_index()

        return True

    def import_story_v2(self, story_path):
        pass

    def import_story_v3(self, story_path):
        print("ERROR : unsupported story format")
        pass

    def remove_story(self, short_uuid):
        if short_uuid not in self.stories:
            print("ERROR: This story is not present on your storyteller")
            return False

        ulist = self.stories.full_uuid(short_uuid)
        if len(ulist) > 1:
            print(f"ERROR: at least {len(ulist)} match your pattern. Try a longer UUID.")
            return False
        uuid = str(ulist[0])

        print(f"Removing {uuid[28:].upper()} - {self.stories.name(uuid)}...")

        # asking for confirmation
        answer = input("Are you sure ? [y/N] ")
        if answer.lower() not in ["y", "yes"]:
            return False

        # removing story contents
        st_path = Path(self.mount_point).joinpath(f".content/{uuid[28:]}")
        shutil.rmtree(st_path)

        # removing story from class
        self.stories.remove(ulist[0])
        # updating pack index file
        self.update_pack_index()

        return True

    def __get_plain_data(self, file):
        if not os.path.isfile(file):
            return b""

        # opening file
        with open(file, "rb") as fsrc:
            data = fsrc.read()

        # selecting key
        key = lunii_generic_key
        if file.endswith("bt"):
            key = self.device_key
        if file.endswith("ni") or file.endswith("nm"):
            key = None

        # process file with correct key
        if key:
            return self.decipher(data, key)

        return data

    def __get_plain_name(self, file, uuid):
        file = file.split(uuid.upper())[1]
        while file.startswith("\\") or file.startswith("/"):
            file = file[1:]

        if "rf/" in file or "rf\\" in file:
            return file+".bmp"
        if "sf/" in file or "sf\\" in file:
            return file+".mp3"
        if file.endswith("li") or file.endswith("ri") or file.endswith("si"):
            return file+".plain"

        # untouched name
        return file

    def __get_ciphered_data(self, file, data):
        # selecting key
        if self.lunii_version == LUNII_V2:
            key = lunii_generic_key
            iv = None
        else:
            # LUNII_V3
            key = self.fake_story_key
            iv = self.fake_story_iv
        if file.endswith("bt"):
            key = self.device_key
        if file.endswith("ni") or file.endswith("nm"):
            key = None

        # process file with correct key
        if key:
            return self.cipher(data, key, iv)

        return data


    def __get_ciphered_name(self, file):
        file = file.removesuffix('.plain')
        file = file.removesuffix('.mp3')
        file = file.removesuffix('.bmp')
        return file


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
    root_path = Path(root_path)
    pi_path = root_path.joinpath(".pi")
    md_path = root_path.joinpath(".md")
    cfg_path = root_path.joinpath(".cfg")
    content_path = root_path.joinpath(".content")

    if pi_path.is_file() and md_path.is_file() and cfg_path.is_file() and content_path.is_dir():
        return True
    return False
