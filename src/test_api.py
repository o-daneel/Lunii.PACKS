import unittest
import hexdump

from pkg.api.stories import *
from pkg.api.device import *
from pkg.api.constants import lunii_generic_key


class testLunii_API(unittest.TestCase):

    def test_1_stories(self):
        
        # getting name of all stories
        count = 0
        for key in UUID_DB.keys():
            if UUID_DB[key].get('title'):
                count += 1
                assert story_name(key) == UUID_DB[key].get('title')
        print(count)
        assert count

        # unknown story
        unknown_uuid = UUID("00000000-0000-0000-0000-000000000000")
        assert story_name(unknown_uuid) == STORY_UNKNOWN

    def test_2_story_feed(self):
        stories_list = feed_stories("./test/_v2/")
        for story in stories_list:
            print(f"{story} - {story_name(story)}")

    def test_3_device(self):
        my_dev = LuniiDevice("./test/_v2/")

        assert my_dev.fw_vers_major == 2
        assert my_dev.fw_vers_minor >= 0x16
        assert my_dev.snu
        assert my_dev.raw_devkey

        print(my_dev)

    def test_4_find_devices(self):
        dev_list = find_devices("./test/_v2/")
        print(dev_list)

    def test_5_stories(self):
        slist = StoryList()
        uuid_a = UUID("9D9521E5-84AC-4CC8-9B09-8D0AFFB5D68A")
        uuid_b = UUID("22137B29-8646-4335-8069-4A4C9A2D7E89")
        uuid_c = UUID("9C836C24-34C4-4CC1-B9E6-D8646C8D9CF1")

        slist.append(uuid_a)

        # check full eq with -
        assert "9D9521E5-84AC-4CC8-9B09-8D0AFFB5D68A" in slist

        # check full eq no -
        assert "9D9521E584AC4CC89B098D0AFFB5D68A" in slist

        # check case
        assert "9d9521e584ac4cc89b098d0affb5d68a" in slist

        # check partial end
        assert "d68a" in slist
        assert "09-8D0AFFB5D68A" in slist

        # check partial beg
        assert "9d95" in slist
        assert "9D9521E5-84" in slist

        # check partial mid
        assert "1E584AC" in slist
        assert "1E5-84AC" in slist

        ulist = slist.full_uuid("1E584AC")
        assert len(ulist) == 1
        assert ulist[0] == uuid_a

        # single match
        slist.append(uuid_b)
        ulist = slist.full_uuid("1E584AC")
        assert len(ulist) == 1
        assert ulist[0] == uuid_a
        ulist = slist.full_uuid("4335")
        assert len(ulist) == 1
        assert ulist[0] == uuid_b
        ulist = slist.full_uuid("FFFF")
        assert len(ulist) == 0

        # match multiple
        slist.append(uuid_c)
        ulist = slist.full_uuid("46")
        assert len(ulist) >= 1

    def test_v2crypto(self):
        my_dev = LuniiDevice("./test/_v2")

        with open("./test/_v2/.content/1BBA473C/bt", "rb") as bt:
            buffer_bt = bt.read()
        with open("./test/_v2/.content/1BBA473C/ri", "rb") as ri:
            buffer_ri = ri.read(0x40)

        # deciphering test
        assert len(buffer_bt) == len(buffer_ri)
        assert buffer_bt != buffer_ri

        print("bt:")
        hexdump.hexdump(buffer_bt)
        print("ri:")
        hexdump.hexdump(buffer_ri)

        plain = my_dev.decipher(buffer_bt, my_dev.device_key, None, 0, 0x40)

        print("dec(bt):")
        hexdump.hexdump(plain)

        assert len(buffer_bt) == len(plain)
        assert buffer_bt != plain
        assert buffer_ri == plain

        # ciphering test
        ciphered = my_dev.cipher(plain, my_dev.device_key, None, 0, 0x40)
        print("enc(dec(bt)):")
        hexdump.hexdump(ciphered)

        assert len(plain) == len(ciphered)
        assert ciphered != plain
        assert ciphered == buffer_bt

    def test_v3crypto(self):
        my_dev = LuniiDevice("./test/_v3")

        # with open("../test/_v2/.content/4CDF38C6/bt", "rb") as bt:
        #     buffer_bt = bt.read()
        # with open("../test/_v2/.content/4CDF38C6/ri", "rb") as ri:
        #     buffer_ri = ri.read(0x40)

        # # deciphering test
        # assert len(buffer_bt) == len(buffer_ri)
        # assert buffer_bt != buffer_ri

        # print("bt:")
        # hexdump.hexdump(buffer_bt)
        # print("ri:")
        # hexdump.hexdump(buffer_ri)

        # plain = my_dev.decipher(buffer_bt, my_dev.device_key, None, 0, 0x40)

        # print("dec(bt):")
        # hexdump.hexdump(plain)

        # assert len(buffer_bt) == len(plain)
        # assert buffer_bt != plain
        # assert buffer_ri == plain

        # # ciphering test
        # ciphered = my_dev.cipher(plain, my_dev.device_key, None, 0, 0x40)
        # print("enc(dec(bt)):")
        # hexdump.hexdump(ciphered)

        # assert len(plain) == len(ciphered)
        # assert ciphered != plain
        # assert ciphered == buffer_bt

        pass

if __name__ == '__main__':
    unittest.main()
