# -*- coding: utf-8 -*-
"""
Modulo de busqueda por barrio

"""
__author__ = "SIG Caceres"
__copyright__ = "Copyright 2024, SIG Caceres"
__credits__ = ["SIG Caceres"]

__version__ = "1.1.0"
__maintainer__ = "SIG Cáceres"
__email__ = "https://sig.caceres.es/"
__status__ = "Production"

import os
import qgis
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtGui import QColor
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
import requests
import json

# Initialize Qt resources from file resources.py

from qgis.core import *  # No borrar
from scr.funciones_util import request_service_gis_caceres, add_items_to_table, warning_message, \
    select_row_table, zoom_extension, transform_coordinates,select_columns_table
from scr.servicios_web import BUSCAR_BARRIO_NOMBRE
from scr.mensajes import *

from qgis.utils import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sig_caceres_busqueda_barrios.ui'))

CABECERA_TABLA_BARRIOS = ("NOMBRE", "X", "Y")
ANCHO_COLUMNAS_BARRIOS = (350, 100, 100)


class SigCaceresBusquedaBarrio(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent_obj, parent=None):
        """Constructor."""
        super(SigCaceresBusquedaBarrio, self).__init__(parent)
        self.setupUi(self)
        self.canvas = qgis.utils.iface.mapCanvas()
        self.__reset()

        self.parent_obj = parent_obj

        self.lineEdit_barrio.returnPressed.connect(self.busqueda)
        self.tableWidget.clicked.connect(self.genera_entidad)
        self.pushButton_clean.clicked.connect(self.__reset)
        self.pushButton_zoom.clicked.connect(self.zoom)

    def __reset(self):
        self.lineEdit_barrio.clear()
        self.tableWidget.clearSelection()
        self.tableWidget.clearContents()
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.pushButton_zoom.setEnabled(False)

    def datos2list(self, datos):
        """
        Convertir respuesta en lista de datos
        """
        data_dict = json.loads(datos)
        lista_datos = []
        for dat in data_dict:
            lista_datos.append((dat["barrio"], str(dat["wgs84X"]), str(dat["wgs84Y"])))
        return lista_datos

    def busqueda(self):
        """
        Realiza la busqueda de un barrio, por nombre
        @param text:
        @return:
        """
        texto_nombre = self.lineEdit_barrio.text()
        if texto_nombre not in (None, ''):
            url = BUSCAR_BARRIO_NOMBRE+f'{texto_nombre}'
        else:
            warning_message(header='Aviso', message='Introduzca un texto búsqueda')
            return None
        response, value = request_service_gis_caceres(url=url)

        if response == 0:
            datos = self.datos2list(datos=value)
            add_items_to_table(_data=datos, _table=self.tableWidget, _header=CABECERA_TABLA_BARRIOS,
                               _size_columns=ANCHO_COLUMNAS_BARRIOS, _tooltips=None, _align=None)
            self.tableWidget.setColumnHidden(1, True)
            self.tableWidget.setColumnHidden(2, True)

        elif response == 1:
            warning_message(header='Aviso', message='No hay coincidencias en la búsqueda')

    def genera_entidad(self):
        self.resultado = select_columns_table(_table=self.tableWidget, _cols=[0, 1, 2])
        self.pushButton_zoom.setEnabled(True)

    def zoom(self):
        """
        zoom al objeto
        """
        if self.resultado:
            _,coordenada_x,coordenada_y = self.resultado
            coordenada_x = float(coordenada_x)
            coordenada_y = float(coordenada_y)
            project_crs = QgsProject.instance().crs().authid()
            crs_actual = str(project_crs).split(':')[-1]
            if crs_actual != '4326':
                coordenada_x, coordenada_y = transform_coordinates(x=coordenada_x, y=coordenada_y,
                                                                   source_crs='EPSG:4326', dest_crs=project_crs)
            zoom_extension(coord_x_pto=coordenada_x, coord_y_pto=coordenada_y, extension=50)
        else:
            warning_message(header='Aviso', message='No hay barrio seleccionado')

    def run(self):
        """
        Run
        """
        self.show()
        self.exec_()
