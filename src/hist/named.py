from collections import defaultdict, Counter
from inspect import signature, Parameter
from boost_histogram import axis
from .core import BaseHist


class NamedHist(BaseHist):

    _sentinel = object()

    def __init___(self, *axes: axis, **kwargs):
        super(*axes, **kwargs)
        self._axes_names_to_ixs = defaultdict(lambda: self._sentinel, {ax.name: ix for ix, ax in enumerate(self.axes)})
        self._fill_params_to_ignore = {k for k, param in signature(self.fill).parameters.items()
                                       if param.kind != Parameter.KEYWORD_ONLY}

    def _validate_axes(self):
        for ix, ax in enumerate(self.axes):
            if ax.name is None:
                raise ValueError(f'{ix}. axis `{ax}` doesn\'t have a name.')

    def fill(self, **kwargs):
        args = []
        for k in list(kwargs.keys()):
            if k not in self._fill_params_to_ignore:
                if self._axes_names_to_ixs[k] is self._sentinel:
                    raise ValueError(f'Invalid axis name `{k}`. Valid options are: `{self._axes_names_to_ixs.keys()}`.')
                args.append((self._axes_names_to_ixs[k], kwargs.pop(k)))

        args = tuple(v for k, v in sorted(args, key=lambda kv: kv[0]))
        super().fill(*args, **kwargs)

    def __getitem__(self, item):
        if isinstance(item, dict):
            for k in item.keys():
                if not isinstance(k, (int, str)):
                    raise ValueError(f'All keys for dictionary-based indexing must be either `int` or `str`, '
                                     f'found `{type(k).__name__}`.')
            indices = [(ix if isinstance(ix, int) else self._axes_names_to_ixs[ix]) for ix in item.keys()]

            if any((lambda i: i is self._sentinel, indices)):
                # if any of the names failed to match
                wrong_names = [k for k in item.keys() if self._axes_names_to_ixs[k] is self._sentinel]
                raise ValueError(f'Invalid ax name(s): `{", ".join(wrong_names)}`.')

            counter = Counter(indices)
            if counter.most_common(1)[0][0] != 1:
                # if we have duplicates
                ixs_to_names = {ix: name for name, ix in self._axes_names_to_ixs}
                # since dict has unique keys, invalid combination must've come from int/str mixing
                duplicate_ixs = [(ix, ixs_to_names[ix]) for ix, count in counter.items() if count > 1]
                raise ValueError(f'Found duplicate indices for following entries: `{duplicate_ixs}`.')

            item = dict(zip(indices, item.values()))

        super().__getitem__(item)
