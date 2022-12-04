from tkinter import *
from tkinter.messagebox import *
from tkinter import ttk  # 导入ttk模块，因为Combobox下拉菜单控件在ttk中
from src.parameter import window_capture, version
import sys
import serial
import serial.tools.list_ports
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import webbrowser
import time
import os
import random

import ctypes

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams["axes.unicode_minus"] = False  # 设置正常显示符号
tempData = 0
humData = 0


class MENU:
    def __init__(self, init_window_name):
        self.init_window_name = init_window_name

    @staticmethod
    def callback1():
        print("--- 获取源码 ---")
        showwarning("warning", "Please follow the GPL3.0")
        webbrowser.open("https://github.com/Theo-s-Open-Source-Project")

    @staticmethod
    def callback2():
        print("--- 退出 ---")
        sys.exit()

    def callback3(self):
        print("--- 刷新串口 ---")

    @staticmethod
    def callback4():
        print("--- 截图 ---")
        window_capture()

    @staticmethod
    def callback5():
        config = version.config()
        if config['power'] == 'Professional':
            print("--- 温度折线图 ---")
            new_win = zsh_serial()
            new_win.createTempWindow()
        else:
            showerror("权限不足", "请升级专业版")
            new_win = zsh_serial()
            new_win.power()

    @staticmethod
    def callback6():
        config = version.config()
        if config['power'] == 'Professional':
            print("--- 湿度折线图 ---")
            new_win = zsh_serial()
            new_win.createHumWindow()
        else:
            showerror("权限不足", "请升级专业版")
            new_win = zsh_serial()
            new_win.power()

    @staticmethod
    def callback7():
        print("--- 帮助 ---")
        os.startfile("data\\readme.txt")

    @staticmethod
    def callback8():
        print("--- 关于 ---")
        version.info()

    @staticmethod
    def callback9():
        print("--- 更新检测 ---")
        import requests
        ver = requests.get('http://xxx.xxx.xxx.xx/download/open-source-project/zshSerial/version.txt')
        print(ver.text)
        config = version.config()
        if "lastest: v{}".format(config['version']) == ver.text:
            versionCheck = "当前版本：v{} 为最新版".format(config['version'])
            showinfo('更新检测', versionCheck)
        else:
            versionCheck = "当前版本：v{} 版本过低，请及时更新".format(config['version'])
            showwarning('更新检测', versionCheck)
            version.update()

    @staticmethod
    def callback10():
        print("--- 博客教程 ---")
        webbrowser.open("http://t.csdn.cn/Fc538")


class zsh_serial:
    def __init__(self):
        self.window = Tk()  # 实例化出一个父窗口
        self.com = serial.Serial()
        self.serial_combobox = None
        self.bound_combobox = None
        self.txt = None

    def ui(self):
        ############################################
        # 窗口配置
        ############################################
        # self.window = Tk()  # 实例化出一个父窗口
        self.window.title("温湿度串口调试助手")
        self.window.iconbitmap(default='data\\COM.ico')  # 修改 logo
        width = self.window.winfo_screenwidth()
        height = self.window.winfo_screenheight()
        print(width, height)
        win = '{}x{}+{}+{}'.format(880, 500, width // 3, height // 5)  # {}x{} 窗口大小，+10 +10 定义窗口弹出时的默认展示位置
        self.window.geometry(win)
        self.window.resizable(False, False)

        # 调用api设置成由应用程序缩放
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        # 调用api获得当前的缩放因子
        ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        # 设置缩放因子
        self.window.tk.call('tk', 'scaling', ScaleFactor / 75)

        ############################################
        # menu菜单
        ############################################
        menubar = Menu(self.window)  # 创建一个顶级菜单
        menu = MENU(self.window)
        filemenu1 = Menu(menubar, tearoff=False)  # 在顶级菜单menubar下, 创建一个子菜单filemenu1
        filemenu2 = Menu(menubar, tearoff=False)  # 在顶级菜单menubar下, 创建一个子菜单filemenu2
        filemenu3 = Menu(menubar, tearoff=False)  # 在顶级菜单menubar下, 创建一个子菜单filemenu3
        menubar.add_cascade(label="文件", menu=filemenu1)  # 为子菜单filemenu1取个名字
        menubar.add_cascade(label="工具", menu=filemenu2)  # 为子菜单filemenu2取个名字
        menubar.add_cascade(label="折线图", menu=filemenu3)  # 为子菜单filemenu3取个名字
        menubar.add_command(label="帮助", command=menu.callback7)
        menubar.add_command(label="关于", command=menu.callback8)
        filemenu1.add_command(label="更新检测", command=menu.callback9)  # 为子菜单filemenu1添加选项，取名"更新检测"
        filemenu1.add_command(label="获取源码", command=menu.callback1)  # 为子菜单filemenu1添加选项，取名"获取源码"
        filemenu1.add_command(label="博客教程", command=menu.callback10)  # 为子菜单filemenu1添加选项，取名"博客教程"
        filemenu1.add_separator()  # 添加一条分割线
        filemenu1.add_command(label="退出", command=menu.callback2)  # 为子菜单filemenu1添加选项，取名"关闭"
        filemenu2.add_command(label="刷新串口", command=self.cleanSerial)  # 为子菜单filemenu2添加选项，取名"刷新串口"
        filemenu2.add_command(label="截图", command=menu.callback4)  # 为子菜单filemenu2添加选项，取名"截图"
        filemenu3.add_command(label="温度图", command=menu.callback5)  # 为子菜单filemenu2添加选项，取名"温度图"
        filemenu3.add_command(label="湿度图", command=menu.callback6)  # 为子菜单filemenu2添加选项，取名"湿度图"

        ############################################
        # 串口设置子菜单 1
        ############################################

        # 串口设置
        group_serial_set = LabelFrame(self.window, text="串口设置")
        group_serial_set.grid(row=0, padx=10, pady=10)

        serial_label = Label(group_serial_set, text="串口号")
        serial_label.grid(row=0, column=0, padx=10, pady=10, sticky=W)
        self.serial_combobox = ttk.Combobox(group_serial_set, width=8)
        self.serial_combobox['value'] = zsh_serial.getSerialPort()
        self.serial_combobox.grid(row=0, column=1, padx=10, pady=10)

        bound_label_set = Label(group_serial_set, text="波特率")
        bound_label_set.grid(row=1, column=0)
        self.bound_combobox = ttk.Combobox(group_serial_set, width=8)
        self.bound_combobox['value'] = ("9600", "19200", "38400", "57600", "115200", "128000")
        self.bound_combobox.grid(row=1, column=1)

        databits_label = Label(group_serial_set, text="数据位")
        databits_label.grid(row=2, column=0, pady=10)
        databits_combobox = ttk.Combobox(group_serial_set, width=8)
        databits_combobox['value'] = ("1", "1.5", "2")
        databits_combobox.grid(row=2, column=1)

        checkbits_label = Label(group_serial_set, text="校验位")
        checkbits_label.grid(row=3, column=0)
        checkbits_combobox = ttk.Combobox(group_serial_set, width=8)
        checkbits_combobox['value'] = ("None", "Odd", "Even")
        checkbits_combobox.grid(row=3, column=1)

        xxx_label = Label(group_serial_set, text="   ")
        xxx_label.grid(row=4, column=0, pady=1)

        # 接收设置
        recv_set = LabelFrame(self.window, text="接收设置")
        recv_set.grid(row=1, padx=10)

        recv_set_v = IntVar()
        recv_set_radiobutton1 = Radiobutton(recv_set, text="ASCII", variable=recv_set_v, value=1)
        recv_set_radiobutton1.grid(row=0, column=0, sticky=W, padx=10)
        recv_set_radiobutton2 = Radiobutton(recv_set, text="HEX", variable=recv_set_v, value=2)
        recv_set_radiobutton2.grid(row=0, column=1, sticky=W, padx=10)

        recv_set_v1 = IntVar()
        recv_set_v2 = IntVar()
        recv_set_v3 = IntVar()
        recv_set_checkbutton1 = Checkbutton(recv_set, text="自动换行", variable=recv_set_v1, onvalue=1, offvalue=2)
        recv_set_checkbutton1.grid(row=1, column=0, padx=10)
        recv_set_checkbutton2 = Checkbutton(recv_set, text="显示发送", variable=recv_set_v2, onvalue=1, offvalue=2)
        recv_set_checkbutton2.grid(row=2, column=0, padx=10)
        recv_set_checkbutton3 = Checkbutton(recv_set, text="显示时间", variable=recv_set_v3, onvalue=1, offvalue=2)
        recv_set_checkbutton3.grid(row=3, column=0, padx=10)

        # 串口操作
        group_serial_event = LabelFrame(self.window, text="串口操作")
        group_serial_event.grid(row=2, padx=10, pady=10)

        self.serial_btn_flag_str = StringVar()
        self.serial_btn_flag_str.set("串口未打开")
        label_name = Label(group_serial_event, textvariable=self.serial_btn_flag_str, bg='#ff001a', fg='#ffffff')
        label_name.grid(row=0, column=0, padx=55, pady=2)

        self.serial_btn_str = StringVar()
        self.serial_btn_str.set("打开串口")
        serial_btn = Button(group_serial_event, textvariable=self.serial_btn_str, command=self.hit1)
        serial_btn.grid(row=1, column=0, padx=55, pady=10)

        # 数据显示
        self.txt = Text(self.window, width=70, height=26.5, font=("SimHei", 10))
        self.txt.grid(row=0, rowspan=3, column=1, padx=8, pady=10, sticky='s')

        # 串口子菜单设置初值
        self.bound_combobox.set(self.bound_combobox['value'][4])
        databits_combobox.set(databits_combobox['value'][0])
        checkbits_combobox.set(checkbits_combobox['value'][0])
        recv_set_v.set(2)
        recv_set_v1.set(1)
        recv_set_v2.set(2)
        recv_set_v3.set(2)

        ############################################
        # 配置tkinter样式
        ############################################
        self.window.config(menu=menubar)

        ############################################
        # 退出检测
        ############################################
        def bye():
            plt.close('all')
            self.window.destroy()

        self.window.protocol("WM_DELETE_WINDOW", bye)

        # 窗口循环显示
        self.window.mainloop()

    def hit1(self):
        """
        打开串口按钮回调
        """
        # print(self.com.isOpen())
        if self.com.isOpen():
            self.com.close()
            print("--- 串口未打开 ---")
            self.serial_btn_flag_str.set("串口未打开")
            self.serial_btn_str.set("打开串口")
        else:
            self.com, ser_flag = self.openSerial(self.serial_combobox.get(), self.bound_combobox.get(), None)
            if ser_flag:
                print("--- 串口已打开 ---")
                self.serial_btn_flag_str.set("串口已打开")
                self.serial_btn_str.set("关闭串口")

    @staticmethod
    def getSerialPort():
        port = []
        portList = list(serial.tools.list_ports.comports())
        # print(portList)

        if len(portList) == 0:
            print("--- 无串口 ---")
            port.append('None')
        else:
            for comport in portList:
                # print(list(comport)[0])
                # print(list(comport)[1])
                port.append(list(comport)[0])
                pass
        return port

    def openSerial(self, port, bps, timeout):
        """
        打开串口
        :param port: 端口号
        :param bps: 波特率
        :param timeout: 超时时间
        :return: True or False
        """
        ser_flag = False
        try:
            # 打开串口
            self.com = serial.Serial(port, bps, timeout=timeout)
            if self.com.isOpen():
                ser_flag = True
                threading.Thread(target=self.readSerial, args=(self.com,)).start()
                # print("Debug: 串口已打开\n")
            # else:
            #     print("Debug: 串口未打开")
        except Exception as e:
            print("error: ", e)
            error = "error: {}".format(e)
            showerror('error', error)
        return self.com, ser_flag

    def readSerial(self, com):
        """
        读取串口数据
        :return:
        """
        global serialData
        while True:
            if self.com.in_waiting:
                textSetial = self.com.read(self.com.in_waiting)
                serialData = textSetial
                # print(textSetial)
                self.txt.config(state=NORMAL)
                self.txt.insert(END, textSetial)
                self.txt.config(state=DISABLED)
            # print("Debug: thread_readSerial is running")

    def cleanSerial(self):
        self.txt.config(state=NORMAL)
        self.txt.delete("1.0", END)
        self.txt.config(state=DISABLED)

    def createTempWindow(self):
        """
        创建新的窗口
        """
        new_window = self.window
        new_window.title("温度折线图")
        new_window.geometry("720x480")
        # Button(new_window,
        #        text="This is new window").pack()

        # 创建一个容器, 没有画布时的背景
        frame = Frame(new_window, bg="#ffffff")
        frame.place(x=0, y=0, width=720, height=480)
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        fig = plt.figure(figsize=(6, 3.9), edgecolor='blue')
        # 定义刻度
        ax = fig.add_subplot(111)
        ax.set(xlim=[0, 121], ylim=[0, 40], title="温度折线图", ylabel='温度/°C')
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        # 显示画布
        canvas.get_tk_widget().place(x=0, y=0)

        # 定义存储坐标的空数组
        self.i = 0
        self.x = []
        self.y = []

        def drawTemp():
            global tempData
            self.i += 1
            # time.sleep(1)
            ax.clear()
            ax.set(xlim=[0, 121], ylim=[0, 40], title="温度折线图", ylabel='温度/°C')
            t = self.i
            if t >= 120:
                bye()
            dtax = t
            self.x.append(dtax)
            # 温度数据处理
            """
            xxxxxxxxxxxxxxxxxxxxx
            """
            dtay = random.randint(22, 36)
            # print(dtay)
            self.y.append(dtay)
            ax.plot(self.x, self.y)
            canvas.draw()
            self.afterHandler = self.window.after(100, drawTemp)

        drawTemp()

        def bye():
            plt.close('all')
            new_window.destroy()
            self.window.mainloop()

        new_window.protocol("WM_DELETE_WINDOW", bye)

        # 窗口循环显示
        new_window.mainloop()

    def createHumWindow(self):
        """
        创建新的窗口
        """
        new_window = self.window
        new_window.title("湿度折线图")
        new_window.geometry("720x480")
        # Button(new_window,
        #        text="This is new window").pack()

        # 创建一个容器, 没有画布时的背景
        frame = Frame(new_window, bg="#ffffff")
        frame.place(x=0, y=0, width=720, height=480)
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        fig = plt.figure(figsize=(6, 3.9), edgecolor='blue')
        # 定义刻度
        ax = fig.add_subplot(111)
        ax.set(xlim=[0, 121], ylim=[30, 100], title="湿度折线图", ylabel='湿度/°C')
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        # 显示画布
        canvas.get_tk_widget().place(x=0, y=0)

        # 定义存储坐标的空数组
        self.i = 0
        self.x = []
        self.y = []

        def drawHum():
            global humData
            self.i += 1
            # time.sleep(1)
            ax.clear()
            ax.set(xlim=[0, 121], ylim=[30, 100], title="湿度折线图", ylabel='湿度/%')
            t = self.i
            if t >= 120:
                bye()
            dtax = t
            self.x.append(dtax)
            # 湿度数据处理
            """
            xxxxxxxxxxxxxxxxxxxxx
            """
            dtay = random.randint(40, 80)
            # print(dtay)
            self.y.append(dtay)
            ax.plot(self.x, self.y)
            canvas.draw()
            self.afterHandler = self.window.after(100, drawHum)

        drawHum()

        def bye():
            plt.close('all')
            new_window.destroy()
            self.window.mainloop()

        new_window.protocol("WM_DELETE_WINDOW", bye)

        # 窗口循环显示
        new_window.mainloop()

    def power(self):
        new_window = self.window
        new_window.title("温湿度串口调试助手")
        new_window.geometry("450x520+{}+{}".format(self.window.winfo_screenwidth() // 3, self.window.winfo_screenheight() // 5))
        frame = Frame(new_window, bg="#ffffff")
        frame.place(x=0, y=450, width=450, height=70)
        imgShow = PhotoImage(file='data\\blog.gif', master=new_window)
        # https://cdkm.com/cn/png-to-gif
        Label(new_window, image=imgShow).place(x=0, y=0, width=450, height=450)
        Label(new_window, text="扫码升级", bg="#ffffff", font='宋体', anchor="center").place(x=190, y=470)
        new_window.mainloop()


# if __name__ == "__main__":
#     mySerial = zsh_serial()
#     mySerial.ui()

# 参考资料：
# https://blog.csdn.net/MrV2020/article/details/105623659
# https://www.jianshu.com/p/9d55350bfe32
