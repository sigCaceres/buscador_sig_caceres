# -*- coding: utf-8 -*-
"""
Modulo de funciones generales SIG CACERES

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
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtCore import Qt as pyQT
from PyQt5.QtWidgets import QCompleter, QMessageBox
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets, QtCore

from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.utils import *
from qgis.gui import QgsVertexMarker
from PyQt5.QtGui import QColor
import requests

from qgis.core import *  # No borrar


def warning_message(header, message):
    """
    warning message
    @param header:
    @param message:
    @return:
    """

    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle(header)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)

    # Set flag WindowStaysOnTopHint
    msg_box.setWindowFlag(pyQT.WindowStaysOnTopHint)
    msg_box.exec_()

def request_service_gis_caceres( url):
    """
    Peticiones al servicio de búsquedas de Cáceres
    """

    headers = {
        'accept': 'text/json'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.text
        # print("Respuesta:")
        # print(data)
        return 0,data
    elif response.status_code == 404:
        return 1,response.text
    else:
        # print(f"Error en la solicitud: {response.status_code}")
        return 2,response.status_code



def add_items_to_table(_data, _table, _header, _size_columns, _tooltips=None, _align=None):
    """
    Generate table form a list
    @param _header:
    @param _table:
    @param _data:
    @param_size_columns:
    @return:none
    """
    add_tooltips = False
    if _tooltips and len(_data) == len(_tooltips):
        add_tooltips = True
    _table.setColumnCount(len(_header))
    _table.setHorizontalHeaderLabels(_header)
    _table.setRowCount(len(_data))
    _table.setSortingEnabled(True)
    for n, i in enumerate(_size_columns):
        _table.setColumnWidth(n, i)
    for row, row_data in enumerate(_data):
        for col, item_data in enumerate(row_data):
            item = None
            try:
                _ = float(item_data)
                item = NumericTableWidgetItem(item_data)

                if _align == 'No':
                    item.setTextAlignment(pyQT.AlignLeft | pyQT.AlignVCenter)
                else:
                    item.setTextAlignment(pyQT.AlignRight | pyQT.AlignVCenter)
            except Exception:
                item = QTableWidgetItem(item_data)
                item.setTextAlignment(pyQT.AlignLeft | pyQT.AlignVCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            if add_tooltips:
                item.setToolTip(_tooltips[row])

            _table.setItem(row, col, item)

def select_row_table(_table, _col = None):
    """
    Retorna el valor de una columna de una tabla seleccionando una fila
    @return: value
    """
    whole_row = _table.currentRow()
    col = 0
    if _col:
        col = _col
    first_column_in_row = _table.item(whole_row, col)
    if first_column_in_row is not None:
        _k = first_column_in_row.text()
        return _k

def select_columns_table(_table, _cols=None):
    """
    Retorna los valores de las columnas especificadas de una fila seleccionada
    @param _cols: lista de índices de columna (por defecto None, lo que devuelve la columna 0)
    @return: list de valores
    """
    whole_row = _table.currentRow()
    if whole_row == -1:  # Verifica si hay una fila seleccionada
        return []

    if _cols is None:
        _cols = [0]  # Si no se especifican columnas, retorna solo la columna 0

    values = []
    for col in _cols:
        item = _table.item(whole_row, col)
        if item is not None:
            values.append(item.text())

    return values

def eliminar_cruces_busqueda():
    """
    Elimina las marcas de búsquedas anteriores si las hay
    @return:
    """
    canvas = iface.mapCanvas()
    vertex_items = [i for i in canvas.scene().items() if isinstance(i, QgsVertexMarker)]

    if vertex_items:
        # Usar QTimer para eliminar en el siguiente ciclo de eventos
        QTimer.singleShot(0, lambda: remove_items(canvas, vertex_items))

def remove_items(canvas, vertex_items):
    for ver in vertex_items:
        try:
            if ver.scene() is not None and ver.isVisible():
                canvas.scene().removeItem(ver)
        except Exception as e:
            print(f"Error al eliminar el elemento: {e}")

def zoom_extension(coord_x_pto, coord_y_pto, extension):
    """
    Funcion que realiza un zoom a un punto pasado como parametro
    @param coord_x_pto:
    @param coord_y_pto:
    @param extension: extension del zoom
    @return: nada
    """

    canvas = iface.mapCanvas()
    # eliminar las marcar anteriores de zoom

    eliminar_cruces_busqueda()

    # convertir extension m a grados en caso de proyeccion geografia
    crs = QgsProject.instance().crs()
    if crs.isGeographic():
        scale = extension / 111111
    else:
        scale = extension

    rect = QgsRectangle(float(coord_x_pto) - scale, float(coord_y_pto) - scale,
                        float(coord_x_pto) + scale,
                        float(coord_y_pto) + scale)
    canvas.setExtent(rect)

    # dibujar una cruz en la busqueda por coordenadas
    m = QgsVertexMarker(canvas)
    m.setCenter(QgsPointXY(coord_x_pto, coord_y_pto))
    m.setColor(QColor(0, 255, 0))
    m.setIconSize(10)
    m.setIconType(QgsVertexMarker.ICON_X)  # or ICON_CROSS, ICON_X,ICON_BOX
    m.setPenWidth(3)
    canvas.refresh()


def transform_coordenadas(epsg_source, coord_x, coord_y):
    """"
    Función que transforma las coordenadas de un punto X e Y
    param:
    epsg_source: EPSG de los datos origen
    coord_x: Coordenadas X del punto
    coord_y: Coordenadas Y del punto
    """
    point = QgsGeometry.fromPointXY(QgsPointXY(coord_x, coord_y))
    sourceCrs = QgsCoordinateReferenceSystem(epsg_source)
    tr = QgsCoordinateTransform(sourceCrs, QgsProject.instance().crs(), QgsProject.instance())
    point.transform(tr)
    point.asPoint()
    return point.get().x(), point.get().y()


def transform_coordinates(x, y, source_crs, dest_crs):
    """
    Transforma coordenadas de un sistema de referencia a otro.

    :param x: Coordenada X (longitud o este).
    :param y: Coordenada Y (latitud o norte).
    :param source_crs: EPSG o código de proyección del sistema de referencia de origen.
    :param dest_crs: EPSG o código de proyección del sistema de referencia de destino.
    :return: Tuple (x_transformed, y_transformed) con las coordenadas transformadas.
    """

    crs_source = QgsCoordinateReferenceSystem(source_crs)
    crs_dest = QgsCoordinateReferenceSystem(dest_crs)
    transform = QgsCoordinateTransform(crs_source, crs_dest, QgsProject.instance())
    point_source = QgsPointXY(x, y)
    point_dest = transform.transform(point_source)

    return point_dest.x(), point_dest.y()


def toggle_line_edits(line_edit_1,line_edit_2):
    """
    Alternar ediciones de línea
    @param line_edit_1:
    @param line_edit_2:
    """
    if line_edit_1.text():
        line_edit_2.setDisabled(True)
    else:
        line_edit_2.setDisabled(False)

    if line_edit_2.text():
        line_edit_1.setDisabled(True)
    else:
        line_edit_1.setDisabled(False)

def toggle_line_edits_multiple(line_edit_1,line_edit_2,line_edit_3):
    """
    Alternar ediciones de línea
    @param line_edit_1:
    @param line_edit_2:
    @param line_edit_3:
    """
    if line_edit_1.text():
        line_edit_2.setDisabled(True)
        line_edit_3.setDisabled(True)
    else:
        line_edit_2.setDisabled(False)
        line_edit_3.setDisabled(False)

    if line_edit_2.text() or line_edit_3.text():
        line_edit_1.setDisabled(True)
    else:
        line_edit_1.setDisabled(False)
