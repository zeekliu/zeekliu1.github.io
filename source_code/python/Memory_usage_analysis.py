from os import stat, listdir
from os.path import isfile, isdir, join, split
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from threading import Thread
from sys import argv, exit
from optparse import OptionParser
import sip
parser = OptionParser()
options, args = parser.parse_args()
sizes = []
tot = 0
sort = True
maximum = 0

def get_size(path):
    global sizes, tot, sort, maximum
    if isfile(path):
        size = stat(path).st_size
        if sort:
            lo = 0
            hi = len(sizes)
            mid = (lo + hi) // 2
            while mid != lo:
                if sizes[mid][1] < size:
                    hi = mid
                elif sizes[mid][1] > size:
                    lo = mid
                else: break
                mid = (lo + hi) // 2
            sizes.insert(mid + 1, (path, size))
        else:
            sizes.append((path, size))
            if size > maximum: maximum = size
            
        tot += size
    if isdir(path):
        try:
            file_list = listdir(path)
        except PermissionError:
            window.label.setText('Get size failed: %s'%path)
            return
        for file in file_list:
            filepath = join(path, file)
            try:
                get_size(filepath)
            except PermissionError:
                window.label.setText('Get size failed: %s'%filepath)
            
def get_target(path):
    exec('''
def target():
    global sizes, sort, maximum
    global window
    get_size(%r)
    if sort:
        size = sizes[0][1]
        lo = 0
        hi = len(sizes)
        mid = (lo + hi) // 2
        while mid != lo:
            if sizes[mid][1] < size:
                hi = mid
            elif sizes[mid][1] > size:
                lo = mid
            else: break
            mid = (lo + hi) // 2
        sizes.insert(mid + 1, sizes.pop(0))
        maximum = sizes[0][1]
    window.widget.done()'''%path)
    return locals()['target']

class Window(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle('Memory usage analysis')
        icon_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x000\x00\x00\x000\x08\x06\x00\x00\x00W\x02\xf9\x87\x00\x00\x01\x80IDATx\xda\xed\x98\xcbJ\xc3P\x10\x86\x83"\x8a\xa2\x88\xa2\xf8\xa8\xde\xef]\x08]\x0b\x01\x97\x82\xf8\x1a"\xbeB\x9b\xb8\xcf\x03\xe4\x9el\xc6N\xb1r\n\x92\xcc\xc9L\xc8)\xcc\x0f?\xed\xf2\xfb\xe6?\x9b\xd6\xf34\x1a\x8dF\xa3\xf9\xcd\xe8i\x0c\xabP\xa7\x05>>\xbf\xe6m\xfa\xee\xb4\xc0\xeb\xdb\xfb\xbcM\xdf\x1b\x05\xa2(r\xba\xad\x02u];\xd1\xaa\xaa\x96Z\x96\xe5\xbc\xec\x05\x86\x84\x17\x13\xf0N\'\xecv\x81\'\x0b<\xfb/\x7f\x9ffM\x81\x93\xd17\x1c?\x86p\xf4\x10\xc2\xe1}\x08\x07w!\xec\xdf\x06\xb0w\x13\xc0\xee\xac;\xd7\x01l_\x05\xb0u9\x85\xcdY7.\xa6\xb0~>\x81\xb5\xb3e\x01\xdf\xf7IE\xf8\xa2(\xe4\x16\xe0\xc0\xff\xb7@\xdb\xe5\x11^T\x80\x03\xdfe\x01+\x01\xca\x13\xe2\xc0\x9b\x02\xd4\xcb\x8b/\xc0\x81_\x08 p/\x0bP\x048\xf0X\xdb\xcbc\xf3<\x97{B\x1cxS\x80\xba\x00\xc2\x93\x05(\x0bp\xe0M\x01\xea\xe5\xc5\x058\xf0\x0b\x01\x04\xeee\x01\xca\x13\xe2\xc0cm/\x8f\xcd\xb2Ln\x01\x0e\xbc)@]\x00\xe1E\x058\xf0\xa6\x00\xf5\xf2V\x02\x94\'\xc4\x81_\x08 \xec`\x0bp\xe0\xb1\xb6\x97\xc7\xa6i*\'\xc0\x817\x05\xda.n\xc2\x8b\npk{yg\x05l\xe0\x9d\x13\xb0\x85O\x92\xc4\x1d\x81.\xf0\xce\nP\xe1\xc5\x04\xba\xfe\x18\xe9\xfalz\x11\x18\x02^L`(\xf88\x8e\xdd\xffo\x94\xf5\xef\xb4F\xa3\xd1h4\xab\x96\x1f>4\xe9\xef\xf1\x0fT\x85\x00\x00\x00\x00IEND\xaeB`\x82'
        icon_pixmap = QtGui.QPixmap()
        icon_pixmap.loadFromData(icon_bytes)
        self.setWindowIcon(QtGui.QIcon(icon_pixmap))
                
        self.widget = Widget(self)
        self.setCentralWidget(self.widget)

        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.label = QtGui.QLabel('', self.statusbar)
        self.label.resize(2000, self.statusbar.height())
        self.size_label = QtGui.QLabel('')
        self.statusbar.addPermanentWidget(self.size_label)

        self.menubar = QtGui.QMenuBar(self)
        self.setMenuBar(self.menubar)
        self.file = QtGui.QMenu("&File", self.menubar)
        self.menubar.addMenu(self.file)
        
        self.load = QtGui.QAction('Choose a directory', self.file)
        self.load.triggered.connect(self.widget.load)
        self.file.addAction(self.load)
        
        self.sort = QtGui.QAction('Automatic sorting', self.file)
        self.sort.setCheckable(True)
        self.sort.trigger()
        self.sort.triggered.connect(self.sort_triggered)
        self.file.addAction(self.sort)

        desktop = QtGui.QApplication.desktop()
        w = round(200 / desktop.widthMM() * desktop.width())
        h = round(36 / desktop.heightMM() * desktop.height())
        self.resize(w, h)
        
        self.show()

    def sort_triggered(self):
        global sort
        sort = not sort
        
    def resizeEvent(self, event):
        self.label.resize(self.width(), self.statusbar.height())
        self.size_label.resize(self.width(), self.statusbar.height())
        
    def closeEvent(self, event):
        self.widget.thread.join()
        event.accept()
        
class Widget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        if args:
            self.dir_path = args[0]
            if not isdir(self.dir_path): self.dir_path = split(self.dir_path)[0]
            if not isdir(self.dir_path): exit(0)
        else:
            self.dir_path = str(QtGui.QFileDialog.getExistingDirectory(self, 'Choose a directory', 'C:\\'))
            if not self.dir_path: exit(0)
        self.thread = Thread(target = get_target(self.dir_path))
        self.update_timer = self.startTimer(500)
        self.xs = []
        self.t = 0
        self.cur = QtGui.QCursor()
        self.fontSize = 9
        
    def format_size(self, size):
        if size < 1024:
            return '%i B'%size
        if size < 1048576:
            return '%.1f KB'%(size / 1024)
        if size < 1073741824:
            return '%.1f MB'%(size / 1048576)
        if size < 1099511627776:
            return '%.1f GB'%(size / 1073741824)
        return '%.1f TB'%(size / 1099511627776)
        
    def done(self):
        self.parent().setWindowTitle('Memory usage analysis - ' + self.dir_path)

        self.parent().size_label.setText('Total size: ' + self.format_size(tot))
        
        trayicon = QtGui.QSystemTrayIcon(
            QtGui.QIcon(
                QtGui.QPixmap.fromImage(QtGui.QImage(1, 1, QtGui.QImage.Format_Mono))
                )
            )
        trayicon.show()
        trayicon.showMessage("Memory usage analysis", "Analyse done!", QtGui.QSystemTrayIcon.NoIcon)
        trayicon.hide()
        
        self.update_xs()
        self.update()
        
    def load(self):
        global sizes, tot
        dir_path = str(QtGui.QFileDialog.getExistingDirectory(self, 'Choose a directory', 'C:\\'))
        if dir_path:
            self.parent().setWindowTitle('Memory usage analysis')
            self.parent().size_label.setText('')
            self.parent().label.setText('')
            self.dir_path = dir_path
            sizes.clear()
            tot = 0
            self.xs.clear()
            self.thread.join()
            del self.thread
            self.thread = Thread(target = get_target(self.dir_path))
            self.thread.start()
        
    def update_xs(self):
        self.xs.clear()
        w = self.width()
        s = 0
        for i in range(len(sizes)):
            x = w * s / tot
            self.xs.append([x, sizes[i][1] / tot * 100])
            s += sizes[i][1]
            
    def resizeEvent(self, event):
        self.update_xs()
        
    def paintEvent(self, event):
        w, h = self.width(), self.height()
        p = QtGui.QPainter(self)
        if self.thread.isAlive():
            p.setFont(QtGui.QFont('SimSum', 40))
            fm = p.fontMetrics()
            text = 'Loading' + '.' * (self.t + 1) + ' ' * (3 - self.t) + self.dir_path
            p.drawText((w - fm.width(text)) / 2, (h - fm.height()) / 2 + fm.ascent(), text)
        else:
            p.setFont(QtGui.QFont('SimSum', self.fontSize))
            fm = p.fontMetrics()
            
            for i in range(len(sizes)):
                label = sizes[i][0]
                #print(sizes[i][0])
                hue = round(240 * (1 - sizes[i][1] / maximum))
                #print(hue)
                col = QtGui.QColor.fromHsl(hue, 255, 128)
                gray = (col.red()*77+col.green()*151+col.blue()*28)>>8
                p.setBrush(col)
                left = self.xs[i][0]
                try: width = self.xs[i+1][0] - left
                except IndexError: width = w - left
                p.setPen(QtCore.Qt.black)
                p.drawRect(left, 0, width, h)
                if width >= fm.width(' '):
                    if gray > 96:
                        p.setPen(QtCore.Qt.black)
                    else:
                        p.setPen(QtCore.Qt.white)
                    s = [""]
                    text = split(label)[1] + "\n\n%1.2f%%"%(self.xs[i][1]) + '\n\n' + self.format_size(sizes[i][1])
                    for c in text:
                        if c == '\n': s.append(""); continue
                        if fm.width(s[-1] + c) > width:
                            s.append("")
                        s[-1] += c
                    lines = len(s)
                    for line in range(lines):
                        p.drawText(left + width / 2 - fm.width(s[line]) / 2, h / 2 - (lines / 2 - line) * fm.height() + fm.ascent(), s[line])
                        
    def mousePressEvent(self, event):
        self.update()
        
    def timerEvent(self, event):
        if event.timerId() == self.update_timer:
            if self.thread.isAlive():
                self.t += 1
                if self.t >= 3: self.t = 0
                self.update()
            else:
                if self.xs:
                    pos = self.mapFromGlobal(self.cur.pos())
                    x, y = pos.x(), pos.y()
                    if 0 <= x < self.width() and 0 <= y < self.height():
                        lo = 0
                        hi = len(self.xs)
                        mid = (lo + hi) // 2
                        while (hi - lo) > 1:
                            if self.xs[mid][0] < x:
                                lo = mid
                            elif self.xs[mid][0] > x:
                                hi = mid
                            else: break
                            mid = (lo + hi) // 2
                        #self.setToolTip('%s\n%1.2f%%\n%s'%(split(sizes[mid][0])[1], self.xs[mid][1], self.format_size(sizes[mid][1])))
                        self.parent().label.setText(sizes[mid][0])
                        self.parent().size_label.setText('Size: %s  %1.2f%%'%(self.format_size(sizes[mid][1]), self.xs[mid][1]))
                    else:
                        if self.parent().label.text():
                            #self.setToolTip('')
                            self.parent().label.setText('')
                            self.parent().size_label.setText('Total size: ' + self.format_size(tot))
                            
    def wheelEvent(self, event):
        fontSize = self.fontSize * 1.1 ** (event.delta() / 120)
        if 1 <= fontSize <= 50:
            self.fontSize = fontSize
        self.update()
    
if __name__ == '__main__':
    app = QtGui.QApplication(argv)
    window = Window()
    window.widget.thread.start()
    app.exec_()
