import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from app.storage.originals import IntegrityError, Original, OriginalStore


class OriginalsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.store = OriginalStore(self.root)

    def test_identical_content_is_idempotent_and_distinct_content_preserved(self):
        first = self.store.put(io.BytesIO(b"original"), max_bytes=100)
        again = self.store.put(io.BytesIO(b"original"), max_bytes=100)
        newer = self.store.put(io.BytesIO(b"replacement"), max_bytes=100)
        self.assertEqual(first, again)
        self.assertNotEqual(first.sha256, newer.sha256)
        self.assertEqual(len(list(self.root.iterdir())), 2)
        self.assertEqual(self.store.read(first, max_bytes=100), b"original")
        self.assertEqual(OriginalStore(self.root).read(newer, max_bytes=100), b"replacement")

    def test_interrupted_write_preserves_previous_original(self):
        previous = self.store.put(io.BytesIO(b"old"), max_bytes=100)
        class Broken:
            count = 0
            def read(self, size):
                self.count += 1
                if self.count == 1:
                    return b"partial"
                raise OSError("synthetic interruption")
        with self.assertRaises(OSError):
            self.store.put(Broken(), max_bytes=100)
        self.assertEqual(self.store.read(previous, max_bytes=100), b"old")
        self.assertEqual([p.name for p in self.root.iterdir()], [previous.sha256])

    def test_limits_and_exact_boundary(self):
        item = self.store.put(io.BytesIO(b"abc"), max_bytes=3)
        with self.assertRaises(ValueError):
            self.store.put(io.BytesIO(b"abcd"), max_bytes=3)
        with self.assertRaises(ValueError):
            self.store.read(item, max_bytes=2)
        for limit in [0, -1, True, 1.5]:
            with self.assertRaises(ValueError):
                self.store.put(io.BytesIO(b"x"), max_bytes=limit)
        self.assertEqual(self.store.read(item, max_bytes=3), b"abc")

    def test_untrusted_keys_never_become_paths(self):
        for key in ["../outside", "D:/secret", "A" * 64, "a" * 63, "a" * 64 + "/file"]:
            with self.assertRaises(ValueError):
                self.store.read(Original(key, 0), max_bytes=10)

    def test_corruption_detected_in_read_and_duplicate_publish(self):
        item = self.store.put(io.BytesIO(b"abc"), max_bytes=3)
        (self.root / item.sha256).write_bytes(b"xyz")
        with self.assertRaises(IntegrityError):
            self.store.read(item, max_bytes=3)
        with self.assertRaises(IntegrityError):
            self.store.put(io.BytesIO(b"abc"), max_bytes=3)
        self.assertEqual((self.root / item.sha256).read_bytes(), b"xyz")

    def test_missing_root_and_non_binary_stream_rejected(self):
        with self.assertRaises(FileNotFoundError):
            OriginalStore(self.root / "missing")
        with self.assertRaises(TypeError):
            self.store.put(io.StringIO("text"), max_bytes=100)
        self.assertEqual(list(self.root.iterdir()), [])

if __name__ == "__main__":
    unittest.main()
