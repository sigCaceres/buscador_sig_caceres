# -*- coding: utf-8 -*-
__author__ = "SIG Caceres"
__copyright__ = "Copyright 2024, SIG Caceres"
__credits__ = ["SIG Caceres"]

__version__ = "1.1.0"
__maintainer__ = "SIG Cáceres"
__email__ = "https://sig.caceres.es/"
__status__ = "Production"

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'buscador_sig_caceres_dialog_base.ui'))
class buscador_sig_caceresDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(buscador_sig_caceresDialog, self).__init__(parent)
        self.setupUi(self)
