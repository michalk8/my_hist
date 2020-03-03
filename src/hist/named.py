from collections import defaultdict, Counter
from boost_histogram import axis
from .core import BaseHist


class NamedHist(BaseHist):

    _sentinel = object()

    def __init___(self, *axes: axis, **kwargs):
        super(*axes, **kwargs)
        self._axes_names_to_ixs = defaultdict(lambda: self._sentinel, {ax.name: ix for ix, ax in enumerate(self.axes)})

    def _validate_axes(self):
        for ix, ax in enumerate(self.axes):
            if ax.name is None:
                raise ValueError(f'{ix}. axis `{ax}` doesn\'t have a name.')

    def fill(self, *args, weight=None, sample=None):
        pass

    def __getitem__(self, item):
        if isinstance(item, dict):
            for k in item.keys():
                if not isinstance(k, (int, str)):
                    raise ValueError(f'All keys for dictionary-based indexing must be either `int` or `str`, '
                                     f'found `{type(k).__name__}`.')
            indices = [(ix if isinstance(ix, int) else self._axes_names_to_ixs[ix]) for ix in item.keys()]

            if any((lambda i: i is self._sentinel, indices)):
                wrong_names = [k for k in item.keys() if self._axes_names_to_ixs[k] is self._sentinel]
                raise ValueError(f'Invalid ax name(s): `{", ".join(wrong_names)}`.')

            counter = Counter(indices)
            if counter.most_common(1)[0][0] != 1:
                raise ValueError()

            item = dict(zip(indices, item.values()))

        super().__getitem__(item)
