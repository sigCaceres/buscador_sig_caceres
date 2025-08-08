# -*- coding: utf-8 -*-
__author__ = "SIG Caceres"
__copyright__ = "Copyright 2024, SIG Caceres"
__credits__ = ["SIG Caceres"]
__version__ = "1.1.0"
__maintainer__ = "SIG Cáceres"
__email__ = "https://sig.caceres.es/"
__status__ = "Production"

import os
import qgis
from PyQt5.QtWidgets import QCompleter
from qgis.PyQt import uic, QtWidgets
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import Qt
import json
from qgis.core import *
from qgis.gui import QgsVertexMarker
from scr.funciones_util import request_service_gis_caceres, add_items_to_table, warning_message, \
    select_row_table, zoom_extension, transform_coordinates, toggle_line_edits
from scr.servicios_web import BUSCAR_CALLE_NOMBRE, BUSCAR_CALLE_CODIGO, BUSCAR_CALLE_NUMPOl_NOMBRE, \
    BUSCAR_CALLE_NUMPOl_CODIGO, BUSCAR_NUMEROS_POLICIA_CODIGO_VIA_TODOS, \
    POSICION_CODIGO_VIA, POSICION_NUMPOL_CODIGO_VIA

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sig_caceres_busqueda_calles.ui'))

CABECERA_TABLA_CALLES = ("TIPO VÍA", "NOMBRE", "NÚCLEO", "CÓDIGO")
ANCHO_COLUMNAS_CALLES = (55, 325, 270, 53)


class SigCaceresBusquedaCalle(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent_obj, parent=None):
        super(SigCaceresBusquedaCalle, self).__init__(parent)
        self.setupUi(self)
        self.canvas = qgis.utils.iface.mapCanvas()
        self.marcador_actual = None
        self.__reset()
        self.parent_obj = parent_obj
        self.codigo_via = None
        self.num_pol = None

        # Conexiones
        self.lineEdit_via.textChanged.connect(
            lambda: toggle_line_edits(line_edit_1=self.lineEdit_via, line_edit_2=self.lineEdit_codigo))
        self.lineEdit_codigo.textChanged.connect(
            lambda: toggle_line_edits(line_edit_1=self.lineEdit_via, line_edit_2=self.lineEdit_codigo))
        self.lineEdit_via.returnPressed.connect(self.busqueda)
        self.lineEdit_codigo.returnPressed.connect(self.busqueda)
        self.tableWidget.clicked.connect(self.get_num_policia)
        self.pushButton_clean.clicked.connect(self.__reset)
        self.pushButton_zoom.clicked.connect(self.zoom)
        self.pushButton_clear_marker.clicked.connect(self.__limpiar_marcadores_canvas)  # ← AÑADIDO

    def __reset(self):
        self.__limpiar_marcadores_canvas()
        self.lineEdit_via.clear()
        self.lineEdit_codigo.clear()
        self.comboBox_num_pol.clear()
        self.comboBox_num_pol.setEnabled(False)
        self.tableWidget.clearSelection()
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(len(CABECERA_TABLA_CALLES))
        self.tableWidget.setHorizontalHeaderLabels(CABECERA_TABLA_CALLES)

        header = self.tableWidget.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Fixed)
        for i, ancho in enumerate(ANCHO_COLUMNAS_CALLES):
            self.tableWidget.setColumnWidth(i, ancho)

        self.tableWidget.setMinimumHeight(30 * 10 + self.tableWidget.horizontalHeader().height() + 2)
        total_width = sum(ANCHO_COLUMNAS_CALLES) + self.tableWidget.verticalHeader().width()
        self.tableWidget.setMinimumWidth(total_width + 4)
        self.tableWidget.setMaximumWidth(total_width + 4)

        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.pushButton_zoom.setEnabled(False)

    def __limpiar_marcadores_canvas(self):
        if self.marcador_actual:
            self.canvas.scene().removeItem(self.marcador_actual)
            self.marcador_actual = None
        self.canvas.refresh()

    def datos2list(self, datos):
        data_dict = json.loads(datos)
        lista_datos = []
        for dat in data_dict:
            tipo_via = dat.get("tipovia", "") or dat.get("tipoVia", "")
            nombre = dat.get("nombrevia", "") or dat.get("nombreVia", "")
            nucleo = dat.get("nucleo", "")
            codigo = str(dat.get("codigovia", ""))
            lista_datos.append((tipo_via, nombre, nucleo, codigo))
        return lista_datos

    def busqueda(self):
        self.__limpiar_marcadores_canvas()
        texto_nombre = self.lineEdit_via.text().strip()
        texto_codigo = self.lineEdit_codigo.text().strip()

        if texto_nombre:
            url = BUSCAR_CALLE_NOMBRE + texto_nombre
        elif texto_codigo:
            url = BUSCAR_CALLE_CODIGO + texto_codigo
        else:
            warning_message(header='Aviso', message='Debe introducir un nombre o código de vía')
            return

        response, value = request_service_gis_caceres(url=url)

        if response == 0 and value:
            datos = self.datos2list(datos=value)
            self.tableWidget.setRowCount(0)
            for fila, fila_datos in enumerate(datos):
                self.tableWidget.insertRow(fila)
                for columna, valor in enumerate(fila_datos):
                    item = QtWidgets.QTableWidgetItem(valor)
                    self.tableWidget.setItem(fila, columna, item)
        else:
            warning_message(header='Aviso', message='No hay coincidencias en la búsqueda')

    def get_num_policia(self):
        self.comboBox_num_pol.clear()
        self.comboBox_num_pol.setEnabled(True)
        self.codigo_via = select_row_table(_table=self.tableWidget, _col=3)
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
        if self.codigo_via:
            num_pol = self.comboBox_num_pol.currentText()
            if num_pol:
                coordenada_x = self.num_pol[num_pol]['x']
                coordenada_y = self.num_pol[num_pol]['y']
            else:
                url = POSICION_CODIGO_VIA + f'{self.codigo_via}'
                response, value = request_service_gis_caceres(url=url)
                data_dict = json.loads(value) if response == 0 else []
                if not data_dict or 'centroWgs84X' not in data_dict[0]:
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
                    coordenada_x = data_dict[0]['centroWgs84X']
                    coordenada_y = data_dict[0]['centroWgs84Y']

            project_crs = QgsProject.instance().crs().authid()
            crs_actual = str(project_crs).split(':')[-1]
            if crs_actual != '4326':
                coordenada_x, coordenada_y = transform_coordinates(
                    x=coordenada_x, y=coordenada_y, source_crs='EPSG:4326', dest_crs=project_crs
                )

            self.__limpiar_marcadores_canvas()
            self.marcador_actual = QgsVertexMarker(self.canvas)
            self.marcador_actual.setCenter(QgsPointXY(coordenada_x, coordenada_y))
            self.marcador_actual.setColor(Qt.green)
            self.marcador_actual.setIconSize(12)
            self.marcador_actual.setIconType(QgsVertexMarker.ICON_CROSS)
            self.marcador_actual.setPenWidth(3)
            self.canvas.setCenter(QgsPointXY(coordenada_x, coordenada_y))
            self.canvas.zoomScale(1000)
        else:
            warning_message(header='Aviso', message='No hay calle seleccionada')

    def run(self):
        self.show()
        self.exec_()
