from abc import abstractmethod
import boost_histogram as bha


class BaseHist(bha.Histogram):

    def __init__(self,
                 *axes: bha.axis,
                 **kwargs):
        super().__init__(*axes, **kwargs)
        self._validate_axes()

    @abstractmethod
    def _validate_axes(self):
        pass
