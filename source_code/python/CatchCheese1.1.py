from PyQt4 import QtGui, QtCore
from sys import argv
from math import sin, cos, pi, radians
from random import randint, choice
from os import path
import sip

class Window(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setMinimumSize(640, 480)
        self.fullscreen = False
        self.setWindowTitle('Catch Cheese')
        self.setWindowIcon(QtGui.QIcon('cheese.png'))
        
        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.timeout.connect(self.update)
        self.updateTimer.start(10)
        
        self.initPixTimer = QtCore.QTimer(self)
        self.initPixTimer.timeout.connect(self.initPix)
        self.initPixTimer.start(7.5)
        
        self.moveTimerId = self.startTimer(10)
        
        self.centerRect = QtCore.QRect(0, 0, 640, 480)
        self.background = QtGui.QImage('background.png')
        self.mousePic = QtGui.QImage('mouse.png')
        self.mousetrap = QtGui.QImage('mousetrap.png')
        self.mousetrapPic = QtGui.QImage('mousetrap.png')
        self.cheesePic = QtGui.QImage('cheese.png')
        self.sounds = [QtGui.QSound('eat.wav')]
        
        self.pix = QtGui.QPixmap(480, 360)
        self.pix.fill(QtGui.QColor(0, 255, 255))
        self.initArgs()
        self.mouseHitPoints = [[-15, -5], [-15, 2], [-13, -8], [-13, 4], [-12, -10],
                               [-12, 6], [-10, -11], [-10, 7], [-8, -12], [-8, 8],
                               [-8, -17], [-8, 14], [-6, -17], [-6, 13], [-4, -17],
                               [-4, 15], [-2, -17], [-3, 13], [-2, 12], [-2, -14],
                               [-2, 12], [-1, -12], [-1, 8], [1, -11], [1, 8],
                               [2, -11], [2, 8], [3, -15], [5, -16], [4, 9],
                               [5, 11], [5, 13], [7, -15], [7, 13], [8, -16],
                               [9, 13], [9, -14], [9, 12], [10, -12], [10, 11],
                               [12, -12], [12, 12], [13, -12], [13, 12], [15, -12],
                               [15, 12], [17, -12], [17, 11], [18, -10], [18, 10],
                               [18, -8], [18, 8], [19, 7], [20, -8], [21, 7],
                               [22, -8], [22, 6], [23, -8], [24, 5], [25, -7],
                               [26, -7], [25, 5], [27, -5], [27, 4], [28, -3],
                               [28, 2], [29, -2], [29, -1], [29, 0], [29, 1]]

        p = QtGui.QPainter()
        p.begin(self.pix)
        p.drawImage(0, 0, self.background)
        p.end()

        self.tips = []

        self.show()
    def initArgs(self):
        self.p = 1.0
        self.resizeEvent(self)
        self.score = 0
        self.cheese = [False] * 2
        self.mousePicDirection = 180
        self.mousePicDirection_to = 180
        self.die = False
        self.died_time = 0
        self.pause = False
        self.end = False
        self.time = 12000
        self.mouseDirection = None
        self.mouseSpeed = 1.5
        self.mousePos = [30, 30]
        self.mousetrapPos = [30 + randint(2, 7) * 60, 30 + randint(0, 5) * 60]
        self.mousetrapDirection = randint(0, 3)
        self.trapMove()
        self.keys = set()
        x = randint(0, 7)
        y = randint(0, 5)
        self.cheesePos = [30 + x * 60, 30 + y * 60]
    def trapMove(self):
        tx, ty = int(self.mousetrapPos[0] / 60), int(self.mousetrapPos[1] / 60)
        mx, my = int(self.mousePos[0] / 60), int(self.mousePos[1] / 60)
        d = set()
        for i in range(4):
            sx, sy = [[0, -1], [1, 0], [0, 1], [-1, 0]][i]
            nx, ny = tx + sx, ty + sy
            if 0 <= nx <= 7 and 0 <= ny <= 5 and \
               not self.hit_wall(30 + (tx + nx) / 2 * 60,
                                 30 + (ty + ny) / 2 * 60): d.add(i)
        if len(d) > 1:
            d -= {(self.mousetrapDirection + 2) % 4}
        if d: self.mousetrapDirection = choice(list(d))
    def initMouseDirection(self):
        up = []
        left = []
        for key in self.keys:
            if key == QtCore.Qt.Key_Up:
                up.append(1)
            elif key == QtCore.Qt.Key_Down:
                up.append(-1)
            elif key == QtCore.Qt.Key_Left:
                left.append(1)
            elif key == QtCore.Qt.Key_Right:
                left.append(-1)
        if not up and not left: left_ = up_ = 0
        elif not up:
            left_ = int(sum(left) / len(left))
            up_ = 0
        elif not left:
            up_ = int(sum(up) / len(up))
            left_ = 0
        else:
            left_ = int(sum(left) / len(left))
            up_ = int(sum(up) / len(up))
        if left_ or up_:
            self.mousePicDirection_to = [[0, 1],
                                         [-1, 1],
                                         [-1, 0],
                                         [-1, -1],
                                         [0, -1],
                                         [1, -1],
                                         [1, 0],
                                         [1, 1],
                                         ].index([left_, up_]) * 45
            self.mouseDirection = self.mousePicDirection_to
        else:
            self.mouseDirection = None
    def hit_wall(self, x, y):
        return (QtCore.QPoint(x, y) not in QtCore.QRect(2, 2, 478, 358)) | self.background.pixel(x, y) >= 16777216
    def move(self):
        if not (self.die or self.end):
            if [(self.mousetrapPos[0] - 30) % 60, (self.mousetrapPos[1] - 30) % 60] == [0, 0]:
                self.trapMove()
            dx, dy = [0, 1, 0, -1][self.mousetrapDirection], [-1, 0, 1, 0][self.mousetrapDirection]
            x, y = self.mousetrapPos[0] + dx * 29, self.mousetrapPos[1] + dy * 29
            if self.time == 2000:
                self.tips.append(['The speed of mousetrap increase to 150px/s!', 1000, QtCore.Qt.red])
            elif self.time == 1000:
                self.tips.append(['The speed of mousetrap increase to 200px/s!', 1000, QtCore.Qt.red])
                self.tips.append(["Be careful! It's faster than your mouse!", 1000, QtCore.Qt.red])
            elif self.time < 1000:
                self.mousetrapPos[0] = (self.mousetrapPos[0] + dx * 2) // 2 * 2
                self.mousetrapPos[1] = (self.mousetrapPos[1] + dy * 2) // 2 * 2
            elif self.time < 2000:
                self.mousetrapPos[0] = (self.mousetrapPos[0] + dx * 1.5) // 1.5 * 1.5
                self.mousetrapPos[1] = (self.mousetrapPos[1] + dy * 1.5) // 1.5 * 1.5
            else:
                self.mousetrapPos[0] += dx
                self.mousetrapPos[1] += dy
            
            sqrt_0_5 = 0.5 ** 0.5

            dx, dy = sin(radians(self.mousePicDirection)), -cos(radians(self.mousePicDirection))
            nx = self.mousePos[0] + dx * self.mouseSpeed
            ny = self.mousePos[1] + dy * self.mouseSpeed
            hit = False
            for point in self.mouseHitPoints:
                p = point[0] + point[1] * 1j
                p *= dx + dy * 1j
                x, y = round(nx + p.real), round(ny + p.imag)
                if self.hit_wall(x, y) and self.mouseDirection != None:
                    hit = True
                pixnel_x, pixnel_y = x - self.cheesePos[0] + 30, y - self.cheesePos[1] + 30
                if 0 <= pixnel_x <= self.cheesePic.width() and\
                   0 <= pixnel_y <= self.cheesePic.height(): p = self.cheesePic.pixel(pixnel_x, pixnel_y)
                else: p = 0
                if p >= 16777216:
                    self.score += 1
                    self.tips.append(['score + 1', 1000, QtCore.Qt.darkGreen])
                    self.time += 100
                    self.sounds[0].play()
                    self.cheesePos = [30 + randint(0, 7) * 60, 30 + randint(0, 5) * 60]
                if QtCore.QPoint(x, y) in QtCore.QRect(round(self.mousetrapPos[0] - self.mousetrapPic.width() / 2),
                                                       round(self.mousetrapPos[1] - self.mousetrapPic.height() / 2),
                                                       self.mousetrapPic.width(),
                                                       self.mousetrapPic.height()):
                    self.die = self.end = True
                    if not self.die:
                        self.tips.append(['You died!', 1000, QtCore.Qt.red])
            if not hit and self.mouseDirection != None:
                self.mousePos = [nx, ny]
                
            diff = abs(self.mousePicDirection - self.mousePicDirection_to)
            s = 7.5
            if min(diff, 360 - diff) > (0.5 * s):
                diff1 = self.mousePicDirection_to - self.mousePicDirection
                if diff1 >= 0:
                    diff2 = -360 + diff1
                else:
                    diff2 = 360 + diff1
                i = randint(1, 2)
                diff = eval('{abs(diff%i) : diff%i, abs(diff%i) : diff%i}'%(i, i, 3 - i, 3 - i))[min(abs(diff1), abs(diff2))]
                self.mousePicDirection += round(diff / s)
                self.mousePicDirection %= 360
            else:
                self.mousePicDirection = self.mousePicDirection_to
            self.time -= 1
            if self.time <= 0:
                self.end = True
                self.tips.append(['You won!', 1000, QtCore.Qt.darkGreen])
                
        else:
            self.died_time += 1
        
    def keyPressEvent(self, event):
        self.keys.add(event.key())
        self.initMouseDirection()
    def keyReleaseEvent(self, event):
        try: self.keys.remove(event.key()); self.initMouseDirection()
        except: pass
    def resizeEvent(self, event):
        size = event.size()
        w, h = size.width(), size.height()
        self.p = min(w / 960, h / 720)
        self.centerRect = QtCore.QRect(w / 2 - 480 * self.p, h / 2 - 360 * self.p, 960 * self.p, 720 * self.p)
    def initPix(self):
        pass
    def paintEvent(self, event):
        self.pix = QtGui.QPixmap(480, 360)
        self.pix.fill(QtGui.QColor(0, 255, 255))
        w, h = self.pix.width(), self.pix.height()
        p = QtGui.QPainter()
        p.begin(self.pix)
        p.drawImage(0, 0, self.background)
        mousePic = self.mousePic
        tr = QtGui.QTransform()
        tr = tr.rotate(-90 + self.mousePicDirection)
        mousePic = mousePic.transformed(tr, QtCore.Qt.SmoothTransformation)
        p.drawImage(
            round(self.mousePos[0] - mousePic.width() / 2),
            round(self.mousePos[1] - mousePic.height() / 2),
            mousePic
                    )
        tr = QtGui.QTransform()
        tr = tr.rotate(90 + self.mousetrapDirection * 90)
        self.mousetrapPic = self.mousetrap.transformed(tr, QtCore.Qt.SmoothTransformation)
        rect = QtCore.QRect(round(self.mousetrapPos[0] - self.mousetrapPic.width() / 2),
                            round(self.mousetrapPos[1] - self.mousetrapPic.height() / 2),
                            self.mousetrapPic.width(),
                            self.mousetrapPic.height())
        p.drawImage(rect, self.mousetrapPic)
        
        p.drawImage(self.cheesePos[0] - 30, self.cheesePos[1] - 30, self.cheesePic)

        f = QtGui.QFont("Arial Black")
        f.setPixelSize(20)
        p.setFont(f)
        metrics = p.fontMetrics()
        p.drawText(10, 10 + metrics.ascent(), 'score : ' + str(self.score))
        p.drawText(10, 10 + metrics.ascent() + metrics.height(), 'time remaining : %i'%(self.time / 100))
        
        i = len(self.tips)
        for tip in self.tips:
            col = QtGui.QColor(tip[2])
            col.setAlpha(min(255, tip[1]))
            p.setPen(QtGui.QPen(col))
            p.drawText(10, 350 + metrics.ascent() - metrics.height() * i, tip[0])
            i -= 1
        for t in self.tips:
            t[1] -= 1
            if t[1] <= 0:
                self.tips.remove(t)

        
        f = QtGui.QFont("Arial Black")
        f.setPixelSize(34)
        f.setBold(True)
        p.setFont(f)
        metrics = p.fontMetrics()
        if self.die or self.end:
            p.fillRect(QtCore.QRect(QtCore.QPoint(), self.pix.size()), QtGui.QColor(self.die * 255, 255 - self.die * 255, 0, 128))
            s = ['Time out!', 'You died!'][self.die]
            p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
            p.drawText(w / 2 - metrics.width(s) / 2,
                       h / 3 * 0.8 + metrics.ascent(),
                       s)

            f.setPixelSize(25)
            p.setFont(f)
            metrics = p.fontMetrics()
            s = 'score : %i'%self.score
            p.setPen(QtGui.QPen(QtGui.QColor(255 - self.die * 255, 255, self.die * 255)))
            p.drawText(w / 2 - metrics.width(s) / 2,
                       h / 3 * 1.1 + metrics.ascent(),
                       s)

            p.setPen(QtCore.Qt.NoPen)
            p.setBrush(QtGui.QBrush([QtCore.Qt.red, QtCore.Qt.green][self.die]))
            p.drawRect(w / 2 - 150,
                       h / 3 * 1.5,
                       (300 - (self.died_time / 400 * 300)),
                       30)
            
            p.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.white), 2))
            p.setBrush(QtCore.Qt.NoBrush)
            p.drawRect(w / 2 - 150,
                       h / 3 * 1.5,
                       300,
                       30)
            
            f.setPixelSize(20)
            p.setFont(f)
            metrics = p.fontMetrics()
            s = 'play again (%is)'%(4 - int(self.died_time / 100))
            p.setPen(QtGui.QPen(QtGui.QColor(self.die * 255, 128 - self.die * 128, 0)))
            p.drawText(w / 2 - metrics.width(s) / 2,
                       h / 3 * 1.5 + 15 - metrics.height() / 2 + metrics.ascent(),
                       s)

            if self.died_time >= 400:
                self.initArgs()
                for i in range(len(self.tips)):
                    self.tips[i][1] = min(self.tips[i][1], 255)
        p.end()
        
        p.begin(self)
        p.drawPixmap(self.centerRect, self.pix)
        p.end()
    def timerEvent(self, event):
        if event.timerId() == self.moveTimerId:
            self.move()
            

if __name__ == '__main__':
    app = QtGui.QApplication(argv)
    window = Window()
    app.exec_()
