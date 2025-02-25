# -*- coding: utf-8 -*-
"""
Módulo de busqueda por coordenadas en el EPSG:3046 por grados, minutos y segundos

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
import math
from PyQt5.QtGui import QDoubleValidator,QIntValidator

# Initialize Qt resources from file resources.py

from qgis.core import *  # No borrar
from scr.funciones_util import *
from qgis.utils import *
from scr.mensajes import *


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sig_caceres_busqueda_gradosminutosysegundos.ui'))


class SigCaceresBusquedaGradosMinutosYSegundos(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent_obj, parent=None):
        """Constructor."""
        super(SigCaceresBusquedaGradosMinutosYSegundos, self).__init__(parent)
        self.setupUi(self)
        self.parent_obj = parent_obj
        validator_float = QDoubleValidator(0.0, 999999999999.0, 6)
        validator_float_negativo = QDoubleValidator(-999999999999.0, 999999999999.0, 6)
        validator_integer=QIntValidator()
        self.lineEdit_segundos_x.setValidator(validator_float)
        self.lineEdit_minutos_x.setValidator(validator_integer)
        self.lineEdit_grados_x.setValidator(validator_integer)
        self.lineEdit_segundos_y.setValidator(validator_float)
        self.lineEdit_minutos_y.setValidator(validator_integer)
        self.lineEdit_grados_y.setValidator(validator_float)
        self.__reset()

        self.pushButton_clean.clicked.connect(self.__reset)
        self.pushButton_zoom.clicked.connect(self.zoom)

    def __reset(self):
        self.lineEdit_grados_x.clear()
        self.lineEdit_minutos_x.clear()
        self.lineEdit_segundos_x.clear()
        self.lineEdit_grados_y.clear()
        self.lineEdit_minutos_y.clear()
        self.lineEdit_segundos_y.clear()

    def leer_coordenadas(self):
        """
        Funcion para leer corrdenadas y hacer un zoom a su extension con 50m
        @return:
        """
        try:
            isinstance(int(self.lineEdit_grados_x.text()), int)
            isinstance(int(self.lineEdit_minutos_x.text()), int)
            isinstance(float(self.lineEdit_segundos_x.text()), float)
            isinstance(int(self.lineEdit_grados_y.text()), int)
            isinstance(int(self.lineEdit_minutos_y.text()), int)
            isinstance(float(self.lineEdit_segundos_y.text()), float)

            grados_X = float((((float(self.lineEdit_segundos_x.text()) / 60) + (
                float(self.lineEdit_minutos_x.text()))) / 60) + math.fabs(float(self.lineEdit_grados_x.text())))

            coordenadas_x = -grados_X
            coordenadas_y = float((((float(self.lineEdit_segundos_y.text()) / 60) + (
                float(self.lineEdit_minutos_y.text()))) / 60) + math.fabs(float(self.lineEdit_grados_y.text())))

            project_crs = QgsProject.instance().crs().authid()
            crs_actual = str(project_crs).split(':')[-1]
            if crs_actual != '4326':
                coordenadas_x, coordenadas_y = transform_coordinates(x=coordenadas_x, y=coordenadas_y,
                                                                   source_crs='EPSG:4326', dest_crs=project_crs)

            return coordenadas_x, coordenadas_y
        except:
            QMessageBox.critical(self, 'Error', MENSAJE_ERROR_FORMATO_NO_GMS,
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

