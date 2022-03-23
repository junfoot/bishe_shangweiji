import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import untitled

if __name__ == '__main__':
    # pyqt5程序都需要QApplication对象
    app = QApplication(sys.argv)

    myMainWindow = QMainWindow()
    myUi = untitled.Ui_MainWindow()
    myUi.setupUi(myMainWindow)
    myMainWindow.show()
    # 确保程序完整推出
    sys.exit(app.exec_())