from typing import Optional
import boost_histogram.axis as bha


class NamedAxis(bha.Axis):
    @property
    def name(self):
        return self.metadata["name"]

    @name.setter
    def name(self, value):
        self.metadata["name"] = value


class Regular(bha.Regular, NamedAxis):
    def __init__(
        self,
        bins,
        start,
        stop,
        *,
        name=None,
        underflow=True,
        overflow=True,
        growth=False,
        circular=False,
        transform=None
    ):
        metadata = dict(name=name)
        super().__init__(
            bins,
            start,
            stop,
            metadata=metadata,
            underflow=underflow,
            overflow=overflow,
            growth=growth,
            circular=circular,
            transform=transform,
        )


class Variable(bha.Variable, NamedAxis):
    pass


class Integer(bha.Integer, NamedAxis):
    pass


class Bool(bha.Integer, NamedAxis):
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        circular: bool = False,
        growth: bool = False
    ):
        metadata = dict(name=name)
        super().__init__(
            start=0,
            stop=2,
            metadata=metadata,
            underflow=False,
            overflow=False,
            circular=circular,
            growth=growth,
        )


class IntCategory(bha.IntCategory, NamedAxis):
    pass


class StrCategory(bha.StrCategory, NamedAxis):
    pass
