from PyQt5.QtCore import QMutex, QWaitCondition, QThread, QMetaObject, pyqtSlot
# from PySide2.QtCore import QMutex, QWaitCondition, QThread, QMetaObject, Slot

class WorkerThread(QThread):
    def __init__(self):
        super().__init__()
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()
        self.running = False

    def run(self):
        self.running = True
        i = 0
        while self.running:
            self.mutex.lock()
            i+=1
            print(i)
            # Do some work here...
            print("lock")
            print(self.running)
            # Wait for the wait_condition to be signaled
            self.wait_condition.wait(self.mutex)
            print("alive")
            self.mutex.unlock()
            print("unlock")

    def stop(self):
        # Invoke the stop_slot in the worker thread
        QMetaObject.invokeMethod(self, 'stop_slot')

    @pyqtSlot()
    def stop_slot(self):
        self.mutex.lock()
        self.running = False
        self.wait_condition.wakeOne()
        self.mutex.unlock()
        print("stopping")

    def start_work(self):
        # Invoke the start_slot in the worker thread
        QMetaObject.invokeMethod(self, 'start_slot')

    @pyqtSlot()
    def start_slot(self):
        self.mutex.lock()
        self.running = True
        self.wait_condition.wakeOne()
        self.mutex.unlock()
        self.run()

# from PySide2.QtCore import QTimer, QCoreApplication
from PyQt5.QtCore import QTimer, QCoreApplication
import sys, time

def main():
    app = QCoreApplication(sys.argv)
    worker_thread = WorkerThread()
    worker_thread.start()
    # QTimer.singleShot(1000, worker_thread.stop)
    # print("set shot")
    # time.sleep(3)
    print("set start")
    # QTimer.singleShot(1000, worker_thread.start_work)
    
    # time.sleep(3)
    # QTimer.singleShot(2000, worker_thread.stop)
    # print("set shot2")
    # time.sleep(3)
    print("set start2")
    # QTimer.singleShot(2000, worker_thread.start_work)
    QTimer.singleShot(3000, worker_thread.stop)
    QTimer.singleShot(5000, worker_thread.start_work)
    app.exec_()

if __name__ == '__main__':
    main()