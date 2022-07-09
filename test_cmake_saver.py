import cmake_saver
import unittest


class TestUserInterface(unittest.TestCase):

    def test_main(self):
        self.assertRaises(SystemExit, cmake_saver.main)

    def test_this_should_fail(self):
        self.assertEquals(1, 0)


if __name__ == '__main__':
    unittest.main()
