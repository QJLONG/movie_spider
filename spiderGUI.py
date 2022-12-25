from tkinter import *
from tkinter import scrolledtext
import main_2
import threading

class Application(threading.Thread):
    def __init__(self, master=None):
        threading.Thread.__init__(self)
        self.master = master
        self.checked_list = []
        self.list = list(range(1, 37))
        self.createBanner()
        self.createFrame()
        self.createSelectFrame()
        self.createBottom()
    
    def createBanner(self):
        self.lab_banner = Label(self.master, text="点燃我，温暖你下载：", font=("黑体", 16))
        self.lab_banner.grid(row=0, column=0)

    def createFrame(self):
        self.frm = LabelFrame(self.master)
        self.frm.grid(row=1, column=0, padx=35, pady=20)
        line_num = 0
        for i in range(len(self.list)):
            Button(self.frm, text=f"第{i+1}集", command=lambda num=i:self.clickButton(num+1)).grid(row=i//7, column=i%7, padx=5, pady=5)
    
    def clickButton(self, i):
        # print(f"已经选中第{k}集")
        if i not in self.checked_list:
            self.checked_list.append(i)
        else:
            self.checked_list.remove(i)
        self.checked_list.sort()
        self.select_frm.destroy()
        self.createSelectFrame()
    
    def createSelectFrame(self):
        self.select_frm = LabelFrame(self.master, text="下载如下：")
        self.select_frm.grid(row=2, column=0, padx=35, pady=15, sticky=W)
        for i in range(len(self.checked_list)):
            Label(self.select_frm, text=f"第{self.checked_list[i]}集").grid(row=i//7, column=i%7)

    def select_all(self):
        self.checked_list = range(1,37)
        self.select_frm.destroy()
        self.createSelectFrame()
        
    def remove_all(self):
        self.checked_list = []
        self.select_frm.destroy()

    def createBottom(self):
        self.bot_frm = LabelFrame(self.master)
        self.bot_frm.grid(sticky=S)
        self.remove_all = Button(self.bot_frm, text="清空", command=self.remove_all, font=("黑体", 16))
        self.remove_all.grid(row=0, column=0, padx=20, pady=5)
        self.select_all = Button(self.bot_frm, text="全选", command=self.select_all, font=("黑体", 16))
        self.select_all.grid(row=0, column=1, padx=20, pady=5)
        self.button_cancel = Button(self.bot_frm, text="取消", font=("黑体", 16), command=self.master.quit)
        self.button_cancel.grid(row=0, column=2, padx=20, pady=5)
        self.button_OK = Button(self.bot_frm, text="下载", font=("黑体", 16), command=self.run)
        self.button_OK.grid(row=0, column=3, padx=20, pady=5)
        
    
    def run(self):
        for i in self.checked_list:
            main_2.down(f"https://www.shukeju.org/kanvodplay/386176-3-{i}/")



if __name__ == '__main__':
    win = Tk()
    win.geometry("500x600+600+300")
    win.title("点燃我，温暖你")
    app = Application(win)
    app.start()
    win.mainloop()