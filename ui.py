import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QTextEdit, QFileDialog, QHBoxLayout, \
    QVBoxLayout, QSplitter, QSpinBox
from PyQt5.Qt import QWidget, QColor, QCheckBox, QPalette
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from Paintboard import PaintBoard
import util
from PIL import Image


class FirstUi(QMainWindow):
    def __init__(self, server):
        super(FirstUi, self).__init__()
        self.init_ui()
        self.server = server

    def init_ui(self):
        self.setFixedSize(self.width(), self.height())
        self.setWindowIcon(QtGui.QIcon('./icon.jpg'))
        self.resize(640, 500)  # 设置窗口大小
        self.setWindowTitle(' ')  # 设置窗口标题
        self.btn = QPushButton('手写板识别', self)  # 设置按钮和按钮名称
        self.btn.setGeometry(245, 100, 150, 50)  # 前面是按钮左上角坐标，后面是窗口大小
        self.btn.clicked.connect(self.slot_btn_function)  # 将信号连接到槽
        self.btn2 = QPushButton('图片识别', self)
        self.btn2.setGeometry(245, 200, 150, 50)
        self.btn2.clicked.connect(self.slot_btn2_function)
        self.btn_exit = QPushButton('退出', self)
        self.btn_exit.setGeometry(245, 300, 150, 50)
        self.btn_exit.clicked.connect(self.quit)

    def quit(self):
        self.close()

    def slot_btn_function(self):
        self.hide()  # 隐藏此窗口
        self.s = writeIn(self.server)  # 将第二个窗口换个名字
        self.s.show()  # 经第二个窗口显示出来

    def slot_btn2_function(self):
        self.hide()
        self.s = pictureIn(self.server)
        self.s.show()


# 手写板识别
class writeIn(QWidget):
    def __init__(self, server):
        super(writeIn, self).__init__()
        self.__InitData()
        self.__InitView()
        self.server = server

    def __InitData(self):
        '''
                  初始化成员变量
        '''
        self.__paintBoard = PaintBoard(self)
        # 获取颜色列表(字符串类型)
        self.__colorList = QColor.colorNames()

    def __InitView(self):
        '''
                  初始化界面
        '''
        self.resize(1000, 600)
        self.setWindowIcon(QtGui.QIcon('./icon.jpg'))
        self.setWindowTitle("手写板识别")

        self.recognition_result = QLabel('识别结果', self)
        self.recognition_result.setGeometry(530, 50, 430, 200)
        self.recognition_result.setAlignment(QtCore.Qt.AlignCenter)

        # 新建一个水平布局作为本窗体的主布局
        main_layout = QHBoxLayout(self)
        # 设置主布局内边距以及控件间距为10px
        main_layout.setSpacing(10)
        img_layout = QVBoxLayout()
        img_layout.setContentsMargins(10, 10, 10, 10)

        # 在主界面左侧放置画板
        img_layout.addWidget(self.__paintBoard)
        self.detection_result = QLabel('检测结果', self)
        self.detection_result.setGeometry(10, 300, 480, 280)
        self.detection_result.setStyleSheet("QLabel{background:white;}"
                                            "QLabel{color:rgb(0,0,0,120);font-size:15px;font-weight:bold;font-family:宋体;}"
                                            )
        self.detection_result.setAlignment(QtCore.Qt.AlignCenter)
        img_layout.addWidget(self.detection_result)

        main_layout.addLayout(img_layout)  # 将子布局加入主布局

        # 新建垂直子布局用于放置按键
        sub_layout = QVBoxLayout()
        # 设置此子布局和内部控件的间距为5px
        sub_layout.setContentsMargins(5, 5, 5, 5)

        splitter = QSplitter(self)  # 占位符
        sub_layout.addWidget(splitter)
        # sub_layout.addWidget(self.label_name)
        # sub_layout.addWidget(self.recognition_result)

        self.__btn_Recognize = QPushButton("开始处理")
        self.__btn_Recognize.setParent(self)
        self.__btn_Recognize.clicked.connect(self.on_btn_Recognize_Clicked)
        sub_layout.addWidget(self.__btn_Recognize)

        self.__btn_Clear = QPushButton("清空画板")
        self.__btn_Clear.setParent(self)  # 设置父对象为本界面
        # 将按键按下信号与画板清空函数相关联
        self.__btn_Clear.clicked.connect(self.__paintBoard.Clear)
        sub_layout.addWidget(self.__btn_Clear)

        self.__btn_return = QPushButton("返回")
        self.__btn_return.setParent(self)
        self.__btn_return.clicked.connect(self.slot_btn_function)
        sub_layout.addWidget(self.__btn_return)

        self.__btn_quit = QPushButton("退出")
        self.__btn_quit.setParent(self)
        self.__btn_quit.clicked.connect(self.quit)
        sub_layout.addWidget(self.__btn_quit)

        self.__btn_Save = QPushButton("保存作品")
        self.__btn_Save.setParent(self)
        self.__btn_Save.clicked.connect(self.on_btn_Save_Clicked)
        sub_layout.addWidget(self.__btn_Save)

        self.__cbtn_Eraser = QCheckBox("使用橡皮擦")
        self.__cbtn_Eraser.setParent(self)
        self.__cbtn_Eraser.clicked.connect(self.on_cbtn_Eraser_clicked)
        sub_layout.addWidget(self.__cbtn_Eraser)

        self.__label_penThickness = QLabel(self)
        self.__label_penThickness.setText("画笔粗细")
        self.__label_penThickness.setFixedHeight(20)
        sub_layout.addWidget(self.__label_penThickness)

        self.__spinBox_penThickness = QSpinBox(self)
        self.__spinBox_penThickness.setMaximum(20)
        self.__spinBox_penThickness.setMinimum(2)
        self.__spinBox_penThickness.setValue(10)  # 默认粗细为10
        self.__spinBox_penThickness.setSingleStep(2)  # 最小变化值为2
        self.__spinBox_penThickness.valueChanged.connect(
            self.on_PenThicknessChange)  # 关联spinBox值变化信号和函数on_PenThicknessChange
        sub_layout.addWidget(self.__spinBox_penThickness)

        main_layout.addLayout(sub_layout)  # 将子布局加入主布局

    def on_PenThicknessChange(self):
        penThickness = self.__spinBox_penThickness.value()
        self.__paintBoard.ChangePenThickness(penThickness)

    def on_btn_Save_Clicked(self):
        savePath = QFileDialog.getSaveFileName(self, 'Save Your Paint', '.\\', '*.png')
        print(savePath)
        if savePath[0] == "":
            print("Save cancel")
            return
        image = self.__paintBoard.GetContentAsQImage()
        image.save(savePath[0])
        print(savePath[0])

    def quit(self):
        self.close()

    def on_cbtn_Eraser_clicked(self):
        if self.__cbtn_Eraser.isChecked():
            self.__paintBoard.EraserMode = True  # 进入橡皮擦模式
        else:
            self.__paintBoard.EraserMode = False  # 退出橡皮擦模式

    def on_btn_Recognize_Clicked(self):  # 识别过程**
        savePath = "./img/text.png"
        image = self.__paintBoard.GetContentAsQImage()
        image.save(savePath)

        new_image = Image.new('RGBA', (image.width() + 800, image.height() + 800), (255, 255, 255, 255))
        new_image.paste(Image.open(savePath), (400, 400))
        new_image.save(savePath)

        detection_result_path, recognition_result_path = self.server.handle(savePath)
        result_jpg = QtGui.QPixmap(detection_result_path)
        result_width = self.detection_result.width()
        result_height = result_jpg.height() * (self.detection_result.width()) / result_jpg.width()
        jpg = QtGui.QPixmap(detection_result_path).scaled(int(result_width), int(result_height))
        self.detection_result.setPixmap(jpg)

        recognition_result_txt = ''
        if os.path.isfile(recognition_result_path):
            fp = open(recognition_result_path, 'r', encoding='utf-8')
            line = fp.readline()
            while line:
                recognition_result_txt += line
                line = fp.readline()
        self.recognition_result.setText(recognition_result_txt)

    def slot_btn_function(self):
        self.hide()
        self.f = FirstUi(self.server)
        self.f.show()


# 图片识别
class pictureIn(QWidget):
    def __init__(self, server):
        super(pictureIn, self).__init__()
        self.init_ui()
        self.server = server

    def init_ui(self):
        self.resize(1300, 880)
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle('图片识别')

        self.input = QLabel('待载入图片', self)
        self.input.setGeometry(10, 20, 600, 400)
        self.input.setStyleSheet(
            "QLabel{background:gray;}""QLabel{color:rgb(0,0,0,120);font-size:15px;font-weight:bold;font-family:宋体;}"
        )
        self.input.setAlignment(QtCore.Qt.AlignCenter)

        self.detection_result = QLabel('检测结果', self)
        self.detection_result.setGeometry(10, 450, 600, 400)
        self.detection_result.setStyleSheet("QLabel{background:white;}"
                                            "QLabel{color:rgb(0,0,0,120);font-size:15px;font-weight:bold;font-family:宋体;}"
                                            )
        self.detection_result.setAlignment(QtCore.Qt.AlignCenter)

        # 结果显示框
        self.recognition_result = QLabel('识别结果', self)
        self.recognition_result.setGeometry(650, 10, 600, 400)
        self.recognition_result.setWordWrap(True)
        self.recognition_result.setAlignment(Qt.AlignCenter)
        QPalette().setColor(QPalette.WindowText, Qt.black)
        self.recognition_result.setAutoFillBackground(True)
        QPalette().setColor(QPalette.Window, Qt.white)
        self.recognition_result.setPalette(QPalette())

        self.btn_select = QPushButton('选择图片', self)
        self.btn_select.setGeometry(900, 550, 100, 30)
        self.btn_select.clicked.connect(self.select_image)

        self.btn_dis = QPushButton('处理图片', self)
        self.btn_dis.setGeometry(900, 600, 100, 30)
        self.btn_dis.clicked.connect(self.on_btn_handle_Clicked)

        self.btn = QPushButton('返回', self)
        self.btn.setGeometry(900, 650, 100, 30)
        self.btn.clicked.connect(self.slot_btn_function)

        self.btn_exit = QPushButton('退出', self)
        self.btn_exit.setGeometry(900, 700, 100, 30)
        self.btn_exit.clicked.connect(self.quit)

    def select_image(self):
        global fname
        imgName, imgType = QFileDialog.getOpenFileName(self, "打开图片", "", "All Files(*)")
        jpg1 = QtGui.QPixmap(imgName)

        select_width = self.input.width()
        select_height = jpg1.height() * (self.input.width()) / jpg1.width()

        jpg = QtGui.QPixmap(imgName).scaled(int(select_width), int(select_height))
        self.input.setPixmap(jpg)
        fname = imgName

    def on_btn_handle_Clicked(self):
        global fname

        detection_result_path, recognition_result_path = self.server.handle(fname)
        result_jpg = QtGui.QPixmap(detection_result_path)
        result_width = self.detection_result.width()
        result_height = result_jpg.height() * (self.detection_result.width()) / result_jpg.width()
        jpg = QtGui.QPixmap(detection_result_path).scaled(int(result_width), int(result_height))
        self.detection_result.setPixmap(jpg)

        recognition_result_txt = ''
        if os.path.isfile(recognition_result_path):
            fp = open(recognition_result_path, 'r', encoding='utf-8')
            line = fp.readline()
            while line:
                recognition_result_txt += line
                line = fp.readline()
        self.recognition_result.setText(recognition_result_txt)

    def quit(self):
        self.server.close()
        self.close()

    def slot_btn_function(self):
        self.hide()
        self.f = FirstUi(self.server)
        self.f.show()


def main():
    app = QApplication(sys.argv)
    server = util.Socket_client()
    w = FirstUi(server)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
