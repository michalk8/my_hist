from collections import defaultdict, Counter
from inspect import signature, Parameter
from boost_histogram import axis
from .general import Hist


class NamedHist(Hist):

    _sentinel = object()

    def __init__(self, *axes: axis, **kwargs):
        super().__init__(*axes, **kwargs)
        # ignore these keys when calling .fill
        self._fill_params_to_ignore = {
            k
            for k, param in signature(super().fill).parameters.items()
            if param.kind == Parameter.KEYWORD_ONLY
        }

    def _validate_axes(self):
        for ix, ax in enumerate(self.axes):
            if ax.name is None:
                raise ValueError(f"{ix}. axis `{ax}` doesn't have a name.")

        self._axes_names_to_ixs = defaultdict(
            lambda: self._sentinel, {ax.name: ix for ix, ax in enumerate(self.axes)}
        )
        duplicates = [
            name
            for name, count in Counter((a.name for a in self.axes)).items()
            if count > 1
        ]
        if duplicates:
            raise ValueError(f"Following axis names are not unique: `{duplicates}`.")

    def fill(self, *args, **kwargs):
        if len(args) != 0:  # we keep the args to retain the signature from the parent
            raise RuntimeError("Only keyword arguments are supported.")
        args = []
        for name in list(kwargs.keys()):
            if name not in self._fill_params_to_ignore:  # user could have supplied weight, don't remove it
                if name not in self._axes_names_to_ixs:
                    raise ValueError(
                        f"Invalid axis name `{name}`. "
                        f"Valid options are: `{list(self._axes_names_to_ixs.keys())}`."
                    )
                args.append((self._axes_names_to_ixs[name], kwargs.pop(name)))

        args = tuple(
            value for name, value in sorted(args, key=lambda name_value: name_value[0])
        )  # sort by axis indices
        return super().fill(*args, **kwargs)

    def __getitem__(self, item):
        if isinstance(item, dict):
            for k in item.keys():
                if not isinstance(k, (int, str)):
                    raise TypeError(
                        f"All keys for dictionary-based indexing must be either `int` or `str`, "
                        f"found `{type(k).__name__}`."
                    )
            indices = [
                (ix if isinstance(ix, int) else self._axes_names_to_ixs[ix])
                for ix in item.keys()
            ]

            if any(map(lambda i: i is self._sentinel, indices)):
                # if any of the names failed to match
                wrong_names = [
                    str(k)
                    for k in item.keys()
                    if self._axes_names_to_ixs[k] is self._sentinel
                ]
                raise ValueError(
                    f'Invalid ax name(s): `{", ".join(wrong_names)}`. ',
                    f"Valid options are: `{list(self._axes_names_to_ixs.keys())}`.",
                )

            counter = Counter(indices)
            if counter.most_common(1)[0][1] > 1:
                # if we have duplicates
                ixs_to_names = {
                    ix: name for name, ix in self._axes_names_to_ixs.items()
                }
                # since dict has unique keys, invalid combination must've come from int/str mixing
                duplicate_ixs = [
                    (ix, ixs_to_names[ix]) for ix, count in counter.items() if count > 1
                ]
                raise ValueError(
                    f"Found duplicate indices for following entries: `{duplicate_ixs}`."
                )

            item = dict(zip(indices, item.values()))

        return super().__getitem__(item)
