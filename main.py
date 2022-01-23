import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from multiprocessing import Process, Queue, pool
import multiprocessing as mp
import datetime
import time
from mitutoyo import mitutoyo
from playsound import playsound
import csv
import os
import configparser
import pyautogui as pag

#config.ini
parser = configparser.SafeConfigParser() # for ini file
parser.read("config.ini") # deployment for ini fil
threshold = parser.get("threshold", "threshold") # threshold value
name00 = parser.get("name", "name00") # worker name
name01 = parser.get("name", "name01") # worker name
name02 = parser.get("name", "name02") # worker name
filepath_csv = parser.get("filepath", "filepath") # filepath for the result

filepath_txt ="data\\管理番号.txt" #filepath for "管理番号": tempolarly path, not important

# threshold
threshold = threshold

# warning sound
sound_0010 = 'data\\a.wav' #0.010
sound_0020 = 'data\\b.wav' #0.020
sound_0030 = 'data\\c.wav' #0.030
sound_0040 = 'data\\d.wav' #0.040
sound_0045 = 'data\\e.wav' #0.045
sound_0046 = 'data\\f.wav' #0.046
sound_0047 = 'data\\g.wav' #0.047
sound_0048 = 'data\\h.wav' #0.048
sound_0049 = 'data\\i.wav' #0.049
sound_0050 = 'data\\j.wav' #0.050
sound_error = 'data\\z.wav' #error

# while loop, data from MITUTOYO degimatic guage
def loop(q):
    while True:

        time.sleep(0.5)

        value = mitutoyo()
        q.put(value)

# Alarm
def alarm(q):
    while True:

        value = q.get()

        if float(value) == -100: # for the error: device is in problem
            while True:
                playsound(sound_error)

        if float(value) == 0.010:
            playsound(sound_0010)

        elif float(value) == 0.020:
            playsound(sound_0020)

        elif float(value) == 0.030:
            playsound(sound_0030)

        elif float(value) == 0.040:
            playsound(sound_0040)

        elif float(value) == 0.045:
            playsound(sound_0045)

        elif float(value) == 0.046:
            playsound(sound_0046)

        elif float(value) == 0.047:
            playsound(sound_0047)

        elif float(value) == 0.048:
            playsound(sound_0048)

        elif float(value) == 0.049:
            playsound(sound_0049)

        elif float(value) >= float(threshold):
            playsound(sound_0050)


# data logger from MITUTOYO device
def logger(q):

    # read 管理番号 from the txt file
    f = open(filepath_txt, "r")
    filepath_csv = f.readline()

    # csv file: strain change history
    while True:
        value = q.get()
        f = open(filepath_csv, "a")
        writer =csv.writer(f, lineterminator='\n')
        dt = datetime.datetime.now()
        dt1 = dt.strftime('%Y/%m/%d')
        dt2 = dt.strftime('%H:%M:%S')
        if float(value) == -100:
            value = "ダイヤルゲージ異常"
            writer.writerow([dt1, dt2, value])
            f.close()
        else:
            if float(value) < float(threshold):
                writer.writerow([dt1, dt2, value])
                f.close()
            else:
                abnormal = "闘値"
                writer.writerow([dt1, dt2, value, abnormal])
                f.close()

        print(dt2, value)

def producer(q):
    proc = mp.current_process()
    #print(proc.name)
    print("program start")
    # これを入れておかないと"計測開始"を押さないで、ダイヤルゲージの値が閾値を超えた場合に、警告を発し続ける。
    # これは必ず入れなければならない。
    while True:
        print(q.get())

#necessary file for multiprocessing
class Consumer(QThread):

    poped = Signal(str)

    def __init__(self, q):
        super().__init__()
        self.q = q

    def run(self):
        while True:
            self.poped.emit(q.get())

# GUI
class MyWindow(QMainWindow):

    def __init__(self, q):
        super().__init__()

        self.wo01 = QLineEdit("", self)
        self.wo01.move(20,10)
        self.wo01.resize(400, 100)
        self.wo01.setPlaceholderText(' 作業用番号') # 透かしで表示
        self.wo01.setStyleSheet("color: black; font: 20pt Arial; border-color: black; "
                              "border-style:solid; border-width: 1.5px; border-radius:10px") # 文字の大きさなど


        self.wk01 = QComboBox(self)
        self.wk01.addItem(name00)
        self.wk01.addItem(name01)
        self.wk01.addItem(name02)
        self.wk01.move(480,10)
        self.wk01.resize(400, 100)
        self.wk01.setStyleSheet("color: black; font: 20pt Arial; border-color: white; "
                                "border-style:solid; border-width: 1.5px; border-radius:10px") # 文字の大きさなど

        self.btn01 = QPushButton("計測開始", self)
        self.btn01.move(950, 10)
        self.btn01.resize(400, 100)
        self.btn01.setStyleSheet("color: black; font: 20pt Arial; border-color: black; "
                                "border-style:solid; border-width: 1.5px; border-radius:10px") # 文字の大きさなど
        self.btn01.clicked.connect(self.header)

        self.setGeometry(200, 200, 300, 200)

        self.label = QLabel(self)
        self.label.move(0, 120)
        self.label.resize(1366, 768)

        HBox = QHBoxLayout()
        HBox.addWidget(self.wo01)
        HBox.addWidget(self.wk01)
        HBox.addWidget(self.btn01)
        HBox.addWidget(self.label)
        HBox.addStretch(0)

    # header for CSV + logger start
    def header(self):

        # csv header
        self.filepath_csv = filepath_csv + self.wo01.text() + ".csv"

        # check the file has been already existed or not, if not save headers.
        if not os.path.exists(self.filepath_csv):
            # write the header
            csvlist = []
            f = open(self.filepath_csv, 'w')
            writer = csv.writer(f, lineterminator='\n')

            writer.writerow(["作業番号", self.wo01.text()])
            writer.writerow(["作業者名", self.wk01.currentText()])
            writer.writerow(["日付","時間","熱変形量[mm]","闘値超え"])

            writer.writerow(csvlist)
            f.close()

        else:
            pass

        # to pass the 作業用番号 to the "def logger": saved in txt file
        with open(filepath_txt, mode="w") as f:
            f.write(self.filepath_csv)

        # thread for data consumer
        self.consumer = Consumer(q)
        self.consumer.poped.connect(self.print_data)
        self.consumer.start()

        # multiprocessing p3 start
        p3.start()

    #@pyqtSlot(str)
    def print_data(self, data):
        #self.statusBar().showMessage(data)

       #print(type(data))
        if 0 <= float(data) < 0.045:
            self.label.setText("  " + data)
            self.styleA = "QWidget{background-color:%s; font: 300pt Arial}" % ("green")
            self.label.setStyleSheet(self.styleA)

        elif 0.045 <= float(data) <= 0.049:
            self.label.setText("  " + data)
            self.styleA = "QWidget{background-color:%s; font: 300pt Arial}" % ("yellow")
            self.label.setStyleSheet(self.styleA)

        elif 0.050 <= float(data) < 100:
            self.label.setText("  " + data)
            self.styleA = "QWidget{background-color:%s; font: 300pt Arial}" % ("brown")
            self.label.setStyleSheet(self.styleA)

        elif float(data) == -100:
            data = "ダイヤルゲージ異常"
            self.label.setText(data)
            self.styleB = "QWidget{background-color:%s; font: 135pt Arial}" % ("brown")
            self.label.setStyleSheet(self.styleB)

if __name__ == "__main__":

    q = Queue()

    with pool.Pool(processes=4) as p:

        #multiprocessing
        p0 = p.Process(target=loop, args=(q, ), daemon=True)
        p1 = p.Process(target=alarm, args=(q, ), daemon=True)
        p2 = p.Process(name="producer", target=producer, args=(q,), daemon=True)
        p3 = p.Process(target=logger, args=(q, ), daemon=True)

        p0.start()
        p1.start()
        p2.start()

    # Main process
    app = QApplication(sys.argv)
    mywindow = MyWindow(q)
    mywindow.setWindowTitle("熱変形量監視ソフト Version 0.0.0") # windowのtitle
    #mywindow.showFullScreen()

    scr_w,scr_h= pag.size() #LCD resolution

    mywindow.setFixedSize(scr_w*0.71, scr_h*0.71)  # windows size based on LCD resolution
    mywindow.show()
    app.exec_()