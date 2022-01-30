# python-3.7.6-amd64

import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from multiprocessing import Process, Queue, pool
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
sleep_loop = parser.get("sleep", "loop")
sleep_alarm = parser.get("sleep", "alarm") # threshold value
sleep_logger = parser.get("sleep", "logger")
name00 = parser.get("name", "name00") # worker name
name01 = parser.get("name", "name01") # worker name
name02 = parser.get("name", "name02") # worker name
name03 = parser.get("name", "name03") # worker name
name04 = parser.get("name", "name04") # worker name
name05 = parser.get("name", "name05") # worker name
name06 = parser.get("name", "name06") # worker name
name07 = parser.get("name", "name07") # worker name
name08 = parser.get("name", "name08") # worker name
name09 = parser.get("name", "name09") # worker name
name10 = parser.get("name", "name10") # worker name
filepath_csv = parser.get("filepath", "filepath") # filepath for the result

filepath_txt ="data\\管理番号.txt" #filepath for "管理番号": tempolarly path, not important

# warning sound
sound_a = 'data\\a.wav' #0.005
sound_b = 'data\\b.wav' #0.010
sound_c = 'data\\c.wav' #0.020
sound_d = 'data\\d.wav' #0.030
sound_e = 'data\\e.wav' #0.040
sound_f = 'data\\f.wav' #0.050
sound_g = 'data\\g.wav' #0.060
sound_h = 'data\\h.wav' #0.070
sound_i = 'data\\i.wav' #0.080
sound_j = 'data\\j.wav' #0.090
sound_k = 'data\\k.wav' #0.100
sound_l = 'data\\l.wav' #0.200
sound_m = 'data\\m.wav' #0.300
sound_n = 'data\\n.wav' #0.400
sound_o = 'data\\o.wav' #0.500
sound_p = 'data\\p.wav' #0.600
sound_q = 'data\\q.wav' #0.700
sound_r = 'data\\r.wav' #0.800
sound_s = 'data\\s.wav' #0.900
sound_t = 'data\\t.wav' #1.000

sound_negative = 'data\\x.wav' #negative operation
sound_normal = 'data\\y.wav' #noraml operation
sound_error = 'data\\z.wav' #error

# while loop, data from MITUTOYO degimatic guage
def loop(q):
    while True:

        value = mitutoyo()
        q.put(value)
        dt = datetime.datetime.now()
        dt2 = dt.strftime('%H:%M:%S:%M')
        print(dt2 + " " + value)
        time.sleep(float(sleep_loop)) # 0.1s is a trial value, 0.3 is more secure

# Alarm
def alarm(q):
    while True:

        time.sleep(int(sleep_alarm))

        value = q.get()

        if float(value) == -100: # for the error: device is in a problem
            while True:
                playsound(sound_error)

        if float(value) < 0.000:
            playsound(sound_negative)

        if 0.000 < float(value) <= 0.004:
            playsound(sound_normal)

        if 0.005 == float(value):
            playsound(sound_a)

        if 0.005 < float(value) <= 0.009:
            playsound(sound_normal)

        if 0.010 <= float(value) <= 0.019:
            playsound(sound_b)

        if 0.020 <= float(value) <= 0.029:
            playsound(sound_c)

        if 0.030 <= float(value) <= 0.039:
            playsound(sound_d)

        if 0.040 <= float(value) <= 0.049:
            playsound(sound_e)

        if 0.050 <= float(value) <= 0.059:
            playsound(sound_f)

        if 0.060 <= float(value) <= 0.069:
            playsound(sound_g)

        if 0.070 <= float(value) <= 0.079:
            playsound(sound_h)

        if 0.080 <= float(value) <= 0.089:
            playsound(sound_i)

        if 0.090 <= float(value) <= 0.099:
            playsound(sound_j)

        if 0.10 <= float(value) <= 0.19:
            playsound(sound_k)

        if 0.20 <= float(value) <= 0.29:
            playsound(sound_l)

        if 0.30 <= float(value) <= 0.39:
            playsound(sound_m)

        if 0.40 <= float(value) <= 0.49:
            playsound(sound_n)

        if 0.50 <= float(value) <= 0.59:
            playsound(sound_o)

        if 0.60 <= float(value) <= 0.69:
            playsound(sound_p)

        if 0.70 <= float(value) <= 0.79:
            playsound(sound_q)

        if 0.80 <= float(value) <= 0.89:
            playsound(sound_r)

        if 0.90 <= float(value) <= 0.99:
            playsound(sound_s)

        if 1.0 <= float(value):
            playsound(sound_t)

# data logger from MITUTOYO device
def logger(q):

    # read 管理番号 from the txt file
    f = open(filepath_txt, "r")
    filepath_csv = f.readline()

    # csv file: strain change history
    while True:
        time.sleep(int(sleep_logger))

        dt = datetime.datetime.now()
        dt1 = dt.strftime('%Y/%m/%d')
        dt2 = dt.strftime('%H:%M:%S')
        value = q.get()
        f = open(filepath_csv, "a")
        writer =csv.writer(f, lineterminator='\n')

        if float(value) == -100:
            value = "ダイヤルゲージ異常"
            writer.writerow([dt1, dt2, value])
            f.close()
        else:
            writer.writerow([dt1, dt2, value])
            f.close()

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
        self.wo01.resize(400*0.8, 80)
        self.wo01.setPlaceholderText(' 作業用番号') # 透かしで表示
        self.wo01.setStyleSheet("color: black; font: 20pt Arial; border-color: black; "
                                "border-style:solid; border-width: 1.5px; border-radius:10px") # 文字の大きさなど


        self.wk01 = QComboBox(self)
        self.wk01.addItem(name00)
        self.wk01.addItem(name01)
        self.wk01.addItem(name02)
        self.wk01.addItem(name03)
        self.wk01.addItem(name04)
        self.wk01.addItem(name05)
        self.wk01.addItem(name06)
        self.wk01.addItem(name07)
        self.wk01.addItem(name08)
        self.wk01.addItem(name09)
        self.wk01.addItem(name10)
        self.wk01.move(390,10)
        self.wk01.resize(400*0.8, 80)
        self.wk01.setStyleSheet("color: black; font: 20pt Arial; border-color: white; "
                                "border-style:solid; border-width: 1.5px; border-radius:10px") # 文字の大きさなど

        self.btn01 = QPushButton("計測開始", self)
        self.btn01.move(750, 10)
        self.btn01.resize(400*0.8, 80)
        self.btn01.setStyleSheet("color: black; font: 20pt Arial; border-color: black; "
                                 "border-style:solid; border-width: 1.5px; border-radius:10px") # 文字の大きさなど
        self.btn01.clicked.connect(self.header)

        self.setGeometry(200, 200, 300, 200)

        self.label = QLabel(self)
        self.label.move(0, 100)
        self.label.resize(1366, 400)

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

        # to change the file name if the self.wo01.text() is in blank
        if "\.csv" in self.filepath_csv:
            dt = datetime.datetime.now()
            dt1 = dt.strftime('%Y%m%d')
            dt2 = dt.strftime('%H%M%S')
            self.filepath_csv =str(self.filepath_csv).replace('.csv', '')
            filename = str(dt1) + str(dt2) + ".csv"
            self.filepath_csv = filepath_csv + filename

        else:
            pass

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

        # multiprocessing p2 start
        p2.start()

    #@pyqtSlot(str)
    def print_data(self, data):
        #self.statusBar().showMessage(data)

        #print(type(data))
        #if 0 <= float(data) < 0.045:
            #self.label.setText("  " + data)
            #self.styleA = "QWidget{background-color:%s; font: 300pt Arial}" % ("green")
            #self.label.setStyleSheet(self.styleA)

        #elif 0.045 <= float(data) <= 0.049:
            #self.label.setText("  " + data)
            #self.styleA = "QWidget{background-color:%s; font: 300pt Arial}" % ("yellow")
            #self.label.setStyleSheet(self.styleA)

        #elif 0.050 <= float(data) < 100:
            #self.label.setText("  " + data)
            #self.styleA = "QWidget{background-color:%s; font: 300pt Arial}" % ("brown")
            #self.label.setStyleSheet(self.styleA)



        if -100 <= float(data) < 0:
            self.label.setText(" " + data)
            self.styleA = "QWidget{font: 250pt}"
            self.label.setStyleSheet(self.styleA)

        if 0 <= float(data) < 10:
            self.label.setText("  " + data)
            self.styleA = "QWidget{font: 250pt}"
            self.label.setStyleSheet(self.styleA)

        if 10 <= float(data) < 100:
            self.label.setText(" " + data)
            self.styleA = "QWidget{font: 250pt}"
            self.label.setStyleSheet(self.styleA)

        elif float(data) == -100:
            data = " 異常発生"
            self.label.setText(data)
            self.styleA = "QWidget{color:%s; font: 180pt Arial}" % ("brown")
            self.label.setStyleSheet(self.styleA)


if __name__ == "__main__":

    q = Queue()

    with pool.Pool(processes=3) as p:

        #multiprocessing
        p0 = p.Process(target=loop, args=(q, ), daemon=True)
        p1 = p.Process(target=alarm, args=(q, ), daemon=True)
        p2 = p.Process(target=logger, args=(q, ), daemon=True)

        p0.start()
        p1.start()

    # Main process
    app = QApplication(sys.argv)
    mywindow = MyWindow(q)
    mywindow.setWindowTitle("熱変形量監視ソフト Version 0.0.0") # windowのtitle
    #mywindow.showFullScreen()

    scr_w,scr_h= pag.size() #LCD resolution

    mywindow.setFixedSize(scr_w*0.8, scr_h*0.8)  # windows size based on LCD resolution
    mywindow.show()
    app.exec()