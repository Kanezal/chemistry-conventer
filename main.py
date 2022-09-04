from ast import List
import sys
import time
from urllib import request
import requests
from bs4 import BeautifulSoup
from wolframalpha import Client
from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings

from PyQt5.QtGui import QIcon

from ui import Ui_MainWindow

client = Client("your-wolframalpha-api-key")


class ChemistryConv(QtWidgets.QMainWindow):
    def __init__(self):
        super(ChemistryConv, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle('Конвертер формул')
        self.setWindowIcon(QIcon('test_tube.ico'))
        self.ui.formulainput.setPlaceholderText('Формула:')
        self.ui.pushButton.clicked.connect(self.converter)

        self.ui.formulainput.returnPressed.connect(self.ui.pushButton.click)

        self.structurediagramhtml = QWebEngineView(self)
        self.structurediagramhtml.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.structurediagramhtml.sizePolicy().hasHeightForWidth())
        self.structurediagramhtml.setSizePolicy(sizePolicy)
        self.structurediagramhtml.setAutoFillBackground(False)
        self.structurediagramhtml.setObjectName("structurediagramhtml")

        self.ui.gridLayout.addWidget(self.structurediagramhtml, 1, 0, 1, 2)

    def converter(self):
        formula_input = self.ui.formulainput.text()

        if formula_input == "":
            self.show_html(error=True)
            return 0

        r = requests.get(
            f"http://www.charchem.org/ru/subst-ref/?keyword={formula_input}&langMode=&langs=&brutto={formula_input}",
        )

        soup = BeautifulSoup(r.text, features="html.parser")
        echems = soup.findAll('div', {'class': 'echem-formula'})

        try:
            if echems[1]:
                pass

            self.show_html(echems[0:1])
            return 0
        except IndexError:
            try:
                if echems[0]:
                    pass
                self.show_html(echems[0:0])
                return 0
            except IndexError:
                self.show_html(wait=True)

        res = client.query(formula_input)
        for pod in res.pods:
            for subpod in pod.subpods:
                if subpod.img.alt == "Structure diagram":
                    link = subpod.img.src
                    self.show_html(src=link)
                    return 0
        self.show_html(error=True)

    def show_html(self, formulas: List = [], wait: bool = False, error: bool = False, src: str = None):
        print(formulas, wait, error, src)

        if len(formulas) != 0:
            echem = True
            html_formula = ""

            for formula in formulas:
                html_formula += f'<div align="center" class="echem-formula">{formula}</div>'
        else:
            html_formula = None
            echem = False

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
            <script type="text/javascript" src="http://code.jquery.com/jquery-latest.js"></script>
            <script type="text/javascript" src="http://easychem.org/download/easychem.js"></script>
            <link rel="stylesheet" type="text/css" href="http://easychem.org/download/easychem.css"/>
        </head>
        <body {'class="echem-auto-compile"' if echem else ""} style="zoom: 150%">
            {
                html_formula if html_formula is not None else ""
            }
            {
                '<div align="center"> Ошибка при вводе формулы. Или мы не можем её распознать.</div>' if error else ""
            }
            {
                '<div align="center"> Подождите, мы используем другой вариант поиска.</div>' if wait else ""
            }
            {
                f'<div align="center"><img src="{src}"></div>' if src is not None else ""
            }
        </body>
        </html>
        """
        print(html)
        self.structurediagramhtml.setHtml(html)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    application = ChemistryConv()
    application.show()

    sys.exit(app.exec())
