import cmake_saver
import unittest


class TestUserInterface(unittest.TestCase):
    def test_main(self):
        self.assertRaises(SystemExit, cmake_saver.main)


if __name__ == '__main__':
    unittest.main()
