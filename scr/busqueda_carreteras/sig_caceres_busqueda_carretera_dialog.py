# -*- coding: utf-8 -*-
"""
Modulo de busqueda por carretera

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
    select_row_table, zoom_extension, transform_coordinates,toggle_line_edits
from scr.servicios_web import BUSCAR_CARRETERA_NOMBRE, BUSCAR_CARRETERA_CODIGO, \
    BUSCAR_PK_CODIGO_CARRETERA_TODOS, POSICION_CODIGO_CARRETERA_PK, POSICION_CODIGO_CARRETERA
from scr.mensajes import *

from qgis.utils import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sig_caceres_busqueda_carreteras.ui'))

CABECERA_TABLA_CARRETERAS = ("DENOMINACIÓN", "CÓDIGO")
ANCHO_COLUMNAS_CARRETERAS = (350, 100)


class SigCaceresBusquedaCarretera(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent_obj, parent=None):
        """Constructor."""
        super(SigCaceresBusquedaCarretera, self).__init__(parent)
        self.setupUi(self)
        self.canvas = qgis.utils.iface.mapCanvas()
        self.__reset()

        self.parent_obj = parent_obj
        self.codigo_carretera = None
        self.lineEdit_carretera.textChanged.connect(
            lambda: toggle_line_edits(line_edit_1=self.lineEdit_carretera, line_edit_2=self.lineEdit_codigo))
        self.lineEdit_codigo.textChanged.connect(
            lambda: toggle_line_edits(line_edit_1=self.lineEdit_carretera, line_edit_2=self.lineEdit_codigo))
        self.lineEdit_carretera.returnPressed.connect(self.busqueda)
        self.lineEdit_codigo.returnPressed.connect(self.busqueda)
        self.tableWidget.clicked.connect(self.get_pk)
        self.pushButton_clean.clicked.connect(self.__reset)
        self.pushButton_zoom.clicked.connect(self.zoom)

    def __reset(self):
        self.lineEdit_carretera.clear()
        self.lineEdit_codigo.clear()
        self.comboBox_pk.clear()
        self.comboBox_pk.setEnabled(False)
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
        self.dict_respuesta = {}
        data_dict = json.loads(datos)
        lista_datos = set()
        for dat in data_dict:
            codigo = str(dat["codigo"])
            pk = str(dat["pk"])
            coordenadas = [dat["wgS84_X"], dat["wgS84_Y"]]
            if codigo not in self.dict_respuesta:
                self.dict_respuesta[codigo] = {}
            self.dict_respuesta[codigo][pk] = coordenadas
            lista_datos.add((dat["denominacion"], str(dat["codigo"])))

        return lista_datos

    def busqueda(self):
        """
        Realiza la busqueda de una carretera,por nombre o codigo de carretera
        @param text:
        @return:
        """
        texto_nombre = self.lineEdit_carretera.text()
        texto_codigo = self.lineEdit_codigo.text()
        if texto_nombre not in (None, '') and texto_codigo in (None, ''):
            url = BUSCAR_CARRETERA_NOMBRE + f'{texto_nombre}'
        elif texto_codigo not in (None, '') and texto_nombre in (None, ''):
            url = BUSCAR_CARRETERA_CODIGO + f'{texto_codigo}'
        elif texto_nombre not in (None, '') and texto_codigo not in (None, ''):
            warning_message(header='Aviso', message='Solo se puede buscar por un campo')
            return None
        else:
            warning_message(header='Aviso', message='Introduzca un texto búsqueda')
            return None
        response, value = request_service_gis_caceres(url=url)

        if response == 0:
            datos = self.datos2list(datos=value)
            add_items_to_table(_data=datos, _table=self.tableWidget, _header=CABECERA_TABLA_CARRETERAS,
                               _size_columns=ANCHO_COLUMNAS_CARRETERAS, _tooltips=None, _align=None)
            self.tableWidget.setColumnHidden(2, True)
        elif response == 1:
            warning_message(header='Aviso', message='No hay coincidencias en la búsqueda')

    def get_pk(self):
        """
        Obtiene los pk de la carretera y los carga en el combo
        """
        self.comboBox_pk.clear()
        self.comboBox_pk.setEnabled(True)

        self.codigo_carretera = select_row_table(_table=self.tableWidget, _col=1)
        pk_lista = list(self.dict_respuesta.get(self.codigo_carretera, {}).keys())
        pk_lista_ordenada = sorted(pk_lista, key=int)
        self.comboBox_pk.addItem('')
        for dat in pk_lista_ordenada:
            self.comboBox_pk.addItem(dat)
        self.pushButton_zoom.setEnabled(True)

    def zoom(self):
        """
        zoom al objeto
        """
        if self.codigo_carretera:
            pk = self.comboBox_pk.currentText()
            x, y = None, None
            if pk not in ('', None):
                x, y = self.dict_respuesta[self.codigo_carretera][pk]
            else:
                warning_message(header='Aviso', message='Debe seleccionar un PK')
                return None

            coordenada_x = x
            coordenada_y = y

            project_crs = QgsProject.instance().crs().authid()
            crs_actual = str(project_crs).split(':')[-1]
            if crs_actual != '4326':
                coordenada_x, coordenada_y = transform_coordinates(x=coordenada_x, y=coordenada_y,
                                                                   source_crs='EPSG:4326', dest_crs=project_crs)
            zoom_extension(coord_x_pto=coordenada_x, coord_y_pto=coordenada_y, extension=50)
        else:
            warning_message(header='Aviso', message='No hay carretera seleccionada')

    def run(self):
        """
        Run
        """
        self.show()
        self.exec_()
