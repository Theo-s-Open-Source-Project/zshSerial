import pyautogui
from tkinter.messagebox import *
from configparser import ConfigParser
import webbrowser


def window_capture():
    """
    截图
    """
    pyautogui.keyDown('win')
    pyautogui.keyDown('shift')
    pyautogui.press('s')
    pyautogui.keyUp('win')
    pyautogui.keyUp('shift')


class version:
    @staticmethod
    def info():
        Data = '使用方法：\n\n' \
               '1. 选择串口\n\n' \
               '2. 设置波特率、数据位、校验位\n\n' \
               '3. 接收设置\n\n' \
               '4. 打开串口\n' \
               '\n-----------------------------------------\n' \
               '\n详情：\n\n' \
               '1. UI 基于 tkinter 模块和其子模块 ttk 设计\n\n' \
               '2. 串口通信基于 pyserial 库\n\n' \
               '3. 折线图基于 matplotlib 库\n\n' \
               '4. GPL 3.0 许可，转载请注明来源 :)\n' \
               '\n-----------------------------------------\n\n' \
               'Version：       0.2.6\n' \
               'Maintained：theo@theotsang.xyz\n\n\n' \
               '\t  {}'
        showinfo('Info', Data.format(version.config()['power']))

    @staticmethod
    def config():
        """
        获取配置文件
        :return: 读取到的配置文件信息
        """
        config = ConfigParser()
        config.read("src\\config.ini")
        cfg = dict(config.items("config"))  # 字符串转换为字典
        # print(cfg)
        # print(cfg['version'])
        return cfg

    @staticmethod
    def update():
        """
        版本更新程序
        """
        webbrowser.open("https://github.com/Theo-s-Open-Source-Project/zshSerial")

