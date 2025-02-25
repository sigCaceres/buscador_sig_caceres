# -*- coding: utf-8 -*-
"""
Aplicación QGIS Búsqueda SIG de Cáceres
"""
__author__ = "SIG Caceres"
__copyright__ = "Copyright 2024, SIG Caceres"
__credits__ = ["SIG Caceres"]

__version__ = "1.1.0"
__maintainer__ = "SIG Cáceres"
__email__ = "https://sig.caceres.es/"
__status__ = "Production"

from PyQt5.QtWidgets import QMenu
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from scr.busqueda_barrios.sig_caceres_busqueda_barrio_dialog import SigCaceresBusquedaBarrio
from scr.busqueda_calles.sig_caceres_busqueda_calle_dialog import SigCaceresBusquedaCalle
from scr.busqueda_caminos.sig_caceres_busqueda_camino_dialog import SigCaceresBusquedaCamino
from scr.busqueda_carreteras.sig_caceres_busqueda_carretera_dialog import \
    SigCaceresBusquedaCarretera
from scr.busqueda_toponimia.sig_caceres_busqueda_toponimia_dialog import \
    SigCaceresBusquedaToponimia
from scr.busqueda_coordenadas.sig_caceres_busqueda_coordenadas_25829 import \
    SigCaceresBusquedaCoordenadas25829
from scr.busqueda_coordenadas.sig_caceres_busqueda_coordenadas_4326 import \
    SigCaceresBusquedaCoordenadas4326
from scr.busqueda_coordenadas.sig_caceres_busqueda_gradosminutosysegundos import \
    SigCaceresBusquedaGradosMinutosYSegundos
from scr.busqueda_catastro.sig_caceres_busqueda_catastro_dialog import SigCaceresBusquedaCatastro

# Initialize Qt resources from file resources.py
# Import the code for the dialog
from .buscador_sig_caceres_dialog import buscador_sig_caceresDialog
import os.path


class buscador_sig_caceres:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'buscador_sig_caceres_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Buscador Sig Caceres')

        self.first_start = None

        # incializar variables
        self.dlg = None
        self.menu_ppal = None
        self.buscador_barrio_dialog = None
        self.buscador_calle_dialog = None
        self.buscador_camino_dialog = None
        self.buscador_coordenadas25829_dialog = None
        self.buscador_coordenadas4326_dialog = None
        self.buscador_coordenadas_gradosminutossegundos_dialog = None
        self.buscador_toponimia_dialog = None
        self.buscador_carretera_dialog = None
        self.buscador_catastro_dialog = None

        self.toolbar = self.iface.addToolBar(u'BuscadorSigCaceres')
        self.toolbar.setObjectName(u'BuscadorSigCaceres')

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('buscador_sig_caceres', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.menu_ppal.addAction(
                action)
        self.actions.append(action)

        return action

    def creacion_submenus(self, dict_menu, _submenu):
        """
        Crear submenus a partir de un diccionario de datos
        @param dict_menu:
        @param _submenu:
        @return: objeto submenu
        """

        for k, v in zip(dict_menu.keys(), dict_menu.values()):
            if v['visible'] == 'si':
                menu_funcion = QAction(QIcon(v['icon']), v['name'], self.iface.mainWindow())
                menu_funcion.setObjectName(v['name'])
                menu_funcion.setWhatsThis(v['name'])
                menu_funcion.setStatusTip(v['name'])
                menu_funcion.triggered.connect(v['funcion'])
                _submenu.addAction(menu_funcion)
        return _submenu

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # menu ppal
        self.menu_ppal = self.iface.mainWindow().findChild(QMenu, '&Buscador SIG Cáceres')

        # if not create it
        if not self.menu_ppal:
            self.menu_ppal = QMenu(self.iface.mainWindow())
            self.menu_ppal.setObjectName('&Buscador SIG Cáceres')
            self.menu_ppal.setTitle('&Buscador SIG Cáceres')

        dict_menu = {'callejero': {}, 'coordenadas': {}, 'referencia_catastral': {}}

        # _DATOS
        # _________________________________________________________________________________________________________

        # CREACIÓN DE SUBMENUS
        # _________________________________________________________________________________________________

        # COORDENADAS

        dict_menu['coordenadas']['epsg_25829'] = {'icon': '',
                                                  'name': 'EPSG 25829',
                                                  'funcion': self.run_busqueda_coordenadas25829,
                                                  'visible': 'si'}

        dict_menu['coordenadas']['epsg_4326'] = {'icon': '',
                                                 'name': 'EPSG 4326',
                                                 'funcion': self.run_busqueda_coordenadas4326,
                                                 'visible': 'si'}

        dict_menu['coordenadas']['grados_min_seg'] = {'icon': '',
                                                      'name': 'Grados minutos y segundos',
                                                      'funcion': self.run_busqueda_coordenadas_gradosminutossegundos,
                                                      'visible': 'si'}
        #
        # # REFERENCIA CATASTRAL
        #
        # dict_menu['referencia_catastral']['catastro_urbano'] = {'icon': '',
        #                                                         'name': 'Catastro Urbana',
        #                                                         'funcion': self.run_busqueda_catastrourbano,
        #                                                         'visible': 'si'}
        #
        # dict_menu['referencia_catastral']['catastro_rustico'] = {'icon': '',
        #                                                          'name': 'Catastro Rústica',
        #                                                          'funcion': self.run_busqueda_catastrorustico,
        #                                                          'visible': 'si'}

        # CREACIÓN DE LOS SUBMENUS
        # ____________________________________________________________________________________3

        # #################### Menus simples
        # Calles
        calles_action = QAction(QIcon(''), "Calles", self.iface.mainWindow())
        calles_action.triggered.connect(self.run_busqueda_calles)
        self.menu_ppal.addAction(calles_action)

        # Catastro
        catastro_action = QAction(QIcon(''), "Catastro", self.iface.mainWindow())
        catastro_action.triggered.connect(self.run_busqueda_catastro)
        self.menu_ppal.addAction(catastro_action)

        # Toponimia
        toponimia_action = QAction(QIcon(''), "Toponimia", self.iface.mainWindow())
        toponimia_action.triggered.connect(self.run_busqueda_toponimia)
        self.menu_ppal.addAction(toponimia_action)

        # Carreteras
        calles_action = QAction(QIcon(''), "Carreteras", self.iface.mainWindow())
        calles_action.triggered.connect(self.run_busqueda_carreteras)
        self.menu_ppal.addAction(calles_action)

        # Caminos
        caminos_action = QAction(QIcon(''), "Caminos", self.iface.mainWindow())
        caminos_action.triggered.connect(self.run_busqueda_caminos)
        self.menu_ppal.addAction(caminos_action)

        # Barrios
        barrios_action = QAction(QIcon(''), "Barrios", self.iface.mainWindow())
        barrios_action.triggered.connect(self.run_busqueda_barrios)
        self.menu_ppal.addAction(barrios_action)

        self.menu_ppal.addSeparator()


        # #################### Menus anidados

        submenu_coordenadas = self.menu_ppal.addMenu(QIcon(''), "Coordenadas")
        self.creacion_submenus(dict_menu=dict_menu['coordenadas'], _submenu=submenu_coordenadas)

        menuBar = self.iface.mainWindow().menuBar()
        menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.menu_ppal)

        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.menu_ppal.clear()
        self.menu_ppal.deleteLater()

    def run_busqueda_barrios(self):
        """
        Funcion busqueda por barrio
        @return: none
        """
        if not self.buscador_barrio_dialog:
            self.buscador_barrio_dialog = SigCaceresBusquedaBarrio(self)
            self.buscador_barrio_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.buscador_barrio_dialog.rejected.connect(self.cerrar_barrios)
            self.buscador_barrio_dialog.run()
        else:
            if self.buscador_barrio_dialog.windowState() == Qt.WindowMinimized:
                self.buscador_barrio_dialog.setWindowState(Qt.WindowNoState)
            self.buscador_barrio_dialog.show()
            self.buscador_barrio_dialog.raise_()
            self.buscador_barrio_dialog.activateWindow()

    def cerrar_barrios(self):
        if self.buscador_barrio_dialog:
            self.buscador_barrio_dialog.close()
        self.buscador_barrio_dialog = None

    def run_busqueda_calles(self):
        """
        Funcion busqueda por calle
        @return: none
        """
        if not self.buscador_calle_dialog:
            self.buscador_calle_dialog = SigCaceresBusquedaCalle(self)
            self.buscador_calle_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.buscador_calle_dialog.rejected.connect(self.cerrar_calle)
            self.buscador_calle_dialog.run()
        else:
            if self.buscador_calle_dialog.windowState() == Qt.WindowMinimized:
                self.buscador_calle_dialog.setWindowState(Qt.WindowNoState)
            self.buscador_calle_dialog.show()
            self.buscador_calle_dialog.raise_()
            self.buscador_calle_dialog.activateWindow()

    def cerrar_calle(self):
        if self.buscador_calle_dialog:
            self.buscador_calle_dialog.close()
        self.buscador_calle_dialog = None

    def run_busqueda_caminos(self):
        """
        Funcion busqueda por caminos
        @return: none
        """
        if not self.buscador_camino_dialog:
            self.buscador_camino_dialog = SigCaceresBusquedaCamino(self)
            self.buscador_camino_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.buscador_camino_dialog.rejected.connect(self.cerrar_caminos)
            self.buscador_camino_dialog.run()

        else:
            if self.buscador_camino_dialog.windowState() == Qt.WindowMinimized:
                self.buscador_camino_dialog.setWindowState(Qt.WindowNoState)
            self.buscador_camino_dialog.show()
            self.buscador_camino_dialog.raise_()
            self.buscador_camino_dialog.activateWindow()

    def cerrar_caminos(self):
        if self.buscador_camino_dialog:
            self.buscador_camino_dialog.close()
        self.buscador_camino_dialog = None

    def run_busqueda_carreteras(self):
        """
        Funcion busqueda por carretera
        @return: none
        """
        if not self.buscador_carretera_dialog:
            self.buscador_carretera_dialog = SigCaceresBusquedaCarretera(self)
            self.buscador_carretera_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.buscador_carretera_dialog.rejected.connect(self.cerrar_carreteras)
            self.buscador_carretera_dialog.run()
        else:
            if self.buscador_carretera_dialog.windowState() == Qt.WindowMinimized:
                self.buscador_carretera_dialog.setWindowState(Qt.WindowNoState)
            self.buscador_carretera_dialog.show()
            self.buscador_carretera_dialog.raise_()
            self.buscador_carretera_dialog.activateWindow()

    def cerrar_carreteras(self):
        if self.buscador_carretera_dialog:
            self.buscador_carretera_dialog.close()
        self.buscador_carretera_dialog = None

    def run_busqueda_toponimia(self):
        """
        Funcion busqueda por caminos
        @return: none
        """
        if not self.buscador_toponimia_dialog:
            self.buscador_toponimia_dialog = SigCaceresBusquedaToponimia(self)
            self.buscador_toponimia_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.buscador_toponimia_dialog.rejected.connect(self.cerrar_toponimia)
            self.buscador_toponimia_dialog.run()

        else:
            if self.buscador_toponimia_dialog.windowState() == Qt.WindowMinimized:
                self.buscador_toponimia_dialog.setWindowState(Qt.WindowNoState)
            self.buscador_toponimia_dialog.show()
            self.buscador_toponimia_dialog.raise_()
            self.buscador_toponimia_dialog.activateWindow()

    def cerrar_toponimia(self):
        if self.buscador_toponimia_dialog:
            self.buscador_toponimia_dialog.close()
        self.buscador_toponimia_dialog = None

    def run_busqueda_catastro(self):
        """
        Funcion busqueda por caminos
        @return: none
        """
        if not self.buscador_catastro_dialog:
            self.buscador_catastro_dialog = SigCaceresBusquedaCatastro(self)
            self.buscador_catastro_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.buscador_catastro_dialog.rejected.connect(self.cerrar_catastro)
            self.buscador_catastro_dialog.run()

        else:
            if self.buscador_catastro_dialog.windowState() == Qt.WindowMinimized:
                self.buscador_catastro_dialog.setWindowState(Qt.WindowNoState)
            self.buscador_catastro_dialog.show()
            self.buscador_catastro_dialog.raise_()
            self.buscador_catastro_dialog.activateWindow()

    def cerrar_catastro(self):
        if self.buscador_catastro_dialog:
            self.buscador_catastro_dialog.close()
        self.buscador_catastro_dialog = None

    def run_busqueda_coordenadas25829(self):
        """
        Funcion busqueda por coordenadas epsg:25829
        @return:
        """
        if not self.buscador_coordenadas25829_dialog:
            self.buscador_coordenadas25829_dialog = SigCaceresBusquedaCoordenadas25829(self)
            self.buscador_coordenadas25829_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.buscador_coordenadas25829_dialog.rejected.connect(self.cerrar_busqueda_coordenadas25829)
            self.buscador_coordenadas25829_dialog.run()

        else:
            if self.buscador_coordenadas25829_dialog.windowState() == Qt.WindowMinimized:
                self.buscador_coordenadas25829_dialog.setWindowState(Qt.WindowNoState)
            self.buscador_coordenadas25829_dialog.show()
            self.buscador_coordenadas25829_dialog.raise_()
            self.buscador_coordenadas25829_dialog.activateWindow()

    def cerrar_busqueda_coordenadas25829(self):
        if self.buscador_coordenadas25829_dialog:
            self.buscador_coordenadas25829_dialog.close()
        self.buscador_coordenadas25829_dialog = None

    def run_busqueda_coordenadas4326(self):
        """
        Funcion busqueda por coordenadas epsg:4326
        @return:
        """
        if not self.buscador_coordenadas4326_dialog:
            self.buscador_coordenadas4326_dialog = SigCaceresBusquedaCoordenadas4326(self)
            self.buscador_coordenadas4326_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.buscador_coordenadas4326_dialog.rejected.connect(self.cerrar_busqueda_coordenadas4326)
            self.buscador_coordenadas4326_dialog.run()

        else:
            if self.buscador_coordenadas4326_dialog.windowState() == Qt.WindowMinimized:
                self.buscador_coordenadas4326_dialog.setWindowState(Qt.WindowNoState)
            self.buscador_coordenadas4326_dialog.show()
            self.buscador_coordenadas4326_dialog.raise_()
            self.buscador_coordenadas4326_dialog.activateWindow()

    def cerrar_busqueda_coordenadas4326(self):
        if self.buscador_coordenadas4326_dialog:
            self.buscador_coordenadas4326_dialog.close()
        self.buscador_coordenadas4326_dialog = None

    def run_busqueda_coordenadas_gradosminutossegundos(self):
        """
        Funcion busqueda por coordenadas grados, min, seg
        @return:
        """
        if not self.buscador_coordenadas_gradosminutossegundos_dialog:
            self.buscador_coordenadas_gradosminutossegundos_dialog = SigCaceresBusquedaGradosMinutosYSegundos(self)
            self.buscador_coordenadas_gradosminutossegundos_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.buscador_coordenadas_gradosminutossegundos_dialog.rejected.connect(
                self.cerrar_busqueda_coordenadas_gradosminutossegundos_dialog)
            self.buscador_coordenadas_gradosminutossegundos_dialog.run()
        else:
            if self.buscador_coordenadas_gradosminutossegundos_dialog.windowState() == Qt.WindowMinimized:
                self.buscador_coordenadas_gradosminutossegundos_dialog.setWindowState(Qt.WindowNoState)
            self.buscador_coordenadas_gradosminutossegundos_dialog.show()
            self.buscador_coordenadas_gradosminutossegundos_dialog.raise_()
            self.buscador_coordenadas_gradosminutossegundos_dialog.activateWindow()

    def cerrar_busqueda_coordenadas_gradosminutossegundos_dialog(self):
        if self.buscador_coordenadas_gradosminutossegundos_dialog:
            self.buscador_coordenadas_gradosminutossegundos_dialog.close()
        self.buscador_coordenadas_gradosminutossegundos_dialog = None

    def run(self):
        """Run method that performs all the real work"""
        if self.first_start:
            self.first_start = False
            self.dlg = buscador_sig_caceresDialog()
        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass
