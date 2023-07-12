#!/usr/bin/env python3
# ⇒ EV3上で実行するのに必要

# EV3に取り付けたLモータをソケット通信で信号を受信して回転させるサンプルプログラム

from ev3dev2.motor import LargeMotor, MoveTank, MoveSteering, SpeedPercent, OUTPUT_A, OUTPUT_B
from ev3dev2.display import Display 
from ev3dev2.sound import Sound

import socket
import sys
import time
import math

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
    # angle=90
    # time=7.77*angle
    # tank.on_for_seconds(SpeedPercent(100), SpeedPercent(-100), time/1000)
    while True:
        conn, addr = s.accept()
        sound.speak("connected")
        display.text_pixels(addr[0], False, 5, 20, font = "courB" + "14")
        display.update()
        with conn:
            while True:
                received_message = conn.recv(1024)
                received_message = received_message.decode()

                if received_message == "disconnect":  # "dissconect"の場合は、強制終了
                    print(received_message)
                    raise ValueError("disconnected")    # これじゃexceptに行かない・・・
                else:
                    positions = []  # 座標をここに保持
                    temp = received_message.split(",")  # カンマで区切る
                    for pos in temp:
                        positions.append(float(pos))    # floatに変換しながら保持
                    # print("Positions:")
                    # print(positions)
                    positions_num = (int)(len(positions) / 2)
                    display.text_pixels("Pos.Num.: " + str(positions_num), False, 5, 35, font = "courB" + "14")  # 画面に文字を表示する
                    display.update()

                    # ベクトルの算出
                    vectors = []
                    loop_num = (int)(len(positions) / 2)  - 1
                    cnt = 0
                    for i in range(0, loop_num):
                        vectors.append(positions[cnt + 2] - positions[cnt])
                        vectors.append(positions[cnt + 3] - positions[cnt + 1])
                        cnt = cnt + 2
                    # print("Vectors: ")
                    # print(vectors)

                    # 正規化
                    normalized_vectors = []
                    loop_num = (int)(len(vectors) / 2)
                    cnt = 0
                    for i in range(0, loop_num):
                        x = vectors[cnt]
                        y = vectors[cnt + 1]
                        norm = math.sqrt(x * x + y * y)
                        x = x / norm
                        y = y / norm
                        normalized_vectors.append(x)
                        normalized_vectors.append(y)
                        cnt = cnt + 2
                    # print("Normalized: ")
                    print(normalized_vectors)

                    # 角度の算出
                    angles = []
                    loop_num = (int)(len(normalized_vectors) / 2) - 1
                    cnt = 0
                    for i in range(0, loop_num):
                        # 内積から角度を算出
                        x1 = normalized_vectors[cnt]
                        y1 = normalized_vectors[cnt + 1]
                        x2 = normalized_vectors[cnt + 2]
                        y2 = normalized_vectors[cnt + 3]
                        cos_theta = (x1 * x2 + y1 * y2) / (math.sqrt(x1 * x1 + y1 * y1) * math.sqrt(x2 * x2 + y2 * y2))
                        theta_radian = math.acos(cos_theta)
                        theta_degree = theta_radian * (180 / math.pi)
                        # 外積から角度の正負を決める
                        dot_product =x1 * y2 - x2 * y1
                        if dot_product > 0:
                            direction = -1
                        else:
                            direction = 1
                        # 角度をリストに保持
                        angles.append(theta_degree * direction)
                        cnt = cnt + 2
                    # print("Angles(deg): ")
                    # print(angles)
                    display.text_pixels("Angles Num.: " + str(len(angles)), False, 5, 50, font = "courB" + "14")  # 画面に文字を表示する
                    display.update()
                    # ロボットを動かす
                    for angle in angles:
                        if angle > 0:
                            motor_a = -100
                            motor_b = 100
                        else:
                            motor_a = 100
                            motor_b = -100
                        time = 7.77 * abs(angle)
                        tank.on_for_seconds(SpeedPercent(motor_a), SpeedPercent(motor_b), time / 1000)
                        tank.on_for_seconds(SpeedPercent(-100), SpeedPercent(-100), 0.5)

                    # if received_message == "move":
                    #     tank.on_for_seconds(SpeedPercent(50), SpeedPercent(50), 3)
                    # elif received_message == 'exit':
                    #     break
                    received_message = None
            sys.exit()
        
sys.exit()