from tkinter import *
from random import choice
from threading import Timer
from functools import partial

class DifficultyWindow(Toplevel):
    def __init__(self, master, index = 0):
        super().__init__(master)
        self.iconbitmap("icon.ico")
        self.title("Select difficulty")
        self.frame = Frame(self)
        self.btns = []
        self.destoryed = False
        i = 0
        for text in ['easy - 10x10  10 mines', 'medium - 16x16  40 mines', 'difficult - 30x16  99 mines']:
            btn = Checkbutton(self.frame, text = text, command = partial(self.choose, i))
            btn.grid(column = 0, row = i, padx = 10, pady = 10, sticky = 'w')
            self.btns.append(btn)
            i += 1
        self.index = index
        self.btns[index].select()
        self.ok_btn = Button(self.frame, text = 'OK')
        self.ok_btn.grid(column = 0, row = i, pady = 10, ipadx = 30)
        self.ok_btn.bind("<ButtonRelease-1>", self.close)
        self.frame.pack()
        
    def choose(self, index):
        self.index = index
        for i in range(len(self.btns)):
            if i != index:
                self.btns[i].deselect()

    def close(self, event):
        if not self.destoryed:
            self.destoryed = True
            if self.master.difficulty != self.index:
                self.master.difficulty = self.index
                for i in range(self.master.map_height):
                    for j in range(self.master.map_width):
                        self.master.btns[i][j].destroy()
                self.master.btns.clear()
                self.master.map_width, self.master.map_height, self.master.mine_cnt = [(10, 10, 10), (16, 16, 40), (30, 16, 99)][self.master.difficulty]
                self.master.mine_rest = self.master.mine_cnt
                self.master.init_btns()
                self.master.reset()
            self.destroy()
            
class App(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self.num_images = [PhotoImage(file = 'images/%i.gif'%i) for i in range(9)]
        self.lcdnum_images = [PhotoImage(file = 'images/lcdnumber/%i.gif'%i) for i in range(10)]
        self.bg_img = PhotoImage(file = 'images/bg.gif')
        self.flag_img = PhotoImage(file = 'images/flag.gif')
        self.mine_img = PhotoImage(file = 'images/mine.gif')
        self.mine_img_red = PhotoImage(file = 'images/mine_red.gif')
        self.reset_img = PhotoImage(file = 'images/reset.gif')
        self.win_img = PhotoImage(file = 'images/win.gif')
        self.lose_img = PhotoImage(file = 'images/lose.gif')

        self.map_width = 10
        self.map_height = 10
        self.mine_cnt = 10
        self.mine_rest = 10
        self.mines = [[False]*self.map_width for i in range(self.map_height)]
        self.block_status = [[-1]*self.map_width for i in range(self.map_height)]
        self.difficulty = 0
        self.end = 0
        self.first = True

        self.top = Frame(self)
        self.reset_btn = Button(self.top, image = self.reset_img, bg = '#c0c0c0', activebackground = '#c0c0c0')
        self.reset_btn.grid(column = 1, row = 0, padx = 40)
        self.reset_btn.bind('<ButtonRelease-1>', self.reset)

        self.mine_canvas = Canvas(self.top)
        self.update_lcdcanvas(self.mine_canvas, 0)
        self.mine_canvas.grid(column = 0, row = 0)

        self.time = 0
        self.time_canvas = Canvas(self.top)
        self.update_lcdcanvas(self.time_canvas, 0)
        self.time_canvas.grid(column = 2, row = 0)
        
        self.top.grid(column = 0, row = 0, columnspan = self.map_width, pady = 5)
        self.init_btns()

        self.menubar = Menu(self.master)
        self.game_menu = Menu(self.menubar)
        self.game_menu.add_command(label = "Select difficulty", command = self.select_difficulty)
        self.menubar.add_cascade(label = 'Game', menu = self.game_menu)
        self.master.config(menu = self.menubar)

        self.select_difficulty()

    def init_btns(self):
        self.btns = []
        for i in range(self.map_height):
            self.btns.append([])
            for j in range(self.map_width):
                btn = Label(self, image = self.bg_img, bg = '#00a000', activebackground = '#00a000', relief = RAISED, width = 20, height = 20)
                btn.bind('<Button-1>', partial(self.press, j, i))
                btn.bind('<ButtonRelease-1>', partial(self.pressed, j, i))
                btn.bind('<ButtonRelease-3>', partial(self.pressed_right, j, i))
                btn.grid(column = j, row = i + 1)
                self.btns[-1].append(btn)
                self.top.grid(column = 0, row = 0, columnspan = self.map_width, pady = 5)
                
    def select_difficulty(self):
        w = DifficultyWindow(self, self.difficulty)
        
    def random_mines(self, x = -1, y = -1):
        self.mines = [[False]*self.map_width for i in range(self.map_height)]
        l = [[i, j] for i in range(self.map_width) for j in range(self.map_height)]
        if [x, y] in l:
            l.remove([x, y])
        for i in range(self.mine_cnt):
            tmp = choice(l)
            self.mines[tmp[1]][tmp[0]] = True
            l.remove(tmp)
        del l
        
    def press(self, x, y, *args):
        if not self.end:
            self.btns[y][x].config(relief = SUNKEN)
        
    def create_timer(self):
        self.timer = Timer(1.0, self.timer_timeout)
        self.timer.start()
        
    def timer_timeout(self):
        self.create_timer()
        self.time += 1
        self.update_lcdcanvas(self.time_canvas, self.time)
        
    def update_lcdcanvas(self, canvas, num):
        n = max(0, num)
        s = '%.3d'%n
        canvas.config(width = len(s) * 13, height = 23)
        for i in range(len(s)):
            canvas.create_image(i * 13 + 2, 0 + 2, anchor = 'nw', image = self.lcdnum_images[int(s[i])])
            #canvas.create_rectangle(i * 13, 0, i * 13 + 13, 23)
        return True
        
    def reset(self, *args, **kwargs):
        try: self.timer.cancel()
        except AttributeError: pass
        self.mines = [[False]*self.map_width for i in range(self.map_height)]
        self.block_status = [[-1]*self.map_width for i in range(self.map_height)]
        self.end = 0
        self.mine_rest = self.mine_cnt
        self.first = True
        for i in range(self.map_height):
            for j in range(self.map_width):
                self.btns[i][j].config(image = self.bg_img, bg = '#00a000', activebackground = '#00a000', relief = RAISED)
        self.reset_btn.config(image = self.reset_img)
        
        self.update_lcdcanvas(self.mine_canvas, 0)
        self.time = 0
        self.update_lcdcanvas(self.time_canvas, 0)

    def update_mine_label(self):
        self.update_lcdcanvas(self.mine_canvas, self.mine_rest)
        
    def near(self, x, y):
        return [[a, b] for a, b in [[x, y+1],
                                    [x, y-1],
                                    [x+1, y],
                                    [x+1, y+1],
                                    [x+1, y-1],
                                    [x-1, y],
                                    [x-1, y+1],
                                    [x-1, y-1]] if 0 <= a < self.map_width and 0 <= b < self.map_height]
    
    def win_check(self):
        cnt = 0
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.block_status[y][x] < 0:
                    cnt += 1
        if cnt == self.mine_cnt:
            self.end = 1
            self.timer.cancel()
            self.reset_btn.config(image = self.win_img)
            return
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.mines[y][x] and self.block_status[y][x] != -2:
                    return
                if not self.mines[y][x] and self.block_status[y][x] == -2:
                    return
        self.end = 1
        self.timer.cancel()
        self.reset_btn.config(image = self.win_img)
        
    def pressed(self, x, y, *args, f = False):
        if not self.end:
            if (f and self.block_status[y][x] in [-1, -2]) or (not f and self.block_status[y][x] == -1):
                if self.block_status[y][x] == -2:
                    self.mine_rest += 1
                    self.update_mine_label()
                if self.first:
                    self.random_mines(x, y)
                    self.first = False
                    self.create_timer()
                if self.mines[y][x]:
                    for i in range(self.map_height):
                        for j in range(self.map_width):
                            if self.mines[i][j]:
                                self.btns[i][j].config(image = self.mine_img, bg = '#c0c0c0', activebackground = '#c0c0c0', relief = RAISED)
                                
                    self.btns[y][x].config(image = self.mine_img_red, bg = '#ff0000', activebackground = '#ff0000', relief = RAISED)
                    self.end = -1
                    self.timer.cancel()
                    self.reset_btn.config(image = self.lose_img)
                    return
                near = self.near(x, y)
                cnt = 0
                for a, b in near:
                    if self.mines[b][a]: cnt += 1
                self.btns[y][x].config(image = self.num_images[cnt], bg = '#c0c0c0', activebackground = '#c0c0c0', relief = SUNKEN)
                self.block_status[y][x] = cnt
                self.win_check()
                
                if not cnt:
                    for a, b in near:
                        self.pressed(a, b, f = True)
                        
            elif self.block_status[y][x] == -2:
                self.block_status[y][x] = -1
                self.mine_rest += 1
                self.update_mine_label()
                self.btns[y][x].config(image = self.bg_img, bg = '#00a000', activebackground = '#00a000', relief = RAISED)
        
    def pressed_right(self, x, y, *args):
        if not self.end:
            if self.block_status[y][x] == -1:
                self.block_status[y][x] = -2
                self.mine_rest -= 1
                self.update_mine_label()
                self.btns[y][x].config(image = self.flag_img, bg = '#c0c0c0', activebackground = '#c0c0c0')
                self.win_check()
            elif self.block_status[y][x] == -2:
                self.block_status[y][x] = -1
                self.mine_rest += 1
                self.update_mine_label()
                self.btns[y][x].config(image = self.bg_img, bg = '#00a000', activebackground = '#00a000')
                

root = Tk()
root.title("minesweeper")
root.iconbitmap("icon.ico")
myapp = App(root)
myapp.mainloop()
try: myapp.timer.cancel()
except AttributeError: pass
