# Core
from fsociety.core.menu import tools_cli

from .photon import photon
from .xsstrike import xsstrike
from .nuclei import nuclei

__tools__ = [xsstrike, photon, nuclei]


def cli():
    tools_cli(__name__, __tools__)
