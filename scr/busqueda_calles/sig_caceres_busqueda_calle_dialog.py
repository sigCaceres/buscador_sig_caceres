# -*- coding: utf-8 -*-
"""
Modulo de busqueda por calle

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
    select_row_table, zoom_extension, transform_coordinates, toggle_line_edits
from scr.servicios_web import BUSCAR_CALLE_NOMBRE, BUSCAR_CALLE_CODIGO, BUSCAR_CALLE_NUMPOl_NOMBRE, \
    BUSCAR_CALLE_NUMPOl_CODIGO, BUSCAR_NUMEROS_POLICIA_CODIGO_VIA_TODOS,  \
    POSICION_CODIGO_VIA, POSICION_NUMPOL_CODIGO_VIA
from scr.mensajes import *

from qgis.utils import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sig_caceres_busqueda_calles.ui'))

CABECERA_TABLA_CALLES = ("NOMBRE", "CÓDIGO")
ANCHO_COLUMNAS_CALLES = (350, 100)


class SigCaceresBusquedaCalle(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent_obj, parent=None):
        """Constructor."""
        super(SigCaceresBusquedaCalle, self).__init__(parent)

        self.setupUi(self)
        self.canvas = qgis.utils.iface.mapCanvas()
        self.__reset()

        self.parent_obj = parent_obj
        self.codigo_via = None
        self.num_pol = None

        self.lineEdit_via.textChanged.connect(
            lambda: toggle_line_edits(line_edit_1=self.lineEdit_via, line_edit_2=self.lineEdit_codigo))
        self.lineEdit_codigo.textChanged.connect(
            lambda: toggle_line_edits(line_edit_1=self.lineEdit_via, line_edit_2=self.lineEdit_codigo))
        self.lineEdit_via.returnPressed.connect(self.busqueda)
        self.lineEdit_codigo.returnPressed.connect(self.busqueda)
        self.tableWidget.clicked.connect(self.get_num_policia)
        self.pushButton_clean.clicked.connect(self.__reset)
        self.pushButton_zoom.clicked.connect(self.zoom)

    def __reset(self):
        self.lineEdit_via.clear()
        self.lineEdit_codigo.clear()
        self.comboBox_num_pol.clear()
        self.comboBox_num_pol.setEnabled(False)
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
            if "nombreVia" in dat:
                lista_datos.append((dat["nombreVia"], str(dat["codigovia"])))
            else:
                lista_datos.append((dat["nombrevia"], str(dat["codigovia"])))
        return lista_datos

    def busqueda(self):
        """
        Realiza la busqueda de una calle,por nombre o codigo de via
        @param text:
        @return:
        """
        texto_nombre = self.lineEdit_via.text()
        texto_codigo = self.lineEdit_codigo.text()
        response, value = 1, []

        if texto_nombre not in (None, '') and texto_codigo in (None, ''):
            url_nombre = BUSCAR_CALLE_NOMBRE + f'{texto_nombre}'
            url_numpol = BUSCAR_CALLE_NUMPOl_NOMBRE + f'{texto_nombre}'

            response_nombre, value_nombre = request_service_gis_caceres(url=url_nombre)
            response_numpol, value_numpol = request_service_gis_caceres(url=url_numpol)

            if response_numpol == 0:
                try:
                    numpol_data = json.loads(value_numpol)
                    unique_numpol = {}
                    for numpol in numpol_data:
                        key = (numpol.get("nombreVia"), numpol.get("codigovia"))
                        if key not in unique_numpol:
                            unique_numpol[key] = numpol
                    value_numpol = json.dumps(list(unique_numpol.values()))
                except Exception as e:
                    print(f"Error procesando value_numpol: {e}")
                    value_numpol = "[]"

            if response_nombre == 0 and response_numpol == 0:
                try:
                    combined_data = []
                    if response_nombre == 0:
                        combined_data.extend(json.loads(value_nombre))
                    if response_numpol == 0:
                        combined_data.extend(json.loads(value_numpol))

                    unique_combined = {}
                    for record in combined_data:
                        nombre = record.get("nombrevia") or record.get("nombreVia")
                        codigo = record.get("codigovia")
                        key = (nombre, codigo)
                        if key not in unique_combined:
                            unique_combined[key] = record
                    response = 0
                    value = json.dumps(list(unique_combined.values()))
                except Exception as e:
                    print(f"Error procesando combinación de datos: {e}")
                    response = 1
                    value = "[]"
            elif response_nombre == 0:
                response = 0
                value = value_nombre
            elif response_numpol == 0:
                response = 0
                value = value_numpol

        elif texto_codigo not in (None, '') and texto_nombre in (None, ''):
            url_codigo = BUSCAR_CALLE_CODIGO + f'{texto_codigo}'
            url_numpol = BUSCAR_CALLE_NUMPOl_CODIGO + f'{texto_codigo}'

            response_codigo, value_codigo = request_service_gis_caceres(url=url_codigo)
            response_numpol, value_numpol = request_service_gis_caceres(url=url_numpol)

            if response_numpol == 0:
                try:
                    numpol_data = json.loads(value_numpol)
                    unique_numpol = {}
                    for numpol in numpol_data:
                        key = (numpol.get("nombreVia"), numpol.get("codigovia"))
                        if key not in unique_numpol:
                            unique_numpol[key] = numpol
                    value_numpol = json.dumps(list(unique_numpol.values()))
                except Exception as e:
                    print(f"Error procesando value_numpol: {e}")
                    value_numpol = "[]"

            if response_codigo == 0 and response_numpol == 0:
                try:
                    combined_data = []
                    if response_codigo == 0:
                        combined_data.extend(json.loads(value_codigo))
                    if response_numpol == 0:
                        combined_data.extend(json.loads(value_numpol))

                    unique_combined = {}
                    for record in combined_data:
                        nombre = record.get("nombrevia") or record.get("nombreVia")
                        codigo = record.get("codigovia")
                        key = (nombre, codigo)
                        if key not in unique_combined:
                            unique_combined[key] = record
                    response = 0
                    value = json.dumps(list(unique_combined.values()))
                except Exception as e:
                    print(f"Error procesando combinación de datos: {e}")
                    response = 1
                    value = "[]"
            elif response_codigo == 0:
                response = 0
                value = value_codigo
            elif response_numpol == 0:
                response = 0
                value = value_numpol

        else:
            warning_message(header='Aviso', message='Introduzca un texto búsqueda')
            return None

        if response == 0:
            datos = self.datos2list(datos=value)
            add_items_to_table(_data=datos, _table=self.tableWidget, _header=CABECERA_TABLA_CALLES,
                               _size_columns=ANCHO_COLUMNAS_CALLES, _tooltips=None, _align=None)
        elif response == 1:
            warning_message(header='Aviso', message='No hay coincidencias en la búsqueda')

    def get_num_policia(self):
        """
        Obtiene los num de policia de la calle y los carga en el combo
        """
        self.comboBox_num_pol.clear()
        self.comboBox_num_pol.setEnabled(True)

        self.codigo_via = select_row_table(_table=self.tableWidget, _col=1)
        url = BUSCAR_NUMEROS_POLICIA_CODIGO_VIA_TODOS + f'{self.codigo_via}'
        response, value = request_service_gis_caceres(url=url)
        data_dict = json.loads(value)
        self.comboBox_num_pol.addItem('')
        self.num_pol = {}
        for dat in data_dict:
            if response == 0:
                self.num_pol[str(dat["numpol"])] = {'x': dat["wgs84X"], 'y': dat["wgs84Y"]}
                self.comboBox_num_pol.addItem(str(dat["numpol"]))
        self.pushButton_zoom.setEnabled(True)

    def zoom(self):
        """
        zoom al objeto
        """
        if self.codigo_via:
            num_pol = self.comboBox_num_pol.currentText()
            if num_pol not in ('', None):
                coordenada_x = self.num_pol[num_pol]['x']
                coordenada_y = self.num_pol[num_pol]['y']
            else:

                url = POSICION_CODIGO_VIA + f'{self.codigo_via}'
                coor_x = 'centroWgs84X'
                coor_y = 'centroWgs84Y'

                response, value = request_service_gis_caceres(url=url)
                data_dict = []
                if response == 0:
                    try:
                        data_dict = json.loads(value)
                    except Exception as e:
                        warning_message(header='Error', message=f'Error procesando datos: {e}')
                        return

                if not data_dict or coor_x not in data_dict[0] or coor_y not in data_dict[0]:

                    url_numpol = POSICION_NUMPOL_CODIGO_VIA + f'{self.codigo_via}'
                    response_numpol, value_numpol = request_service_gis_caceres(url=url_numpol)
                    if response_numpol == 0:
                        numpol_data = json.loads(value_numpol)
                        if numpol_data:
                            coordenada_x = numpol_data[0]['wgs84X']
                            coordenada_y = numpol_data[0]['wgs84Y']
                        else:
                            warning_message(header='Error', message='No se encontraron coordenadas en numpol')
                            return
                    else:
                        warning_message(header='Error', message='No se pudo obtener datos de numpol')
                        return
                else:
                    coordenada_x = data_dict[0][coor_x]
                    coordenada_y = data_dict[0][coor_y]

            project_crs = QgsProject.instance().crs().authid()
            crs_actual = str(project_crs).split(':')[-1]
            if crs_actual != '4326':
                coordenada_x, coordenada_y = transform_coordinates(x=coordenada_x, y=coordenada_y,
                                                                   source_crs='EPSG:4326', dest_crs=project_crs)
            zoom_extension(coord_x_pto=coordenada_x, coord_y_pto=coordenada_y, extension=50)
        else:
            warning_message(header='Aviso', message='No hay calle seleccionada')

    def run(self):
        """
        Run
        """
        self.show()
        self.exec_()
