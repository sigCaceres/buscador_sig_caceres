# -*- coding: utf-8 -*-
"""
Módulo de busqueda por coordenadas en el EPSG:25829

"""
__author__ = "SIG Caceres"
__copyright__ = "Copyright 2024, SIG Caceres"
__credits__ = ["SIG Caceres"]

__version__ = "1.1.0"
__maintainer__ = "SIG Cáceres"
__email__ = "https://sig.caceres.es/"
__status__ = "Production"


from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import *
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QDoubleValidator
# Initialize Qt resources from file resources.py

from qgis.core import *  # No borrar
from scr.funciones_util import *
from scr.mensajes import *
from qgis.utils import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sig_caceres_busqueda_coordenadas_25829.ui'))

class SigCaceresBusquedaCoordenadas25829(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent_obj, parent=None):
        """Constructor."""
        super(SigCaceresBusquedaCoordenadas25829, self).__init__(parent)
        self.setupUi(self)
        self.parent_obj = parent_obj
        validator = QDoubleValidator(0.0, 999999999999.0, 6)
        validator_negativo = QDoubleValidator(-999999999999.0, 999999999999.0, 6)
        self.lineEdit_x.setValidator(validator)
        self.lineEdit_y.setValidator(validator_negativo)
        self.__reset()
        self.pushButton_clean.clicked.connect(self.__reset)
        self.pushButton_zoom.clicked.connect(self.zoom)
    def __reset(self):
        self.lineEdit_x.clear()
        self.lineEdit_y.clear()

    def leer_coordenadas(self):
        """
        Funcion para leer coordenadas y hacer un zoom a su extension con 50m
        @return: True /False
        """
        try:
            isinstance(float(self.lineEdit_x.text()), float)
            isinstance(float(self.lineEdit_y.text()), float)

            coordenadas_x = float(self.lineEdit_x.text())
            coordenadas_y = float(self.lineEdit_y.text())
            project_crs = QgsProject.instance().crs().authid()
            crs_actual = str(project_crs).split(':')[-1]
            if crs_actual != '25829':
                coordenadas_x, coordenadas_y = transform_coordinates(x=coordenadas_x, y=coordenadas_y,
                                                                   source_crs='EPSG:25829', dest_crs=project_crs)

            return coordenadas_x, coordenadas_y

        except:
            QMessageBox.critical(self, 'Error', MENSAJE_ERROR_FORMATO_NO_25829,
                                 QMessageBox.Ok,
                                 QMessageBox.Ok)
    def zoom(self):
        """
        zoom al objeto
        """
        coordenadas = self.leer_coordenadas()
        if coordenadas:
            coordenadas_x, coordenadas_y = self.leer_coordenadas()
            zoom_extension(coord_x_pto=coordenadas_x, coord_y_pto=coordenadas_y, extension=50)
        else:
            pass

    def run(self):
        """Run method that performs all the real work"""
        self.show()
        self.exec_()

