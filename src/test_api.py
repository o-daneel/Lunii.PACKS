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


if __name__ == '__main__':
    unittest.main()
