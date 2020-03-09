from hist import axis, NamedHist
import unittest


class NamedHistTestCase(unittest.TestCase):
    def test_only_named_axes(self):
        with self.assertRaises(ValueError):
            h = NamedHist(axis.Regular(10, 0, 1), axis.Regular(10, 0, 1, name="y"))

    def test_only_kwargs_fill(self):
        h = NamedHist(axis.Regular(10, 0, 1, name="x"))
        with self.assertRaises(RuntimeError):
            h.fill([0.35, 0.35, 0.45])

    def test_wrong_key_type(self):
        h = NamedHist(axis.Regular(10, 0, 1, name="x"))
        h.fill(x=[0.35, 0.35, 0.45])

        with self.assertRaises(TypeError):
            _ = h[{object: 2}]

    def test_invalid_ax_names(self):
        h = NamedHist(axis.Regular(10, 0, 1, name="x"))

        with self.assertRaises(ValueError):
            h.fill(y=[0.35, 0.35, 0.45])

    def test_duplicate_key(self):
        h = NamedHist(axis.Regular(10, 0, 1, name="x"))
        h.fill(x=[0.35, 0.35, 0.45])

        with self.assertRaises(ValueError):
            _ = h[{"x": 3, 0: 2}]  # x is the 0th index

    def test_key_not_found(self):
        h = NamedHist(axis.Regular(10, 0, 1, name="x"))
        h.fill(x=[0.35, 0.35, 0.45])

        with self.assertRaises(ValueError):
            _ = h[{"y": 3, 0: 2}]

    def test_basic_usage(self):
        h = NamedHist(
            axis.Regular(10, 0, 1, name="x")
        )  # NamedHist should require axis.Regular to have a name set
        h.fill(x=[0.35, 0.35, 0.45])  # Fill should be keyword only, with the names

        self.assertEqual(h[2], 0)
        self.assertEqual(h[3], 2)
        self.assertEqual(h[4], 1)
        self.assertEqual(h[5], 0)


if __name__ == "__main__":
    unittest.main()
