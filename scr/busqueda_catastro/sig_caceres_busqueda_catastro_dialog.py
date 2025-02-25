# -*- coding: utf-8 -*-
"""
Modulo de busqueda por catastro

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
    select_row_table, zoom_extension, transform_coordinates, toggle_line_edits_multiple, select_columns_table
from scr.servicios_web import BUSCAR_CATASTRO_URBANO_REFCAT, BUSCAR_CATASTRO_RUSTICO_REFCAT, \
    BUSCAR_CATASTRO_RUSTICA, BUSCAR_CATASTRO_URBANO_MANZANA
from scr.mensajes import *

from qgis.utils import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sig_caceres_busqueda_catastro.ui'))

CABECERA_TABLA_CATASTRO_URBANO = ("MANZANA", "PARCELA", "HOJA", "REFERENCIA CATASTRAL","X", "Y")
ANCHO_COLUMNAS_CATASTRO_URBANO = (90, 90, 90, 180, 20, 20)

CABECERA_TABLA_CATASTRO_RUSTICO = ("POLÍGONO", "PARCELA", "REFERENCIA CATASTRAL",  "X", "Y")
ANCHO_COLUMNAS_CATASTRO_RUSTICO = (110, 110, 180, 10, 10)


class SigCaceresBusquedaCatastro(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent_obj, parent=None):
        """Constructor."""
        super(SigCaceresBusquedaCatastro, self).__init__(parent)
        self.setupUi(self)
        self.canvas = qgis.utils.iface.mapCanvas()
        self.__reset()

        self.parent_obj = parent_obj
        self.ref_cat = None
        self.poligono = None
        self.parcela = None

        self.lineEdit_refcat.textChanged.connect(
            lambda: toggle_line_edits_multiple(line_edit_1=self.lineEdit_refcat, line_edit_2=self.lineEdit_poligono, line_edit_3=self.lineEdit_parcela))
        self.lineEdit_poligono.textChanged.connect(
            lambda: toggle_line_edits_multiple(line_edit_1=self.lineEdit_refcat, line_edit_2=self.lineEdit_poligono, line_edit_3=self.lineEdit_parcela))
        self.lineEdit_parcela.textChanged.connect(
            lambda: toggle_line_edits_multiple(line_edit_1=self.lineEdit_refcat, line_edit_2=self.lineEdit_poligono, line_edit_3=self.lineEdit_parcela))

        self.lineEdit_refcat.returnPressed.connect(self.busqueda)
        self.lineEdit_poligono.returnPressed.connect(self.busqueda)
        self.lineEdit_parcela.returnPressed.connect(self.busqueda)

        self.tableWidget.clicked.connect(self.genera_entidad)
        self.pushButton_clean.clicked.connect(self.__reset)
        self.pushButton_zoom.clicked.connect(self.zoom)

    def __reset(self):
        self.lineEdit_refcat.clear()
        self.lineEdit_poligono.clear()
        self.lineEdit_parcela.clear()
        self.tableWidget.clearSelection()
        self.tableWidget.clearContents()
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.pushButton_zoom.setEnabled(False)

    def datos2list_urbano(self, datos):
        """
        Convertir respuesta en lista de datos
        """
        data_dict = json.loads(datos)
        print(data_dict)
        lista_datos = []
        for dat in data_dict:
            lista_datos.append((dat["manzana"], dat["parcela"], dat["hoja"], dat["refCat"], str(dat["wgs84X"]), str(dat["wgs84Y"])))
        return lista_datos

    def datos2list_rustico(self, datos):
        """
        Convertir respuesta en lista de datos
        """
        data_dict = json.loads(datos)
        lista_datos = []
        for dat in data_dict:
            refcat = str(dat["refCat"])
            if refcat[-8:].isdigit():
                lista_datos.append((str(dat["poligono"]), str(dat["parcela"]), dat["refCat"], str(dat["wgs84X"]), str(dat["wgs84Y"])))
        return lista_datos

    def busqueda(self):
        """
        Realiza la busqueda por catastro o utilizando la referencia catatrasl (14 caracteres)
        o haciendo referencia al número de polígono y Parcela
        @param text:
        @return:
        """
        texto_refcat = self.lineEdit_refcat.text()
        texto_poligono = self.lineEdit_poligono.text()
        texto_parcela = self.lineEdit_parcela.text()
        rustico = False

        if texto_refcat not in (None, ''):
            if len(texto_refcat) >= 14:
                url = BUSCAR_CATASTRO_URBANO_REFCAT + f'{texto_refcat}'
                status_code, value = request_service_gis_caceres(url=url)
                if status_code != 0:
                    url = BUSCAR_CATASTRO_RUSTICO_REFCAT + f'{texto_refcat}'
                    rustico = True
            elif 7 <= len(texto_refcat) < 14:
                manzana = texto_refcat[:5]
                parcela = texto_refcat[5:7]
                url = BUSCAR_CATASTRO_URBANO_MANZANA + f'{manzana}/' + f'{parcela}'
                status_code, value = request_service_gis_caceres(url=url)
                if status_code != 0:
                    url = BUSCAR_CATASTRO_RUSTICO_REFCAT + f'{texto_refcat}'
                    rustico = True
            else:
                warning_message(header='Aviso', message='La referencia catastral no es correcta')
                return None

        elif texto_poligono not in (None, '') and texto_parcela not in (None, ''):
            url = BUSCAR_CATASTRO_RUSTICA + f'{texto_poligono}/{texto_parcela}'
            rustico = True
        elif texto_poligono in (None, '') and texto_parcela not in (None, ''):
            warning_message(header='Aviso', message='Introduzca la referencia del polígono')
            return None
        elif texto_poligono not in (None, '') and texto_parcela in (None, ''):
            warning_message(header='Aviso', message='Introduzca la referencia de la parcela')
            return None
        else:
            warning_message(header='Aviso', message='Introduzca un texto búsqueda')
            return None

        response, value = request_service_gis_caceres(url=url)

        if response == 0 and rustico == False:
            datos = self.datos2list_urbano(datos=value)
            add_items_to_table(_data=datos, _table=self.tableWidget, _header=CABECERA_TABLA_CATASTRO_URBANO,
                               _size_columns=ANCHO_COLUMNAS_CATASTRO_URBANO, _tooltips=None, _align=None)
            self.tableWidget.setColumnHidden(4, True)
            self.tableWidget.setColumnHidden(5, True)
        elif response == 0 and rustico == True:
            datos = self.datos2list_rustico(datos=value)
            add_items_to_table(_data=datos, _table=self.tableWidget, _header=CABECERA_TABLA_CATASTRO_RUSTICO,
                               _size_columns=ANCHO_COLUMNAS_CATASTRO_RUSTICO, _tooltips=None, _align=None)
            self.tableWidget.setColumnHidden(3, True)
            self.tableWidget.setColumnHidden(4, True)
        elif response == 1:
            warning_message(header='Aviso', message='No hay coincidencias en la búsqueda')

    def genera_entidad(self):
        column_count = self.tableWidget.columnCount()
        self.resultado = select_columns_table(_table=self.tableWidget, _cols=list(range(column_count)))
        self.pushButton_zoom.setEnabled(True)

    def zoom(self):
        """
        zoom al objeto
        """
        if self.resultado:
            print(self.resultado)
            if len(self.resultado) == 6:
                _, _, _, _, coordenada_x, coordenada_y = self.resultado
            elif len(self.resultado) == 5:
                _, _, _, coordenada_x, coordenada_y = self.resultado

            coordenada_x = float(coordenada_x)
            coordenada_y = float(coordenada_y)

            project_crs = QgsProject.instance().crs().authid()
            crs_actual = str(project_crs).split(':')[-1]
            if crs_actual != '4326':
                coordenada_x, coordenada_y = transform_coordinates(x=coordenada_x, y=coordenada_y,
                                                                   source_crs='EPSG:4326', dest_crs=project_crs)
            zoom_extension(coord_x_pto=coordenada_x, coord_y_pto=coordenada_y, extension=50)
        else:
            warning_message(header='Aviso', message='No hay camino seleccionado')

    def run(self):
        """
        Run
        """
        self.show()
        self.exec_()
