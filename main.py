#!/usr/bin/env python3
# ⇒ EV3上で実行するのに必要

# EV3に取り付けたLモータをソケット通信で信号を受信して回転させるサンプルプログラム

from ev3dev2.motor import LargeMotor, MoveTank, MoveSteering, SpeedPercent, OUTPUT_A, OUTPUT_B
from ev3dev2.display import Display 
from ev3dev2.sound import Sound

import socket
import sys
import time

received_message = None
server_port = 8001                  # 使用するポート

tank = MoveTank(OUTPUT_A, OUTPUT_B) # EV3のインスタンス
sound = Sound()                     # サウンドのインスタンス
display = Display()                 # ディスプレイのインスタンス

# IPアドレス取得
ip = socket.gethostbyname(socket.gethostname())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, server_port))
    s.listen(1)     # 1台のみと通信
    
    sound.speak("listen started")
    display.text_pixels(ip, True, 5, 5, font = "courB" + "14")  # 画面に文字を表示する
    display.update()

    while True:
        conn, addr = s.accept()
        sound.speak("connected")
        display.text_pixels(addr[0], False, 5, 20, font = "courB" + "14")
        display.update()
        with conn:
            while True:
                received_message = conn.recv(1024)
                if received_message is not None:
                    received_message = received_message.decode()
                    if received_message == "move":
                        tank.on_for_seconds(SpeedPercent(50), SpeedPercent(50), 3)
                    elif received_message == 'exit':
                        break
                    received_message = None
            sys.exit()

sys.exit()