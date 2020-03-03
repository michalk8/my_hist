from abc import abstractmethod
import boost_histogram as bha


class BaseHist(bha.Histogram):

    def __init__(self,
                 x_axis: bha.axis,
                 y_axis: bha.axis,
                 z_axis: bha.axis,
                 **kwargs):
        super().__init__(x_axis, y_axis, z_axis, **kwargs)
        self._validate_axes()

    @abstractmethod
    def _validate_axes(self):
        pass
