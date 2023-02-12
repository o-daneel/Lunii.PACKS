import unittest

from pkg.api.stories import *
from pkg.api.device import *

class testLunii_API(unittest.TestCase):

    def test_1_stories(self):
        
        # getting name of all stories
        for key in STORY_PACKS.keys():
            assert story_name(key) == STORY_PACKS[key]

        # unknown story
        unknown_uuid = UUID("00000000-0000-0000-0000-000000000000")
        assert story_name(unknown_uuid) == STORY_UNKNOWN

    def test_2_story_feed(self):
        stories_list = feed_stories("./test/")
        for story in stories_list:
            print(f"{story} - {story_name(story)}")

    def test_3_device(self):
        my_dev = LuniiDevice("./test/")

        assert my_dev.fw_vers_major == 2
        assert my_dev.fw_vers_minor >= 0x16
        assert my_dev.snu
        assert my_dev.raw_devkey

        print(my_dev)

    def test_4_find_devices(self):
        dev_list = find_devices("./test/")
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


if __name__ == '__main__':
    unittest.main()
