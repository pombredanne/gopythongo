# -* encoding: utf-8 *-
from gopythongo.initializers import BaseInitializer


class PbuilderFpmAptlyInitializer(BaseInitializer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def initializer_name(self) -> str:
        return "pbuilder_deb"

    def build_config(self) -> str:
        return ""


initializer_class = PbuilderFpmAptlyInitializer