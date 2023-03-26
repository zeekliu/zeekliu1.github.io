from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from sys import argv
import sip
from optparse import OptionParser
from os.path import split, abspath, getsize

parser = OptionParser()
(options, args) = parser.parse_args()

class chess_piece:
    def __init__(self, chessboard, color, type, x, y):
        self.pos = [max(0, min(8, x)), max(0, min(9, y))]
        self.type = max(0, min(6, type))
        self.color = max(0, min(1, color))#0:红 1:黑
        self.chessboard = chessboard
        '''
        将:0
        士:1
        相:2
        马:3
        车:4
        炮:5
        卒:6
        '''
        
    def get_chinese_name(self):
        if self.color:
            return ['將', '士', '象', '馬', '車', '砲', '卒'][self.type]
        return ['帥', '仕', '相', '馬', '車', '炮', '兵'][self.type]
    
    def __bool__(self): return True

    def get_movements(self):
        movements = set()
        for x in range(9):
            for y in range(10):
                dx = x - self.pos[0]
                dy = y - self.pos[1]
                c = self.chessboard.get_chess_piece(x, y)
                if c != None:
                    if c.color == self.color: continue
                if 0 <= x <= 8 and 0 <= y <= 9:
                    if self.type == 0:
                        if dx == 0 and bool(c) and c.type == 0:
                            b = True
                            step = dy // abs(dy)
                            for ny in range(self.pos[1] + step, y, step):
                                b &= not bool(self.chessboard.get_chess_piece(x, ny))
                            if b: movements |= {(x, y)}
                        elif [dx, dy] in [[0, 1], [1, 0], [0, -1], [-1, 0]] and 3 <= x <= 5 and (7 - 7 * self.color) <= y <= (9 - 7 * self.color):
                            movements |= {(x, y)}
                    elif self.type == 1:
                        if [dx, dy] in [[1, 1], [1, -1], [-1, 1], [-1, -1]] and 3 <= x <= 5 and (7 - 7 * self.color) <= y <= (9 - 7 * self.color):
                            movements |= {(x, y)}
                    elif self.type == 2:
                        if [dx, dy] in [[2, 2], [2, -2], [-2, 2], [-2, -2]] and not self.chessboard.get_chess_piece(x - dx / 2, y - dy / 2) and (5 - 5 * self.color) <= y <= (9 - 5 * self.color):
                            movements |= {(x, y)}
                    elif self.type == 3:
                        if [dx, dy] in [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [-1, 2], [1, -2], [-1, -2]]:
                            if abs(dx) > abs(dy): nx, ny = (self.pos[0] + dx // abs(dx)), self.pos[1]
                            elif abs(dx) < abs(dy): nx, ny = self.pos[0], (self.pos[1] + dy // abs(dy))
                            if not self.chessboard.get_chess_piece(nx, ny):
                                movements |= {(x, y)}
                    elif self.type == 4:
                        b = True
                        if dx == 0:
                            step = dy // abs(dy)
                            for ny in range(self.pos[1] + step, y, step):
                                b &= not bool(self.chessboard.get_chess_piece(x, ny))
                        elif dy == 0:
                            step = dx // abs(dx)
                            for nx in range(self.pos[0] + step, x, step):
                                b &= not bool(self.chessboard.get_chess_piece(nx, y))
                        else: b = False
                        if b: movements |= {(x, y)}
                    elif self.type == 5:
                        pieces = 0
                        if dx == 0:
                            step = dy // abs(dy)
                            for ny in range(self.pos[1] + step, y, step):
                                pieces += bool(self.chessboard.get_chess_piece(x, ny))
                        elif dy == 0:
                            step = dx // abs(dx)
                            for nx in range(self.pos[0] + step, x, step):
                                pieces += bool(self.chessboard.get_chess_piece(nx, y))
                        else: continue
                        if (pieces == 0 and not c) or (pieces == 1 and c):
                            movements |= {(x, y)}
                    elif self.type == 6:
                        direction = self.color * 2 - 1
                        if ((0 + 5 * self.color) <= self.pos[1] <= (4 + 5 * self.color) or [dx, dy] == [0, direction]) and ([dx, dy] in [[0, direction], [1, 0], [-1, 0]]):
                            movements |= {(x, y)}
        return movements
    def move(self, x, y):
        if (x, y) in self.get_movements():
            c = self.chessboard.get_chess_piece(x, y)
            if c and c.color != self.color:
                self.chessboard.chess_pieces.remove(c)
                if c.type == 0: self.chessboard.won = self.color + 1
            self.pos = [x, y]
            self.chessboard.turn = 1 - self.chessboard.turn
            return True
        return False
    def to_bytes(self):
        n = self.pos[0] + self.pos[1] * 9 + self.type * 9 * 10 + self.color * 9 * 10 * 7
        byte0 = n % 256
        byte1 = n // 256
        return bytes([byte0, byte1])
    def from_bytes(bytes, chessboard):
        if type(bytes) == list: byte0, byte1 = bytes
        else: byte0, byte1 = list(bytes)
        n = byte1 * 256 + byte0
        c = chess_piece(chessboard, n // (9 * 10 * 7), n % (9 * 10 * 7) // (9 * 10),
                        n % 9, n % (9 * 10) // 9)
        return c
    
class chessboard:
    def __init__(self):
        self.chess_pieces = [
            chess_piece(self, 0, 6, 0, 6),
            chess_piece(self, 0, 6, 2, 6),
            chess_piece(self, 0, 6, 4, 6),
            chess_piece(self, 0, 6, 6, 6),
            chess_piece(self, 0, 6, 8, 6),
            chess_piece(self, 0, 5, 1, 7),
            chess_piece(self, 0, 5, 7, 7),
            chess_piece(self, 0, 4, 0, 9),
            chess_piece(self, 0, 3, 1, 9),
            chess_piece(self, 0, 2, 2, 9),
            chess_piece(self, 0, 1, 3, 9),
            chess_piece(self, 0, 0, 4, 9),
            chess_piece(self, 0, 1, 5, 9),
            chess_piece(self, 0, 2, 6, 9),
            chess_piece(self, 0, 3, 7, 9),
            chess_piece(self, 0, 4, 8, 9),
            chess_piece(self, 1, 6, 0, 3),
            chess_piece(self, 1, 6, 2, 3),
            chess_piece(self, 1, 6, 4, 3),
            chess_piece(self, 1, 6, 6, 3),
            chess_piece(self, 1, 6, 8, 3),
            chess_piece(self, 1, 5, 1, 2),
            chess_piece(self, 1, 5, 7, 2),
            chess_piece(self, 1, 4, 0, 0),
            chess_piece(self, 1, 3, 1, 0),
            chess_piece(self, 1, 2, 2, 0),
            chess_piece(self, 1, 1, 3, 0),
            chess_piece(self, 1, 0, 4, 0),
            chess_piece(self, 1, 1, 5, 0),
            chess_piece(self, 1, 2, 6, 0),
            chess_piece(self, 1, 3, 7, 0),
            chess_piece(self, 1, 4, 8, 0)]
        self.won = 0
        self.turn = 0
        
    def get_chess_piece(self, x, y):
        for piece in self.chess_pieces:
            if piece.pos == [x, y]: return piece
    def general(self, color):
        for piece in self.chess_pieces:
            if piece.color == color and piece.type == 0: return piece
    def to_bytes(self):
        n = self.won + self.turn * 3
        byte = bytes([n])
        for piece in self.chess_pieces: byte += piece.to_bytes()
        return byte
    def longest_lenth():
        return len(chessboard().to_bytes())
    def from_bytes(bytes):
        l = list(bytes)
        c = chessboard()
        c.chess_pieces = []
        c.won, c.turn = l[0] % 3, l[0] // 3
        index = 1
        while index < (len(l)):
            c.chess_pieces.append(chess_piece.from_bytes(l[index:index + 2], c))
            index += 2
        return c
    def copy(self):
        return chessboard.from_bytes(self.to_bytes())

class chessboard_window(QtGui.QMainWindow):
    def __init__(self, parent = None, arg = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle('象棋')
        self.setWindowIcon(QtGui.QIcon(split(abspath(argv[0]))[0] + '\\icon.png'))
        self.central_widget = QtGui.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.chessboard = chessboard()

        #菜单栏
        self.menubar = QtGui.QMenuBar(self)
        self.setMenuBar(self.menubar)
        
        self.game = QtGui.QMenu('棋局', self.menubar)
        self.menubar.addMenu(self.game)
        
        self.undo = QtGui.QAction('悔棋', self.game)
        self.undo.setShortcut('Ctrl+Z')
        self.undo.triggered.connect(self.undo_triggered)
        self.undo.setEnabled(False)
        self.game.addAction(self.undo)
        
        self.redo = QtGui.QAction('撤销悔棋', self.game)
        self.redo.setShortcut('Ctrl+Y')
        self.redo.triggered.connect(self.redo_triggered)
        self.redo.setEnabled(False)
        self.game.addAction(self.redo)
        
        self.open = QtGui.QAction('打开文件', self.game)
        self.open.setShortcut('Ctrl+O')
        self.open.triggered.connect(self.open_from_file)
        self.game.addAction(self.open)
        
        self.save = QtGui.QAction('保存棋局', self.game)
        self.save.setShortcut('Ctrl+S')
        self.save.triggered.connect(self.save_to_file)
        self.game.addAction(self.save)
        
        self.mute_action = QtGui.QAction('静音', self.game)
        self.mute_action.setCheckable(True)
        self.mute_action.triggered.connect(self.mute_action_triggered)
        self.mute_action.setShortcut('Ctrl+M')
        self.mute = False
        self.game.addAction(self.mute_action)
        
        self.reset_action = QtGui.QAction('重置棋局', self.game)
        self.reset_action.triggered.connect(self.reset)
        self.reset_action.setEnabled(False)
        self.game.addAction(self.reset_action)

        self.reset_button = QtGui.QPushButton('重置棋局', self)
        self.reset_button.clicked.connect(self.reset)
        self.reset_button.setVisible(False)
        #

        self.move_sound = QtGui.QSound('move.wav') #音效
        
        desktop = QtGui.QApplication.desktop()
        w = round(100 / desktop.widthMM() * desktop.width()) #窗口宽100mm
        h = round(110 / desktop.heightMM() * desktop.height()) #窗口高110mm
        self.w_h_ratio = w / h
        self.block_lenth = w / 10
        
        self.reset_button_style = '''
QPushButton{
background-color:rgba(255,255,255,160);
border:%ipx solid black;
}
QPushButton:hover{
background-color:rgba(255,255,255,224);
border:%ipx solid black;
}
QPushButton:pressed{
background-color:rgba(128,128,128,160);
border:%ipx solid black;
}'''
        self.reset_button.setStyleSheet(self.reset_button_style%(self.block_lenth * 0.05, self.block_lenth * 0.05, self.block_lenth * 0.05))

        self.mouse_timer = self.startTimer(10)
        self.update_timer = self.startTimer(10)
        self.hover_block = None
        self.choice_block = None

        self.messages = []
        self.flickering = []
        self.last = []
        self.next = []
        self.time = 0
        
        self.resize(w, h)
        self.setMinimumSize(w / 4, h / 4)
        self.show()
        
        self.resize(w * 2 - self.central_widget.width(), h * 2 - self.central_widget.height())
        self.central_rect = QtCore.QRect(0, 0, w, h)

        if arg: self._open(arg)

    def mute_action_triggered(self, mute): self.mute = mute
    
    def open_from_file(self):
        if self.chessboard.to_bytes() != chessboard().to_bytes():
            msgbox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, '警告', '打开新的文件将丢失当前棋局，是否要保存当前棋局？', parent = self)
            msgbox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            msgbox.button(QtGui.QMessageBox.Yes).setText("是")
            msgbox.button(QtGui.QMessageBox.No).setText("否")
            if msgbox.exec_() == QtGui.QMessageBox.Yes:
                self.save_to_file()
        self._open(QtGui.QFileDialog.getOpenFileName(self, '打开', '..', '象棋文件(*.chs)'))
        
    def _open(self, path):
        if path:
            error = False
            if getsize(path) <= chessboard.longest_lenth():
                with open(path, 'rb') as f: b = f.read()
                try: self.chessboard = chessboard.from_bytes(b)
                except: error = True
            else: error = True
            if error:
                msgbox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, '警告', '无法打开文件', parent = self)
                msgbox.setStandardButtons(QtGui.QMessageBox.Ok)
                msgbox.button(QtGui.QMessageBox.Ok).setText("确定")
                msgbox.exec_()
                
    def save_to_file(self):
        path = QtGui.QFileDialog.getSaveFileName(self, '保存为', '..\\棋局.chs', '象棋文件(*.chs)')
        if path:
            with open(path, 'wb') as f:
                b = f.write(self.chessboard.to_bytes())
            
    def reset(self):
        if not self.mute: self.move_sound.play()
        self.chessboard = chessboard()
        self.messages = []
        self.flickering = []
        self.last = []
        self.next = []
        self.time = 0
        self.reset_action.setEnabled(False)
        self.reset_button.setVisible(False)
        self.undo.setEnabled(False)
        self.redo.setEnabled(False)
        self.choice_block = None
        self.update()
        
    def redo_triggered(self):
        if self.next:
            if not self.mute: self.move_sound.play()
            self.last.append(self.chessboard.copy())
            self.chessboard = self.next.pop().copy()
            self.undo.setEnabled(bool(self.last))
            self.redo.setEnabled(bool(self.next))
            self.choice_block = None
            self.update()
            
    def undo_triggered(self):
        if self.last:
            self.next.append(self.chessboard.copy())
            self.chessboard = self.last.pop().copy()
            self.undo.setEnabled(bool(self.last))
            self.redo.setEnabled(bool(self.next))
            self.choice_block = None
            self.update()
            
    def resizeEvent(self, event):
        w = min(self.central_widget.width(), self.central_widget.height() * self.w_h_ratio) #根据长计算画布在窗口中的宽
        h = min(self.central_widget.height(), self.central_widget.width() / self.w_h_ratio) #根据宽计算画布在窗口中的长
        self.central_rect = QtCore.QRect(self.central_widget.width() / 2 - w / 2,
                                         self.central_widget.height() / 2 - h / 2,
                                         w,
                                         h)
        self.block_lenth = w / 10
        t, l = self.central_rect.top() + self.central_widget.geometry().top(), self.central_rect.left() + self.central_widget.geometry().left()
        self.reset_button.setGeometry(l + self.block_lenth * 3, t + self.block_lenth * 6, self.block_lenth * 4, self.block_lenth)
        font = self.reset_button.font()
        font.setPixelSize(self.block_lenth * 0.85)
        self.reset_button.setFont(font)
        self.reset_button.setStyleSheet(self.reset_button_style%(self.block_lenth * 0.05, self.block_lenth * 0.05, self.block_lenth * 0.05))
        
    def paintEvent(self, event):
        #   0 1 2 3 4 5 6 7 8
        #0 ┏┯┯┯┯┯┯┯┓
        #1 ┠┼┼┼┼┼┼┼┨
        #2 ┠┼┼┼┼┼┼┼┨
        #3 ┠┼┼┼┼┼┼┼┨
        #4 ┣┷┷┷┷┷┷┷┫
        #5 ┣┯┯┯┯┯┯┯┫
        #6 ┠┼┼┼┼┼┼┼┨
        #7 ┠┼┼┼┼┼┼┼┨
        #8 ┠┼┼┼┼┼┼┼┨
        #9 ┗┷┷┷┷┷┷┷┛
        
        t, l = self.central_rect.top() + self.central_widget.geometry().top(), self.central_rect.left() + self.central_widget.geometry().left()
        rect = QtCore.QRect(QtCore.QPoint(l, t), self.central_rect.size())
        p = QtGui.QPainter()
        p.begin(self)
        
        pen1 = QtGui.QPen(QtGui.QBrush(Qt.black), self.block_lenth / 20, join = Qt.MiterJoin)#细
        pen1_red = QtGui.QPen(QtGui.QBrush(Qt.red), self.block_lenth / 20, join = Qt.MiterJoin)#细
        pen2 = QtGui.QPen(QtGui.QBrush(Qt.black), self.block_lenth / 10, join = Qt.MiterJoin)#粗

        #绘制棋盘
        p.setPen(pen2)
        p.drawRect(l + self.block_lenth, t + self.block_lenth, self.block_lenth * 8, self.block_lenth * 9)
        p.drawLine(l + self.block_lenth, t + self.block_lenth * 5, l + self.block_lenth * 9, t + self.block_lenth * 5)
        p.drawLine(l + self.block_lenth, t + self.block_lenth * 6, l + self.block_lenth * 9, t + self.block_lenth * 6)
        p.setPen(pen1)
        for y in [2, 3, 4, 7, 8, 9]:
            p.drawLine(l + self.block_lenth, t + self.block_lenth * y, l + self.block_lenth * 9, t + self.block_lenth * y)
        for x in range(2, 9):
            p.drawLine(l + self.block_lenth * x, t + self.block_lenth, l + self.block_lenth * x, t + self.block_lenth * 5)
            p.drawLine(l + self.block_lenth * x, t + self.block_lenth * 6, l + self.block_lenth * x, t + self.block_lenth * 10)
        p.drawLine(l + self.block_lenth * 4, t + self.block_lenth, l + self.block_lenth * 6, t + self.block_lenth * 3)
        p.drawLine(l + self.block_lenth * 4, t + self.block_lenth * 3, l + self.block_lenth * 6, t + self.block_lenth)
        p.drawLine(l + self.block_lenth * 4, t + self.block_lenth * 8, l + self.block_lenth * 6, t + self.block_lenth * 10)
        p.drawLine(l + self.block_lenth * 4, t + self.block_lenth * 10, l + self.block_lenth * 6, t + self.block_lenth * 8)

        for x, y in [[2, 3], [4, 3], [6, 3], [8, 3], [1, 2], [7, 2], [2, 6], [4, 6], [6, 6], [8, 6], [1, 7], [7, 7]]:
            p.drawLine(l + self.block_lenth * (x + 0.7), t + self.block_lenth * (y + 0.9), l + self.block_lenth * (x + 0.9), t + self.block_lenth * (y + 0.9))
            p.drawLine(l + self.block_lenth * (x + 0.7), t + self.block_lenth * (y + 1.1), l + self.block_lenth * (x + 0.9), t + self.block_lenth * (y + 1.1))
            p.drawLine(l + self.block_lenth * (x + 0.9), t + self.block_lenth * (y + 0.7), l + self.block_lenth * (x + 0.9), t + self.block_lenth * (y + 0.9))
            p.drawLine(l + self.block_lenth * (x + 0.9), t + self.block_lenth * (y + 1.1), l + self.block_lenth * (x + 0.9), t + self.block_lenth * (y + 1.3))
        
        for x, y in [[0, 3], [2, 3], [4, 3], [6, 3], [1, 2], [7, 2], [0, 6], [2, 6], [4, 6], [6, 6], [1, 7], [7, 7]]:
            p.drawLine(l + self.block_lenth * (x + 1.1), t + self.block_lenth * (y + 0.9), l + self.block_lenth * (x + 1.3), t + self.block_lenth * (y + 0.9))
            p.drawLine(l + self.block_lenth * (x + 1.1), t + self.block_lenth * (y + 1.1), l + self.block_lenth * (x + 1.3), t + self.block_lenth * (y + 1.1))
            p.drawLine(l + self.block_lenth * (x + 1.1), t + self.block_lenth * (y + 0.7), l + self.block_lenth * (x + 1.1), t + self.block_lenth * (y + 0.9))
            p.drawLine(l + self.block_lenth * (x + 1.1), t + self.block_lenth * (y + 1.1), l + self.block_lenth * (x + 1.1), t + self.block_lenth * (y + 1.3))
        
        font = QtGui.QFont('楷体')
        font.setPixelSize(self.block_lenth * 0.9)
        p.setFont(font)
        fm = p.fontMetrics()
        center = rect.center()
        text = '楚 河 汉 界'
        p.drawText(center.x() - fm.width(text) / 2, center.y() - fm.height() / 2 + fm.ascent(), text)
        
        #绘制棋子
        for c in self.chessboard.chess_pieces:
            x, y = c.pos

            if self.choice_block == c.pos:
                p.setPen(QtGui.QPen(QtGui.QBrush(Qt.blue), self.block_lenth / 20))
                p.setBrush(QtGui.QColor(192, 192, 192))
            elif self.hover_block == c.pos:
                p.setPen([pen1_red, pen1][c.color])
                p.setBrush(QtGui.QColor(192, 192, 192))
            else:
                p.setPen([pen1_red, pen1][c.color])
                p.setBrush(self.palette().background())
            for _x, _y in self.flickering:
                if (_x, _y) == (x, y):
                    if self.time % 100 < 50:
                        p.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(0, 192, 0)), self.block_lenth / 20))
            
            p.drawEllipse(l + self.block_lenth * (x + 0.55), t + self.block_lenth * (y + 0.55),
                          self.block_lenth * 0.9, self.block_lenth * 0.9)
                    
            p.setPen(QtGui.QPen(QtGui.QColor(255 * (1 - c.color), 0, 0)))
            font = QtGui.QFont('楷体')
            font.setPixelSize(self.block_lenth * 0.7)
            p.setFont(font)
            fm = p.fontMetrics()
            cx, cy = l + self.block_lenth * (x + 1), t + self.block_lenth * (y + 1)
            text = c.get_chinese_name()
            p.drawText(cx - fm.width(text) / 2, cy - fm.height() / 2 + fm.ascent(), text)
        
        if self.hover_block and self.choice_block and \
           not self.chessboard.get_chess_piece(self.hover_block[0], self.hover_block[1]) and \
           tuple(self.hover_block) in self.chessboard.get_chess_piece(self.choice_block[0], self.choice_block[1]).get_movements():
            p.setBrush(QtGui.QColor(128, 128, 128, 128))
            p.setPen(Qt.NoPen)
            p.drawRect(l + self.block_lenth * (self.hover_block[0] + 0.5), t + self.block_lenth * (self.hover_block[1] + 0.5),
                       self.block_lenth, self.block_lenth)

        for message in self.messages:
            color = QtGui.QColor(message[1])
            if 255 > message[-1] * 2: color.setAlpha(message[-1] * 2)
            p.setPen(QtGui.QPen(color))
            font = QtGui.QFont('Microsoft YaHei UI')
            font.setPixelSize(self.block_lenth * 2)
            p.setFont(font)
            fm = p.fontMetrics()
            p.drawText(l + message[2] * self.block_lenth - fm.width(message[0]) / 2, t + message[3] * self.block_lenth - fm.height() / 2 + fm.ascent(), message[0])

        p.setPen(Qt.NoPen)
        p.setBrush(Qt.black)
        if self.chessboard.turn:
            p.drawPolygon(QtCore.QPointF(l + self.block_lenth * 5, t + self.block_lenth * 0.45),
                          QtCore.QPointF(l + self.block_lenth * 5.5, t + self.block_lenth * 0.1),
                          QtCore.QPointF(l + self.block_lenth * 4.5, t + self.block_lenth * 0.1))
        else:
            p.drawPolygon(QtCore.QPointF(l + self.block_lenth * 5, t + self.block_lenth * 10.55),
                          QtCore.QPointF(l + self.block_lenth * 5.5, t + self.block_lenth * 10.9),
                          QtCore.QPointF(l + self.block_lenth * 4.5, t + self.block_lenth * 10.9))

        if self.chessboard.won:
            self.reset_button.setVisible(True)
            p.fillRect(rect, QtGui.QColor(128, 128, 128, 128))
            p.setPen(QtGui.QPen(Qt.red))
            font = QtGui.QFont('Microsoft YaHei UI')
            font.setPixelSize(self.block_lenth * 2)
            p.setFont(font)
            fm = p.fontMetrics()
            center = rect.center()
            text = '  %s方胜利！'%(['红', '黑'][self.chessboard.won - 1])
            p.drawText(center.x() - fm.width(text) / 2, center.y() - self.block_lenth - fm.height() / 2 + fm.ascent(), text)
        p.end()
        
    def timerEvent(self, event):
        if event.timerId() == self.mouse_timer and not self.chessboard.won:
            if self.hover_block: hover_block_last = self.hover_block[:]
            else: hover_block_last = None
            cursor = QtGui.QCursor()
            point = QtCore.QPoint((cursor.pos().x() - self.geometry().left() - self.central_widget.geometry().left() - self.central_rect.left()),
                                  (cursor.pos().y() - self.geometry().top() - self.central_widget.geometry().top() - self.central_rect.top()))
            x = int(point.x() / self.block_lenth - 0.5)
            y = int(point.y() / self.block_lenth - 0.5)
            if 0 <= x <= 8 and 0 <= y <= 9:
                c = self.chessboard.get_chess_piece(x, y)
                if c:
                    if (((point.x() - (x + 1) * self.block_lenth) ** 2 + \
                         (point.y() - (y + 1) * self.block_lenth) ** 2) ** 0.5) < self.block_lenth * 0.45 and \
                         (c.color == self.chessboard.turn or \
                          (self.choice_block and (x, y) in self.chessboard.get_chess_piece(self.choice_block[0], self.choice_block[1]).get_movements())):
                        self.hover_block = [x, y]
                    else: self.hover_block = None
                else: self.hover_block = [x, y]
            else: self.hover_block = None
            if hover_block_last != self.hover_block: self.update()
            
        elif event.timerId() == self.update_timer:
            self.time += 1
            i = 0
            update = False
            while i < len(self.messages):
                self.messages[i][-1] -= 1
                if self.messages[i][-1] * 2 < 255: update = True
                if self.messages[i][-1] <= 0: self.messages.remove(self.messages[i])
                else: i += 1
            update |= bool(self.flickering)
            if update: self.update()
                
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.choice_block: choice_block_last = self.choice_block[:]
            else: choice_block_last = None
            if self.hover_block and not self.chessboard.won:
                c = self.chessboard.get_chess_piece(self.hover_block[0], self.hover_block[1])
                if c and c.color == self.chessboard.turn:
                    self.choice_block = self.hover_block
                elif self.choice_block:
                    chessboard = self.chessboard.copy()
                    c = self.chessboard.get_chess_piece(self.choice_block[0], self.choice_block[1])
                    done = c.move(self.hover_block[0], self.hover_block[1])
                    if done:
                        if not self.mute: self.move_sound.play()
                        self.last.append(chessboard.copy())
                        self.flickering.clear()
                        if len(self.last) > 20:
                            self.last = self.last[-20:]
                        self.next = []
                        self.undo.setEnabled(bool(self.last))
                        self.redo.setEnabled(bool(self.next))
                        self.reset_action.setEnabled(True)
                        self.choice_block = None
                        self.update()
                        for piece in self.chessboard.chess_pieces:
                            general = self.chessboard.general(1 - piece.color)
                            if general and tuple(general.pos) in piece.get_movements():
                                self.messages.append(['  将军！', Qt.red, 5, 5.5, 256]) #将军提示
                                self.flickering.append(piece.pos) #闪烁将军棋子
            else: self.choice_block = None
            if choice_block_last != self.choice_block: self.update()
            
    def closeEvent(self, event):
        self.killTimer(self.mouse_timer)
        self.killTimer(self.update_timer)
        event.accept()

if __name__ == '__main__':
    app = QtGui.QApplication(argv)
    if args:
        windows = []
        for arg in args:
            windows.append(chessboard_window(arg = arg))
    else: window = chessboard_window()
    app.exec_()
