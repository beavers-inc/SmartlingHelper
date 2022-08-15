from SmartlingCrawler import SmartlingCrawler
import datetime
import sys
from PasswordReader import PasswordReader
EXECUTE = '发送至Smartling'
EXECUTE_WAITING = '发送至Smartling，根据sku的数量，会有相当长的延迟，请耐心等待...'
ENTER = '确认'
LOGIN = '登录'
ID = 'ID'
PASSWORD = '密码'
FAIL_LOGIN = '登录失败'
TITLE = '小助手'
INSTRUCTION = '把Execl里的sku号粘贴在这里'
MESSAGE_LABEL = '历史记录'
TOTAL_COUNTER_LABEL = '总共已经接受sku数：'
import tkinter as tk
from tkinter import *
from tkinter import messagebox

class UI(tk.Tk):
    def __init__(self , *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title(string=TITLE)
        self.sc = SmartlingCrawler(self)
        self.password_reader = PasswordReader(self)
        self.total_counter = 0

        self.FrameLeft = tk.Frame()
        self.FrameRight = tk.Frame()

        self.FrameLeft.grid(row=0, column=0,sticky="news")
        self.FrameRight.grid(row=0, column=1, sticky="news")

        self.InputLabel = tk.Label(self.FrameLeft,text = INSTRUCTION)
        self.InputLabel.grid(row=0, column=0, sticky="news")

        self.InputField = tk.Text(self.FrameLeft)
        self.InputField.grid( row=1, column=0,sticky="news")

        self.messageLabel = tk.Label(self.FrameRight, text = MESSAGE_LABEL)
        self.messageLabel.grid( row=0, column=0,sticky="news")

        self.messageField = tk.Text(self.FrameRight)
        self.messageField.grid( row=1, column=0,sticky="news")
        self.messageField.config(state=DISABLED)

        self.total_counter_label = tk.Label(self.FrameRight, text = (TOTAL_COUNTER_LABEL+str(self.total_counter)))
        self.total_counter_label.grid( row=2, column=0,sticky="sew")

        self.Execute = tk.Button( self.FrameLeft,text=EXECUTE, command=self.execute)
        self.Execute.grid( row=2, column=0,sticky="sew")

        # self.test = tk.Button( self.FrameLeft,text='test', command=self.quit_all)
        # self.test.grid( row=3, column=0,sticky="sew")

        self.time = datetime.datetime

        self.name = ''
        self.password = ''
        self.check_password()

    def update_change(self):
        self.total_counter_label.config(text = (TOTAL_COUNTER_LABEL+str(self.total_counter)))


    def execute(self):
        self.accept_skus()
        self.update_change()


    def check_password(self):
        if (self.password_reader.hasFile == False or self.password_reader.correctPassword == False):
            self.create_password_window()
        elif self.password_reader.correctPassword == True:
            self.name = self.password_reader.name
            self.password = self.password_reader.password

    def create_password_window(self):
        self.withdraw()
        self.password_window  = Toplevel(self)
        self.password_window.title (LOGIN)
        self.password_window.attributes('-topmost', True)

        self.nameLabel = Label(self.password_window, text=ID)
        self.nameLabel.grid(row=0, column=0)

        self.nameField = tk.Text(self.password_window, height=1)
        self.nameField.grid(row=1, column=0)

        self.passwordLabel = Label(self.password_window, text=PASSWORD)
        self.passwordLabel.grid(row=2, column=0)

        self.passwordFeild = tk.Text(self.password_window , height=1)
        self.passwordFeild.grid(row=3, column=0)

        self.enterButton = Button(self.password_window, text=ENTER, command=self.get_password_ID)
        self.enterButton.grid(row=4, column=0)
        # self.enterButton.wait_variable(self.name)
        self.password_window.protocol("WM_DELETE_WINDOW", self.quit_all)


    def quit_all(self):
        self.quit()
        self.destroy()

    def get_password_ID(self):

        self.name=self.nameField.get("1.0", END).strip('\n')
        self.password=self.passwordFeild.get("1.0", END).strip('\n')
        if self.check_if_password_is_correct(self.name, self.password):
            self.password_reader.write_password_file(self.name,self.password)
            self.deiconify()
            self.password_window.destroy()
        else:
            self.popup(FAIL_LOGIN)


    def check_if_password_is_correct(self, name ,password):
        return self.sc.login( name,password)


    def display_message(self, message):
        self.messageField.configure(state='normal')
        self.messageField.insert('end', message)
        self.messageField.configure(state='disabled')

    def clear_message(self):
        self.messageField.configure(state='normal')
        self.messageField.delete('1.0', END)
        self.messageField.configure(state='disabled')

    @ staticmethod
    def popup(message):
        tk.messagebox.showinfo(message=message)

    def accept_skus(self):
        self.Execute.config(text=EXECUTE_WAITING)
        self.update()
        not_accepted_skus = []
        accepted_skus =[]
        unknown_error =[]

        skus_copy=self.InputField.get("1.0", END).strip()
        if len(skus_copy)>0:
            self.sc.login(self.name, self.password)

            skus_array = skus_copy.splitlines()
            skus_array =  list(filter(None, skus_array))
            sku_counter = 0

            if len(skus_array)>0:

                for each_sku in skus_array:
                    result = self.sc.add_one_sku(each_sku)
                    if result is True:
                        sku_counter+=1
                        accepted_skus.append(self.sc.current_sku)
                    elif result is False:
                        not_accepted_skus.append(self.sc.current_sku)
                    else:
                        unknown_error.append(self.sc.current_sku)
            message = str(self.time.now().strftime("%Y-%m-%d %H:%M:%S")) + '\n成功接受'+str(sku_counter)+'条sku'
            if len(not_accepted_skus)>0:
                message = message +'\n未找到sku，请手动确认：'
                for each_not_accepted_sku in not_accepted_skus:
                    message = message + '\n'
                    message = message+ each_not_accepted_sku
            if len(accepted_skus) > 0:
                self.total_counter = self.total_counter + len(accepted_skus)
                message = message +'\n已接受sku：'
                for each_accepted_sku in accepted_skus:
                    message = message + '\n'
                    message = message + each_accepted_sku
            if len(unknown_error) > 0:
                message = message + '\n已找到此sku，但接受sku时失败，请重试或手动添加：'
                for each_accepted_sku in unknown_error:
                    message = message + '\n'
                    message = message + each_accepted_sku
            message = message + '\n\n'
            self.display_message(message)
            self.popup('完成！')
        self.sc.clear()
        self.Execute.config(text=EXECUTE)



