import base64
import gzip
import unittest

from export_case import after, apply_transforms, before


class ExportTest(unittest.TestCase):
    def test_combinations_preserve_bytes_and_decode_to_original(self):
        for rows in ([], ["hello", "世界"], ["", "a\nb"]):
            for compress in (False, True):
                for encode in (False, True):
                    with self.subTest(rows=rows, compress=compress, encode=encode):
                        actual = after(iter(rows), compress, encode)
                        self.assertEqual(before(iter(rows), compress, encode), actual)
                        decoded = base64.b64decode(actual) if encode else actual
                        decoded = gzip.decompress(decoded) if compress else decoded
                        self.assertEqual("\n".join(rows).encode("utf-8"), decoded)

    def test_generator_consumed_once_before_transforms(self):
        for implementation in (before, after):
            seen = []

            def rows():
                for row in ("a", "b"):
                    seen.append(row)
                    yield row

            self.assertEqual(b"a\nb", implementation(rows()))
            self.assertEqual(["a", "b"], seen)

    def test_input_exception_is_not_swallowed(self):
        for implementation in (before, after):
            with self.assertRaises(TypeError):
                implementation(["valid", None], True, True)

    def test_transform_order_calls_once_and_stops_at_failure(self):
        calls = []

        def first(value):
            calls.append(("first", value))
            return value + b"1"

        def failing(value):
            calls.append(("failing", value))
            raise ValueError("transform failed")

        def last(value):
            calls.append(("last", value))
            return value

        with self.assertRaisesRegex(ValueError, "transform failed"):
            apply_transforms(b"start", [first, failing, last])
        self.assertEqual([("first", b"start"), ("failing", b"start1")], calls)


if __name__ == "__main__":
    unittest.main()
