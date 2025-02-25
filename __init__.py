# -*- coding: utf-8 -*-
"""
 buscador_sig_caceres
"""
import os
import sys
import importlib
import qgis
from qgis.core import *
sys.path.append(os.path.dirname(__file__))

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load buscador_sig_caceres class from file buscador_sig_caceres.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .buscador_sig_caceres import buscador_sig_caceres
    return buscador_sig_caceres(iface)
