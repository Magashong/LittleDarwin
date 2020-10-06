import os
import sys
import unittest
import tempfile
import base64
import zipfile
from io import BytesIO

from littledarwin import LittleDarwin


class TestLittleDarwin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.videostoreZipContentBase64 = b'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dmEvbnVsL3N0dWR5L3ZpZGVvc3RvcmUvT3JpZ2luYWwvVVQFAANebHxfdXgLAAEE6AMAAAToAwAAUEsBAh4DFAAAAAgAF3lGUWKBnWnsAQAARQcAAEoAGAAAAAAAAQAAAICBvAIAAHZpZGVvc3RvcmUvc3JjL3Rlc3QvamF2YS9udWwvc3R1ZHkvdmlkZW9zdG9yZS9PcmlnaW5hbC9WaWRlb1N0b3JlVGVzdC5qYXZhVVQFAANebHxfdXgLAAEE6AMAAAToAwAAUEsBAh4DCgAAAAAAF3lGUQAAAAAAAAAAAAAAADsAGAAAAAAAAAAQAMBBLAUAAHZpZGVvc3RvcmUvc3JjL3Rlc3QvamF2YS9udWwvc3R1ZHkvdmlkZW9zdG9yZS9OdWxsQWRlcXVhdGUvVVQFAANebHxfdXgLAAEE6AMAAAToAwAAUEsBAh4DFAAAAAgAF3lGURWRnblWAQAAEgQAAFYAGAAAAAAAAQAAAICBoQUAAHZpZGVvc3RvcmUvc3JjL3Rlc3QvamF2YS9udWwvc3R1ZHkvdmlkZW9zdG9yZS9OdWxsQWRlcXVhdGUvTW92aWVfTnVsbEFkZXF1YXRlVGVzdC5qYXZhVVQFAANebHxfdXgLAAEE6AMAAAToAwAAUEsBAh4DFAAAAAgAF3lGUcbYvTHeAAAAbwEAAFkAGAAAAAAAAQAAAICBhwcAAHZpZGVvc3RvcmUvc3JjL3Rlc3QvamF2YS9udWwvc3R1ZHkvdmlkZW9zdG9yZS9OdWxsQWRlcXVhdGUvQ3VzdG9tZXJfTnVsbEFkZXF1YXRlVGVzdC5qYXZhVVQFAANebHxfdXgLAAEE6AMAAAToAwAAUEsBAh4DFAAAAAgAF3lGUVYv3dWjAAAAPAEAAEgAGAAAAAAAAQAAAICB+AgAAHZpZGVvc3RvcmUvc3JjL3Rlc3QvamF2YS9udWwvc3R1ZHkvdmlkZW9zdG9yZS9OdWxsQWRlcXVhdGUvQWxsVGVzdHMuamF2YVVUBQADXmx8X3V4CwABBOgDAAAE6AMAAFBLAQIeAxQAAAAIABd5RlG/Uuvx3gAAALQBAABXABgAAAAAAAEAAACAgR0KAAB2aWRlb3N0b3JlL3NyYy90ZXN0L2phdmEvbnVsL3N0dWR5L3ZpZGVvc3RvcmUvTnVsbEFkZXF1YXRlL1JlbnRhbF9OdWxsQWRlcXVhdGVUZXN0LmphdmFVVAUAA15sfF91eAsAAQToAwAABOgDAABQSwECHgMKAAAAAAAXeUZRAAAAAAAAAAAAAAAAQQAYAAAAAAAAABAAwEGMCwAAdmlkZW9zdG9yZS9zcmMvdGVzdC9qYXZhL251bC9zdHVkeS92aWRlb3N0b3JlL0phdmFsYW5jaGVBZGVxdWF0ZS9VVAUAA15sfF91eAsAAQToAwAABOgDAABQSwECHgMUAAAACAAXeUZRAl3Dwy0BAAC2AwAAYgAYAAAAAAABAAAAgIEHDAAAdmlkZW9zdG9yZS9zcmMvdGVzdC9qYXZhL251bC9zdHVkeS92aWRlb3N0b3JlL0phdmFsYW5jaGVBZGVxdWF0ZS9Nb3ZpZV9KYXZhbGFuY2hlQWRlcXVhdGVUZXN0LmphdmFVVAUAA15sfF91eAsAAQToAwAABOgDAABQSwECHgMKAAAAAAAXeUZRAAAAAAAAAAAAAAAAPQAYAAAAAAAAABAAwEHQDQAAdmlkZW9zdG9yZS9zcmMvdGVzdC9qYXZhL251bC9zdHVkeS92aWRlb3N0b3JlL1BJVGVzdEFkZXF1YXRlL1VUBQADXmx8X3V4CwABBOgDAAAE6AMAAFBLAQIeAxQAAAAIABd5RlGyhOgiUAEAABsDAABSABgAAAAAAAEAAACAgUcOAAB2aWRlb3N0b3JlL3NyYy90ZXN0L2phdmEvbnVsL3N0dWR5L3ZpZGVvc3RvcmUvUElUZXN0QWRlcXVhdGUvUmVndWxhck1vdmllVGVzdC5qYXZhVVQFAANebHxfdXgLAAEE6AMAAAToAwAAUEsBAh4DFAAAAAgAF3lGUfcPTxxQAQAAIwMAAFUAGAAAAAAAAQAAAICBIxAAAHZpZGVvc3RvcmUvc3JjL3Rlc3QvamF2YS9udWwvc3R1ZHkvdmlkZW9zdG9yZS9QSVRlc3RBZGVxdWF0ZS9OZXdSZWxlYXNlTW92aWVUZXN0LmphdmFVVAUAA15sfF91eAsAAQToAwAABOgDAABQSwECHgMUAAAACAAYeUZR35PhLxACAABXCQAATAAYAAAAAAABAAAAgIECEgAAdmlkZW9zdG9yZS9zcmMvdGVzdC9qYXZhL251bC9zdHVkeS92aWRlb3N0b3JlL1BJVGVzdEFkZXF1YXRlL1JlbnRhbFRl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'
        cls.videostoreZipContent = BytesIO(base64.decodebytes(cls.videostoreZipContentBase64))

    def setUp(self) -> None:
        self.tempDir = tempfile.TemporaryDirectory()
        self.videoStoreSourcePath = os.path.join(self.tempDir.name, "videostore", "src", "main")
        self.videoStoreBuildPath = os.path.join(self.tempDir.name, "videostore")

        print("Created temp directory: " + str(self.tempDir.name) + ".")

        zipObj = zipfile.ZipFile(self.videostoreZipContent)
        zipObj.extractall(path=self.tempDir.name)
        print("Extracted \"VideoStore\" project.")

    def tearDown(self) -> None:
        self.tempDir.cleanup()
        print("Deleted temp directory.")

    def testVideoStoreGenerateTraditionalMutants(self):
        argList = ['-m', '-p', self.videoStoreSourcePath, '-t', self.videoStoreBuildPath]
        print("Running LittleDarwin with arguments:\n" + " ".join(argList))

        try:
            sys.exit(LittleDarwin.main(argList))
        except SystemExit as e:
            self.assertEqual(int(e.code), 0)

    def testVideoStoreTraditionalBuild(self):
        argList = ['-m', '-b', '-p', self.videoStoreSourcePath, '-t', self.videoStoreBuildPath, '-c', "mvn,clean,test"]
        print("Running LittleDarwin with arguments:\n" + " ".join(argList))

        try:
            sys.exit(LittleDarwin.main(argList))
        except SystemExit as e:
            self.assertEqual(int(e.code), 0)


if __name__ == '__main__':
    unittest.main()
