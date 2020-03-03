from .core import BaseHist


class NamedHist(BaseHist):

    def _validate_axes(self):
        for ix, ax in enumerate(self.axes):
            if ax.name is None:
                raise ValueError(f'{ix}. axis `{ax}` doesn\'t have a name.')
