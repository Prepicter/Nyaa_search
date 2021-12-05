import sys
import requests
from bs4 import BeautifulSoup
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

form_class = uic.loadUiType("./winUi.ui")[0]
search_data = []
row_size = 0
# mode 1 : nyaa / 2 : sukebei
search_mod = 2


class App(QMainWindow, form_class):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setup_menu()
        self.connect_ui()

    def setup_menu(self):
        _menubar = self.menuBar()
        menu1 = _menubar.addMenu('설정')
        mode_1 = QAction('Nyaa', self)
        mode_2 = QAction('Sukebei', self)

        mode_1.setCheckable(True)
        mode_2.setCheckable(True)
        mode_2.setChecked(True)

        group = QActionGroup(self)
        group.addAction(mode_1)
        group.addAction(mode_2)

        mode_1.triggered.connect(self.change_mode)
        mode_2.triggered.connect(self.change_mode)
        menu1.addAction(mode_1)
        menu1.addAction(mode_2)

    def change_mode(self):
        global search_mod
        if search_mod == 2:
            search_mod = 1
            self.statusBar().showMessage('Nyaa 검색 모드')
        else:
            search_mod = 2
            self.statusBar().showMessage('Sukebei 검색 모드')

    def connect_ui(self):
        # 아이콘
        self.setWindowIcon(QIcon('icon.png'))
        # 콤보 박스 추가
        self.comboBox.addItem('Game')
        self.comboBox.addItem('Anime')
        # 테이블 사전설정
        table = self.tableWidget
        table.setColumnWidth(0, 70)
        table.setColumnWidth(1, 528)
        table.setColumnWidth(2, 40)
        table.setColumnWidth(3, 80)
        table.setColumnWidth(4, 140)
        table.setColumnWidth(5, 60)

        # 상태바
        self.statusBar().showMessage('대기중')
        # 검색 버튼
        self.pushButton.clicked.connect(self.search)
        # 엔터 쳤을 때
        self.lineEdit.returnPressed.connect(self.search)
        self.show()

    def search(self):
        global search_mod
        text = self.lineEdit.text()
        category = self.comboBox.currentIndex()
        if search_mod == 1:
            mode = 'nyaa.si'
            if category == 0:
                generate = '6_0'  # Game
            else:
                generate = '1_0'  # Anime
        else:
            mode = 'sukebei.nyaa.si'
            if category == 0:
                generate = '1_3'  # Game
            else:
                generate = '1_1'  # Anime
        url = 'https://{0}/?f=0&c={1}&q={2}'.format(mode, generate, text)
        self.refresh_table(url)

    def refresh_table(self, url):
        global row_size
        table = self.tableWidget
        table.clearContents()
        target = requests.get(url)
        pages = 0
        html_doc = target.text
        # print(html_doc)
        soup = BeautifulSoup(html_doc, 'html.parser')
        # 데이터 확인
        try:
            table_row = soup.find('tbody').find_all('tr')
        except AttributeError:
            print('검색대상이 없습니다')
            return
        # 페이지 수 확인
        # 실제 값에서 -2
        try:
            pages = soup.find('div', "center").find_all('li')
        except AttributeError:
            self.statusBar().showMessage('검색결과 1/1 페이지')
        print(len(pages))
        # print(table_row[1])
        table.setRowCount(len(table_row))
        row_size = len(table_row)
        for i in range(len(table_row)):
            print(table_row[i])
            line = table_row[i].find_all('td')
            # 카테고리
            cat = line[0].select('a')[0]['title']
            try:
                title = line[1].select('a')[1]['title']
            except IndexError:
                title = line[1].select('a')[0]['title']
            try:
                magnet = line[2].select('a')[1]['href']
            except IndexError:
                magnet = line[2].select('a')[0]['href']
            size = line[3].text
            time = line[4].text
            down = line[7].text
            _list = [cat, title, magnet, size, time, down]
            search_data.append(_list)
            # print('카테고리 : {0}\n제목 : {1}\n주소 : {2}\n크기 : {3}'.format(cat, title, magnet, size))
            # print(_list)
            for j in range(len(_list)):
                if j == 2:
                    # 마그넷
                    link = QLabel()
                    _url = '<a href="' + _list[j] + '">링크</a>'
                    link.setText(_url)
                    link.setOpenExternalLinks(True)
                    link.setAlignment(QtCore.Qt.AlignCenter)
                    table.setCellWidget(i, j, link)
                    continue
                item = QTableWidgetItem(_list[j])
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                table.setItem(i, j, item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
