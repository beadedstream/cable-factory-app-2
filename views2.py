import os
import re
import math
import random as rand
import QuickSort as quick
# import wizard
# import serialmanager
# import model
# import report
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QEvent, QInputEvent, QKeyEvent, Qt

# import QGraphicsSceneMouseEvent as mB
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QVBoxLayout, QApplication, QLabel,
    QLineEdit, QComboBox, QGridLayout, QGroupBox, QHBoxLayout,
    QMessageBox, QAction, QActionGroup, QFileDialog, QDialog, QMenu, QTextEdit
)

from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QSettings, Qt, QThread

VERSION_NUM = "1.1.4"

WINDOW_WIDTH = 1550
WINDOW_HEIGHT = 900

ABOUT_TEXT = f"""
             PCB assembly test utility. Copyright Beaded Streams, 2019.
             v{VERSION_NUM}
             """


class InvalidMsgType(Exception):
    pass


class MainUtility(QMainWindow):

    def __init__(self):
        super().__init__()

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 12)
        self.config_font = QFont(self.system_font, 12)
        self.config_path_font = QFont(self.system_font, 12)

        self.settings = QSettings()  # to be developed later

        self.config = QAction("Settings", self)
        self.config.setShortcut("Ctrl+E")
        self.config.setStatusTip("Program Settings")
        # self.config.triggered.connect()#(put method)

        self.quit = QAction("Quit", self)
        self.quit.setShortcut("Ctrl+Q")
        self.quit.setStatusTip("Exit Program")
        self.quit.triggered.connect(self.close)

        self.about_tu = QAction("About PCBA Test Utility", self)
        self.about_tu.setShortcut("Ctrl+U")
        self.about_tu.setStatusTip("About Program")
        # self.about_tu.triggered.connect(self.about_program)

        self.aboutqt = QAction("About Qt", self)
        self.aboutqt.setShortcut("Ctrl+I")
        self.aboutqt.setStatusTip("About Qt")
        # self.aboutqt.triggered.connect(self.about_qt)

        # Create menubar
        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu("&File")
        self.file_menu.addAction(self.config)
        self.file_menu.addAction(self.quit)

        self.serial_menu = self.menubar.addMenu("&Serial")
        self.serial_menu.installEventFilter(self)
        self.ports_menu = QMenu("&Ports", self)
        self.serial_menu.addMenu(self.ports_menu)
        # self.ports_menu.aboutToShow.connect(self.populate_ports)
        self.ports_group = QActionGroup(self)
        # self.ports_group.triggered.connect(self.connect_port)

        self.help_menu = self.menubar.addMenu("&Help")
        self.help_menu.addAction(self.about_tu)
        self.help_menu.addAction(self.aboutqt)

        self.pcba_imgs = []
        self.pcba_frame_Dict = {}
        self.pcba_memory = []
        self.pcba_frame_Highlight = []
        self.pcba_hexDict = {}
        self.pcba_hexList = []
        self.hex_lbl_Dict = {}
        self.hex_lbl_list = []
        self.counter = 1
        self.pcba_counter = 1
        self.rowCount = 0
        self.colbCount = 0
        self.sensor_num = [False, 0]
        self.physical_num = 1
        self.lsb = -1
        self.order_dict = {}
        self.final_order = {}


        self.pcba_gridlayout = QGridLayout()
        self.pcba_gridlayout.setVerticalSpacing(100)
        self.pcba_gridlayout.setHorizontalSpacing(200)
        self.pcba_gridlayout.setColumnStretch(7, 1)
        self.pcba_gridlayout.setRowStretch(22, 1)

        self.pcba_groupBox = QGroupBox()
        self.pcba_groupBox.setFlat(True)
        self.pcba_groupBox.setLayout(self.pcba_gridlayout)

        self.initUI()
        # self.center()

    def center(self):
        """Centers the application on the screen the mouse pointer is
                currently on."""
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def resource_path(self, relative_path):
        """Gets the path of the application relative root path to allow us
        to find the logo."""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def initUI(self):
        """"Sets up the main UI."""
        RIGHT_SPACING = 350
        LINE_EDIT_WIDTH = 200

        self.main_central_widget = QWidget()
        # self.main_central_widget.isFullScreen()

        self.gridLayout = QtWidgets.QGridLayout(self.main_central_widget)
        self.gridLayout.setContentsMargins(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.scrollArea = QtWidgets.QScrollArea(self.main_central_widget)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(False)

        self.main_scroll_window = QtWidgets.QWidget()
        self.main_scroll_window.setEnabled(True)
        self.main_scroll_window.setGeometry(QtCore.QRect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

        self.logo_img = QtWidgets.QLabel(self.main_scroll_window)  # self.main_scroll_window)
        self.logo_img.setGeometry(QtCore.QRect(275, 100, 900, 250))
        self.logo_img.setPixmap(QtGui.QPixmap("h_logo.png"))
        self.logo_img.setScaledContents(True)
        self.logo_img.setObjectName("logo_img")

        self.test_btn = QtWidgets.QPushButton(self.main_scroll_window)  # self.main_scroll_window)
        self.test_btn.setGeometry(QtCore.QRect(895, 400, 180, 160))
        self.test_btn.setText("Test")
        self.test_btn.setFont(self.font(20, 75, True))
        self.test_btn.clicked.connect(self.testScreen)

        self.calibrate_btn = QtWidgets.QPushButton(self.main_scroll_window)  # self.main_scroll_window)
        self.calibrate_btn.setGeometry(QtCore.QRect(655, 400, 180, 160))
        self.calibrate_btn.setText("Calibrated")
        self.calibrate_btn.setFont(self.font(20, 75, True))
        self.calibrate_btn.clicked.connect(self.calibrateScreen)

        self.manufacture_btn = QtWidgets.QPushButton(self.main_scroll_window)  # self.main_scroll_window)
        self.manufacture_btn.setGeometry(QtCore.QRect(400, 400, 180, 160))
        self.manufacture_btn.setText("Manufacture")
        self.manufacture_btn.setFont(self.font(20, 75, True))
        self.manufacture_btn.clicked.connect(self.buildScreen)

        self.scrollArea.setWidget(self.main_scroll_window)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setCentralWidget(self.scrollArea)

        # self.central_widget.setLayout(self.gridLayout)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle("BeadedStream Manufacturing App 2")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space and self.counter is not self.sensor_num[1] + 1:
            self.pcbaImgInfo(self.counter, 0)
            self.counter += 1

        if event.key() == Qt.Key_D and self.physical_num is not self.sensor_num[1] + 1:
            self.highlight(self.physical_num, True)

        if event.key() == Qt.Key_A and self.physical_num is not 2:
            self.highlight(self.physical_num, False)

    def buildScreen(self):
        self.build_central_widget = QWidget(self.main_central_widget)

        self.mainBuild_scrollArea = QtWidgets.QScrollArea(self.build_central_widget)
        self.mainBuild_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mainBuild_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mainBuild_scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.mainBuild_scrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.mainBuild_scrollArea.setWidgetResizable(False)

        self.tab_window_gridLayout = QtWidgets.QGridLayout(self.build_central_widget)
        self.four_tab_window = QtWidgets.QTabWidget(self.build_central_widget)

        self.tab_window_gridLayout.addWidget(self.four_tab_window, 0, 0)
        self.tab_window_gridLayout.addWidget(self.mainBuild_scrollArea, 0, 0)
        self.main_central_widget.setLayout(self.tab_window_gridLayout)

        # prep tab
        self.prep_tab = QtWidgets.QWidget()

        self.prep_gridLayout = QtWidgets.QGridLayout()
        self.prep_gridLayout.setSpacing(10)

        self.prep_scrollArea = QtWidgets.QScrollArea()
        self.prep_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.prep_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.prep_scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.prep_scrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.prep_scrollArea.setWidgetResizable(True)

        self.file_btn = QtWidgets.QPushButton()
        self.file_btn.setText("Select File")
        self.file_btn.setGeometry(10, 10, 110, 75)
        self.file_btn.setFont(self.font(20, 75, True))
        self.file_btn.clicked.connect(self.prep_information)

        self.prep_gridLayout.addWidget(self.file_btn, 0, 0)
        self.prep_gridLayout.addWidget(self.prep_scrollArea, 2, 1, 7, 7)
        self.prep_tab.setLayout(self.prep_gridLayout)

        # scan tab window

        self.scan_tab = QtWidgets.QWidget()

        self.scan_gridLayout = QtWidgets.QGridLayout()

        self.scan_scrollArea = QtWidgets.QScrollArea()
        self.scan_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scan_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scan_scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scan_scrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scan_scrollArea.setWidgetResizable(True)

        self.scan_gridLayout.addWidget(self.scan_scrollArea, 1, 1, 11, 11)

        self.sort_btn = QPushButton()
        self.sort_btn.setText("Sort")
        self.sort_btn.setGeometry(10, 10, 110, 75)
        self.sort_btn.setEnabled(self.sensor_num[0])
        self.sort_btn.clicked.connect(self.OneWireSort)  # self.sort)

        self.replace_btn = QPushButton()
        self.replace_btn.setText("Replace Button")
        self.replace_btn.clicked.connect(self.boardReplace)

        self.scan_gridLayout.addWidget(self.sort_btn, 1, 0)
        self.scan_gridLayout.addWidget(self.replace_btn, 2, 0)

        self.scan_tab.setLayout(self.scan_gridLayout)

        # build tab
        self.build_tab = QtWidgets.QWidget()
        self.build_gridLayout = QtWidgets.QGridLayout()

        self.build_scrollArea = QtWidgets.QScrollArea()
        self.build_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.build_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.build_scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.build_scrollArea.setWidgetResizable(True)

        test_btn = QtWidgets.QPushButton()
        test_btn.setText("Test Cable")
        test_btn.setGeometry(10, 10, 110, 75)
        # test_btn.clicked.connect(self.sort)

        para_Pwr_btn = QPushButton()
        para_Pwr_btn.setText("Parasitic Power Test")
        para_Pwr_btn.setGeometry(10, 10, 110, 75)
        # para_Pwr_btn.clicked.connect(self.sort)

        self.build_gridLayout.addWidget(test_btn, 0, 0)
        self.build_gridLayout.addWidget(para_Pwr_btn, 1, 0)

        self.build_gridLayout.addWidget(self.build_scrollArea, 1, 1, 11, 11)
        self.build_tab.setLayout(self.build_gridLayout)

        self.cable_grid = QGridLayout()
        # cable_grid.setColumnStretch(6,1)
        self.cable_group = QGroupBox()
        self.cable_group.setLayout(self.cable_grid)

        # program tab

        self.program_tab = QtWidgets.QWidget()

        self.program_gridLayout = QGridLayout()

        self.program_scrollArea = QtWidgets.QScrollArea()
        self.program_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.program_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.program_scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.program_scrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.program_scrollArea.setWidgetResizable(True)

        self.program_gridLayout.addWidget(self.program_scrollArea, 1, 1, 11, 11)
        self.program_tab.setLayout(self.program_gridLayout)

        eeprom_btn = QPushButton()
        eeprom_btn.setText("Program EEPROM")

        cable_verify_btn = QPushButton()
        cable_verify_btn.setText("Cable Verify")

        final_test_btn = QPushButton()
        final_test_btn.setText("Final Test")

        self.program_gridLayout.addWidget(eeprom_btn, 0, 0)
        self.program_gridLayout.addWidget(cable_verify_btn, 1, 0)
        self.program_gridLayout.addWidget(final_test_btn, 2, 0)

        # inputting of widgets

        self.four_tab_window.addTab(self.prep_tab, "")
        self.four_tab_window.addTab(self.scan_tab, "")
        self.four_tab_window.addTab(self.build_tab, "")
        self.four_tab_window.addTab(self.program_tab, "")

        self.four_tab_window.setTabText(self.four_tab_window.indexOf(self.prep_tab), "Prep")
        self.four_tab_window.setTabText(self.four_tab_window.indexOf(self.scan_tab), "Scan")
        self.four_tab_window.setTabText(self.four_tab_window.indexOf(self.build_tab), "Build")
        self.four_tab_window.setTabText(self.four_tab_window.indexOf(self.program_tab), "Program")

        self.setCentralWidget(self.build_central_widget)

    def calibrateScreen(self):
        central_widget = QWidget()

    def testScreen(self):
        central_widget = QWidget()

    def scan_images(self):
        pass

    def buildDisplay(self):
        cable_grid = QGridLayout()
        cable_grid.setVerticalSpacing(100)
        cable_grid.setHorizontalSpacing(160)
        cable_grid.setRowStretch(2, 1)
        cable_grid.setColumnStretch(10, 1)
        cable_group = QGroupBox()
        cable_group.setLayout(cable_grid)

        program_grid = QGridLayout()
        program_grid.setVerticalSpacing(100)
        program_grid.setHorizontalSpacing(160)
        program_grid.setRowStretch(2, 1)
        program_grid.setColumnStretch(10, 1)
        program_group = QGroupBox()
        program_group.setLayout(program_grid)

        x = 2
        z = 1
        row = 0
        column = 0
        total = self.sensor_num[1]
        for qt in range(0, total):
            if column % 9 is 0:
                row += 1
                column = 0
            box = self.build_img(self.file_specs[x][2], z)
            pBox = self.build_img(self.file_specs[x][2], z)
            cable_grid.addWidget(box, row, column, 2, 2)
            program_grid.addWidget(pBox, row, column, 2, 2)
            column += 1
            x += 1
            z += 1

        self.build_scrollArea.setWidget(cable_group)
        self.program_scrollArea.setWidget(program_group)

    def build_img(self, length, orderNum):
        cable_frame = QtWidgets.QFrame()
        cable_frame.setGeometry(QtCore.QRect(170, 60, 161, 51))
        cable_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        cable_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        cable_frame.setLineWidth(46)

        cable_img = QtWidgets.QLabel(cable_frame)
        cable_img.setGeometry(QtCore.QRect(0, 20, 161, 31))
        cable_img.setPixmap(QtGui.QPixmap("cable and senso.jpg"))
        cable_img.setScaledContents(True)

        length_lbl = QtWidgets.QLabel(cable_frame)
        length_lbl.setText(length + "cm")
        length_lbl.setGeometry(QtCore.QRect(40, 0, 41, 21))
        length_lbl.setFont(self.font(10, 45, True))

        physical_num_lbl = QtWidgets.QLabel(cable_frame)
        physical_num_lbl.setText(str(orderNum))
        physical_num_lbl.setGeometry(QtCore.QRect(130, 0, 41, 16))
        physical_num_lbl.setFont(self.font(10, 75, True))

        return cable_frame

    def prep_information(self):
        """ Grabs the file path for the Select File"""
        select_file = QFileDialog.getOpenFileName(self, "open file", "C:/",
                                                  "Excel (*.csv *.xlsx *.tsv);;PDF(*.pdf);;text(*.txt);;html(*.html)")
        if (select_file[0] is ''):
            return
        else:
            file = open(select_file[0], "r")

        file_contents = []

        for x in file:
            file_contents.append(x)

        # this loop splits info into individual list
        file_desc = []
        for descript_cont in range(1, 7):
            file_desc.append(file_contents[descript_cont].split(","))

        self.file_specs = []
        for content in range(7, len(file_contents)):
            self.file_specs.append(file_contents[content].split(","))

        self.sensor_num[1] = (int(file_desc[2][1]))
        pcba_display = QLabel("Total Sensors: " + str(self.sensor_num[1]))
        pcba_display.setFont(self.font(20, 45, True))
        self.scan_gridLayout.addWidget(pcba_display, 0, 0)

        desc_lbl = []
        desc_lbl.append(QLabel(file_desc[0][0]))
        desc_lbl.append(QLabel(file_desc[0][1]))
        desc_lbl.append(QLabel(file_desc[1][0]))
        desc_lbl.append(QLabel(file_desc[1][1]))
        desc_lbl.append(QLabel(file_desc[2][0]))
        desc_lbl.append(QLabel(file_desc[2][1]))
        desc_lbl.append(QLabel(file_desc[3][0]))
        desc_lbl.append(QLabel(file_desc[3][1]))
        desc_lbl.append(QLabel(file_desc[4][0]))
        desc_lbl.append(QLabel(file_desc[4][1]))
        desc_lbl.append(QLabel(file_desc[5][0]))
        desc_lbl.append(QLabel(file_desc[5][1]))

        desc_lbl[0].setFont(self.font(12, 20, True))
        desc_lbl[2].setFont(self.font(12, 20, True))
        desc_lbl[4].setFont(self.font(12, 20, True))
        desc_lbl[6].setFont(self.font(12, 20, True))
        desc_lbl[8].setFont(self.font(12, 20, True))
        desc_lbl[10].setFont(self.font(12, 20, True))
        desc_lbl[11].setTextFormat(Qt.AutoText)

        comp_lbl = []
        mold_lbl = []
        section_lbl = []
        cable_lbl = []
        addi = 0
        # this for loop makes a label list based on the previous file_spec info
        for lbl in self.file_specs:
            comp_lbl.append(QLabel(self.file_specs[addi][0]))
            mold_lbl.append(QLabel(self.file_specs[addi][1]))
            section_lbl.append(QLabel(self.file_specs[addi][2]))
            cable_lbl.append(QLabel(self.file_specs[addi][3]))
            addi += 1

        comp_lbl[0].setFont(self.font(20, 20, True))
        mold_lbl[0].setFont(self.font(20, 20, True))
        section_lbl[0].setFont(self.font(20, 20, True))
        cable_lbl[0].setFont(self.font(20, 20, True))

        self.frame_group = QGroupBox()
        frame_grid = QGridLayout()

        self.frame_group.setLayout(frame_grid)

        self.frame_1 = QtWidgets.QFrame()
        self.frame_2 = QtWidgets.QFrame()
        self.frame_3 = QtWidgets.QFrame()
        self.frame_4 = QtWidgets.QFrame()

        frame_1_Grid = self.grid(self.frame_1, 0)
        frame_2_Grid = self.grid(self.frame_2, 1)
        frame_3_Grid = self.grid(self.frame_3, 1)
        frame_4_Grid = self.grid(self.frame_4, 1)

        self.frame_1.setLayout(frame_1_Grid)
        self.frame_2.setLayout(frame_2_Grid)
        self.frame_3.setLayout(frame_3_Grid)
        self.frame_4.setLayout(frame_4_Grid)

        frame_grid.addWidget(self.frame_1, 0, 0)
        frame_grid.addWidget(self.frame_2, 0, 2)
        frame_grid.addWidget(self.frame_3, 0, 4)
        frame_grid.addWidget(self.frame_4, 0, 6)

        desc_layout = QGridLayout()
        desc_layout.addWidget(desc_lbl[0], 0, 0)
        desc_layout.addWidget(desc_lbl[1], 0, 1)
        desc_layout.addWidget(desc_lbl[2], 1, 0)
        desc_layout.addWidget(desc_lbl[3], 1, 1)
        desc_layout.addWidget(desc_lbl[4], 2, 0)
        desc_layout.addWidget(desc_lbl[5], 2, 1)
        desc_layout.addWidget(desc_lbl[6], 3, 0)
        desc_layout.addWidget(desc_lbl[7], 3, 1)
        desc_layout.addWidget(desc_lbl[8], 4, 0)
        desc_layout.addWidget(desc_lbl[9], 4, 1)
        desc_layout.addWidget(desc_lbl[10], 5, 0)
        desc_layout.addWidget(desc_lbl[11], 5, 1)

        desc_group = QGroupBox()
        desc_group.setLayout(desc_layout)

        # content
        detail_layout = QGridLayout()
        ran = 1
        for comp in range(1, len(comp_lbl)):
            if comp < 33:
                frame_1_Grid.addWidget(comp_lbl[comp], ran, 0)
                frame_1_Grid.addWidget(mold_lbl[comp], ran, 2)
                frame_1_Grid.addWidget(section_lbl[comp], ran, 4)
                frame_1_Grid.addWidget(cable_lbl[comp], ran, 6)
                ran += 1
            elif comp >= 33 and comp < 65:
                if comp is 33:
                    ran = 1
                frame_2_Grid.addWidget(comp_lbl[comp], ran, 0)
                frame_2_Grid.addWidget(mold_lbl[comp], ran, 2)
                frame_2_Grid.addWidget(section_lbl[comp], ran, 4)
                frame_2_Grid.addWidget(cable_lbl[comp], ran, 6)
                ran += 1
            elif comp >= 65 and comp < 97:
                if comp is 65:
                    ran = 1
                frame_3_Grid.addWidget(comp_lbl[comp], ran, 0)
                frame_3_Grid.addWidget(mold_lbl[comp], ran, 2)
                frame_3_Grid.addWidget(section_lbl[comp], ran, 4)
                frame_3_Grid.addWidget(cable_lbl[comp], ran, 6)
                ran += 1
            elif comp >= 97 and comp < 127:
                if comp is 97:
                    ran = 1
                frame_4_Grid.addWidget(comp_lbl[comp], ran, 0)
                frame_4_Grid.addWidget(mold_lbl[comp], ran, 2)
                frame_4_Grid.addWidget(section_lbl[comp], ran, 4)
                frame_4_Grid.addWidget(cable_lbl[comp], ran, 6)
                ran += 1

        self.prep_gridLayout.addWidget(desc_group, 1, 1)
        self.prep_scrollArea.setWidget(self.frame_group)

        file.close()

    def grid(self, frame, boxNum):

        component = QLabel("Component")
        mold = QLabel("Mold")
        section = QLabel("Section")
        cable = QLabel("Cable Type")

        component.setFont(self.font(20, 20, True))
        mold.setFont(self.font(20, 20, True))
        section.setFont(self.font(20, 20, True))
        cable.setFont(self.font(20, 20, True))

        frame_grid = QGridLayout()
        frame_grid.setVerticalSpacing(0)
        frame_grid.setHorizontalSpacing(1)
        frame_grid.addWidget(component, 0, 0)
        frame_grid.addWidget(mold, 0, 2)
        frame_grid.addWidget(section, 0, 4)
        frame_grid.addWidget(cable, 0, 6)
        frame_grid.setRowStretch(35, 1)

        if boxNum is 1:
            line = QtWidgets.QFrame(frame)
            line.setWindowModality(QtCore.Qt.NonModal)
            line.setGeometry(QtCore.QRect(-7, 0, 10, 1250))
            line.setFrameShadow(QtWidgets.QFrame.Plain)
            line.setLineWidth(5)
            line.setFrameShape(QtWidgets.QFrame.VLine)

        return frame_grid

    def font(self, ptSize, weigth, bold):
        font = QtGui.QFont()
        font.setFamily("System")
        font.setPointSize(ptSize)
        font.setBold(bold)
        font.setWeight(weigth)
        return font

    def pcbaImgInfo(self, num, replace):

        pcba_frame = QtWidgets.QFrame()
        pcba_frame.setGeometry(QtCore.QRect(160, 70, 211, 131))
        pcba_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        pcba_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        pcba_frame.setLineWidth(46)

        pcba_image_lbl = QtWidgets.QLabel(pcba_frame)
        pcba_image_lbl.setGeometry(QtCore.QRect(0, 30, 125, 45))
        pcba_image_lbl.setPixmap(QtGui.QPixmap("Sensor_PCBA.jpg"))
        pcba_image_lbl.setScaledContents(True)

        self.hex_number_lbl = QtWidgets.QLabel(pcba_frame)
        self.hex_number_lbl.setGeometry(QtCore.QRect(0, 77, 160, 16))
        self.hex_number_lbl.setFont(self.font(18, 18, True))
        random_hex = rand.randint(0000000000000000, 9999999999999999)

        self.pcba_hexList.append(random_hex)
        self.pcba_frame_Highlight.append(random_hex)
        self.pcba_hexDict[random_hex] = self.counter
        self.hex_lbl_Dict[self.hex_number_lbl] = self.counter
        self.hex_lbl_list.append(self.hex_number_lbl)

        hex_number = hex(random_hex)
        hex_number = hex_number[2:]
        self.hex_number_lbl.setText(hex_number)

        pcba_right_topCorner_id_lbl = QtWidgets.QLabel(pcba_frame)
        pcba_right_topCorner_id_lbl.setGeometry(QtCore.QRect(0, 10, 45, 16))
        pcba_right_topCorner_id_lbl.setFont(self.font(12, 75, True))

        if self.pcba_counter is 31:
            self.pcba_counter = 1
        if num < 31:
            pcba_right_topCorner_id_lbl.setText("A" + str(num))
        elif num >= 31 and num < 61:
            pcba_right_topCorner_id_lbl.setText("B" + str(self.pcba_counter))
            self.pcba_counter += 1
        elif num >= 61 and num < 91:
            pcba_right_topCorner_id_lbl.setText("C" + str(self.pcba_counter))
            self.pcba_counter += 1
        elif num >= 91 and num < 121:
            pcba_right_topCorner_id_lbl.setText("D" + str(self.pcba_counter))
            self.pcba_counter += 1
        elif num >= 121 and num < 151:
            pcba_right_topCorner_id_lbl.setText("E" + str(self.pcba_counter))
            self.pcba_counter += 1

        self.pcba_orderNum = QLabel(pcba_frame)
        self.pcba_orderNum.setGeometry(QtCore.QRect(109, 10, 50, 20))
        self.pcba_orderNum.setFont(self.font(9, 10, True))

        self.pcba_imgs.append(self.pcba_orderNum)
        self.pcba_frame_Dict[pcba_frame] = self.counter

        self.pcba_print(pcba_frame, self.counter - 1)

    def pcba_print(self, box, increment):

        if increment is self.sensor_num[1] - 1:
            self.sensor_num[0] = True
            self.sort_btn.setEnabled(self.sensor_num[0])

        if (increment % 6) is 0:
            self.colbCount = 0
            self.rowCount += 1
        if (self.counter % 30 is 0):
            line = self.line()
            self.pcba_gridlayout.addWidget(line, self.rowCount - 2, 0, 7, 7)
        self.pcba_gridlayout.addWidget(box, self.rowCount, self.colbCount, 2, 2)
        self.colbCount += 1

        self.scan_scrollArea.setWidget(self.pcba_groupBox)

    def highlight(self, nextNum, rightClick):

        if (rightClick):
            for key in self.pcba_frame_Dict:
                if nextNum is self.pcba_frame_Dict.get(key):
                    key.setAutoFillBackground(True)
                    key.setPalette(self.palette(255, 139, 119))
                    if key is not self.pcba_memory:
                        self.pcba_memory.append(key)

            if nextNum > 1:
                self.pcba_memory[nextNum - 2].setAutoFillBackground(False)
            self.physical_num += 1
        else:  # left click
            self.pcba_memory[nextNum - 2].setAutoFillBackground(False)
            self.pcba_memory[nextNum - 3].setAutoFillBackground(True)
            self.physical_num -= 1

    def palette(self, red, green, blue):
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(red, green, blue))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        return palette

    def line(self):
        line = QtWidgets.QFrame()
        line.setGeometry(QtCore.QRect(10, 350, 781, 16))

        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)

        line.setPalette(palette)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setMidLineWidth(20)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        return line

    def boardReplace(self):
        self.message = QDialog()
        self.message.resize(650, 150)
        self.message.setSizeGripEnabled(True)
        self.message.setWindowTitle("Board Replace")

        msg_grid = QGridLayout()
        self.message.setLayout(msg_grid)

        self.msg_lineEdit = QtWidgets.QLineEdit(self.message)
        self.msg_lineEdit.setGeometry(QtCore.QRect(480, 10, 113, 22))
        self.msg_lineEdit.setPlaceholderText("ex: 5")
        self.msg_lineEdit.setEnabled(True)

        replace_label = QtWidgets.QLabel(self.message)
        replace_label.setGeometry(QtCore.QRect(10, 10, 550, 20))
        replace_label.setText("Please enter the physical number of the board to Replace:")
        replace_label.setFont(self.font(15, 20, True))

        self.msg_lineEdit.returnPressed.connect(self.sortButtonWarning)

        x = self.message.exec_()

    def sortButtonWarning(self):

        num = int(self.msg_lineEdit.text())
        #these two if statements are an error check!
        if num > self.sensor_num[1] or num < 1:
            error = QMessageBox.critical(self.message,"Error","Physical number not found please enter again",QMessageBox.Ok)
            if error == QMessageBox.Ok:
                self.message.close()
                self.boardReplace()
        else:
            self.newScan(self.msg_lineEdit.text())

            call = QMessageBox.information(self.message,"Sort Button","Would you like to re-Enable the Sort Button? ",QMessageBox.Yes | QMessageBox.No)

            if call == QMessageBox.Yes:
                self.yesButton()
            if call == QMessageBox.No:
                self.noButton()

    def newScan(self,phy_num):
        scan_new = QMessageBox.information(self.message,"Scan New pcba","Please Scan New PCBA Board",QMessageBox.Ok)
        random_hex = rand.randint(0000000000000000, 9999999999999999)
        hex_number = hex(random_hex)
        hex_number = hex_number[2:]

        index = 0




        #this loop updates self.pcba_hexList
        for oldHex in self.pcba_hexDict:
            if self.pcba_hexDict[oldHex] is int(phy_num):
                index = self.pcba_hexList.index(oldHex)
                self.pcba_hexList.remove(oldHex)
                self.pcba_hexList.insert(index,random_hex)

        for key in self.hex_lbl_Dict:
            if self.hex_lbl_Dict.get(key) is int(phy_num):
                key.setText(hex_number)

    def yesButton(self):
        m = QMessageBox.warning(self.message,"Warning",
                                   "Are you sure you want to re-Sort?Why dont you give Rodrigo a call? Doing so will re-organize all the boards! ",
                                QMessageBox.Yes | QMessageBox.No)
        if m == QMessageBox.Yes:
            self.doubleCheck()
        else:
            self.noButton()

    def doubleCheck(self):
        self.sort_btn.setEnabled(True)
        self.message.close()

    def noButton(self):
        self.message.close()

    def OneWireSort(self):
        zero_list = []
        one_list = []
        bin_hex_list = []

        for hex in self.pcba_hexList:
            bin_hex_list.append(bin(hex))

        # split hex list into zeros and ones
        for binary in bin_hex_list:
            if binary[self.lsb] is "0":
                zero_list.append(binary)
            else:
                one_list.append(binary)

        zList = len(zero_list)
        self.Halfsies(zero_list, 1, len(zero_list))
        self.Halfsies(one_list, zList + 1, len(one_list))

        count = 0
        # this for loop creates a dictionary with binary as key and number as value
        for b in bin_hex_list:
            self.final_order[b] = str(count)
            count += 1

        key_count = 0

        for order in self.final_order:  # order grabs the binary string
            for place in self.order_dict:  # place grabs the physical location
                if order is self.order_dict[place]:  # searches throught the binary strings in order dict and puts them in final order
                    self.final_order[order] = place
                    self.hex_lbl_Dict[self.hex_lbl_list[key_count]] = place
                    key_count += 1

        run = 0
        next = 0
        # this nested loop updates the pcba frame with its physical order
        for key in self.final_order:
            for frame in self.pcba_frame_Dict:
                if run is next:
                    self.pcba_frame_Dict[frame] = self.final_order[key]
                run += 1
            run = 0
            next += 1

        c = 0
        for phys_num in self.final_order:  # this loop puts that number as a label to the frame box of pcba's
            self.pcba_imgs[c].setText(str(self.final_order[phys_num]))
            c += 1

        info = QLabel("Use 'A' or 'D' to cycle through the pcba boards")
        info.setFont(self.font(20, 20, True))
        self.scan_gridLayout.addWidget(info, 0, 2)

        self.file_btn.setEnabled(False)
        self.highlight(self.physical_num, True)
        self.sort_btn.setEnabled(False)
        self.buildDisplay()
        self.final_order.clear()

    def Halfsies(self, list, key, size):
        '''This method sorts and puts the given list into the self.order_dict dictionary'''
        count = 1
        last = -2
        k = key
        first_index = 0

        for run in range(size):
            hold = list[0]
            while count < len(list):
                if hold[last] < list[count][last]:
                    count += 1
                    last = -2

                elif hold[last] is list[count][last]:
                    last -= 1

                elif hold[last] > list[count][last]:
                    first_index = list.index(hold)
                    hold = list[count]
                    list[first_index], list[count] = list[count], list[first_index]
                    last = -2
                    count = 1
            self.order_dict[k] = hold  # this will put the least on top
            k += 1
            count = 1
            list.remove(hold)


def showscreen():
    app = QApplication([])
    app.setStyle("fusion")
    window = MainUtility()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    showscreen()
