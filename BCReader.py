#!/usr/bin/python
import cv2
import imutils
from pyzbar import pyzbar
from datetime import datetime
import os
from pyzbar.pyzbar import ZBarSymbol
import socket
import sys
import argparse

# ====================================================================
# TCP/IP data exchange (Client)
# ====================================================================

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    Open
logging = True  # Logging
# ----------------------------------------------------------------------------------------------    Close

# Global frames its frames captured by the camera
# Local frame its a global frame area where supposedly locate barcode


def create_parser():

    parser = argparse.ArgumentParser()
    parser.add_argument('-frms', '--num_frames', nargs='?', default='1', type=int)
    parser.add_argument('-step', '--rotations_step', nargs='?', default='20', type=int)
    parser.add_argument('-rot', '--num_of_rotations', nargs='?', default='4', type=int)
    parser.add_argument('-ip', '--server_ip', nargs='?', default='192.168.0.40', type=str)
    parser.add_argument('-p', '--port', nargs='?', default='9090', type=int)
    return parser


def write2txt(text):

    title_log = datetime.now().strftime('%d-%m-%Y')
    name = 'log/log ' + title_log + '.txt'
    if not os.path.exists('log'):
        os.makedirs('log/decoded')
        os.makedirs('log/detected')
    if os.path.exists(name):
        with open(name, 'a') as f:
            f.write(text + '\n')
    else:
        with open(name, 'w') as f:
            f.write(text + '\n')


def draw_barcode(decoded, image, barcode):

    image = cv2.rectangle(image,
                          (decoded.rect.left, decoded.rect.top),
                          (decoded.rect.left + decoded.rect.width,
                           decoded.rect.top + decoded.rect.height),
                          color=(0, 0, 0),
                          thickness=2)
    image = cv2.putText(image, barcode,
                        (decoded.rect.left, decoded.rect.top - 10),
                        cv2.FONT_HERSHEY_DUPLEX, fontScale=2, color=(0, 0, 0),
                        thickness=2)

    return image


def decode(image, angle, num_local_frame, num_global_frame):

    decoded_objects = pyzbar.decode(image, symbols=[ZBarSymbol.EAN13,
                                                    ZBarSymbol.CODE128])

    num_barcode = 0
    barcode = b'None'
    type_barcode = 'None'

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    if logging:
        time = datetime.now().strftime('==== Angle: {} ===== Time: %H:%M:%S.%f %p ===='.format(angle))  # %f microsecond
        write2txt(time)
    # ----------------------------------------------------------------------------------------------

    for obj in decoded_objects:
        num_barcode = num_barcode + 1
        barcode = bytes.decode(obj.data)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if logging:
            # image = draw_barcode(obj, image, barcode)
            text = "#{}: Type: ".format(num_barcode) + obj.type + ' / Data: ' + barcode
            write2txt(text)

    if logging:
        time_now = datetime.now().strftime('%H-%M-%S.%f_%p %d-%m-%Y')
        image_path = 'log/decoded/{} {} correct {} {}.png'.format(num_global_frame, num_local_frame, angle, time_now)
        if num_barcode == 0:
            image_path = 'log/detected/{} {} incorrect {} {}.png'.format(num_global_frame,
                                                                         num_local_frame,
                                                                         angle, time_now)
            text = 'None'
            write2txt(text)

        cv2.imwrite(image_path, image)
    # ----------------------------------------------------------------------------------------------

    return [image, barcode, type_barcode, num_barcode]


def frame_rotation(frames, list_index_global_frms):

    count = 0
    num_barcode = 0

    while count < len(frames):

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if logging:
            text = '\n------------------------------ GlobalFrame: {} ------------------------------'.\
                format(list_index_global_frms[count])
            write2txt(text)
            text = '  ------------------------- LocalFrame: {} -------------------------\n'.format(count)
            write2txt(text)
        # ----------------------------------------------------------------------------------------------

        for i in range(num_of_rotations):
            angle = i * rotations_step

            rotated = imutils.rotate_bound(frames[count], angle)
            rotated, str_barcode, type_barcode, num_barcode = decode(rotated, angle, count,
                                                                     list_index_global_frms[count])

            if num_barcode > 0:
                # ====================================================================
                client_message = '<' + str_barcode + '>'
                print('Client: ' + client_message)
                sock.send(client_message.encode())
                # ====================================================================
                # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                if logging:
                    text = '\n=====================================================================\n'
                    write2txt(text)
                # ----------------------------------------------------------------------------------------------
                return

        count = count + 1

    if num_barcode == 0:
        # ====================================================================
        client_message = 'None decoded'
        print('Client: ' + client_message)
        sock.send(client_message.encode())
        # ====================================================================
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if logging:
            text = '\n=====================================================================\n'
            write2txt(text)
        # ----------------------------------------------------------------------------------------------


def cam_read_and_processing():

    count = 0
    frames = []  # list of local frames
    list_index_global_frms = []  # list of index of global frames with supposed barcode detected

    # Detecting supposed barcodes
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    while count < number_of_frames:

        _, img = cap.read()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        depth = cv2.CV_32F if imutils.is_cv2() else cv2.CV_32F
        grad_x = cv2.Sobel(gray, ddepth=depth, dx=1, dy=0, ksize=-1)
        grad_y = cv2.Sobel(gray, ddepth=depth, dx=0, dy=1, ksize=-1)

        gradient = cv2.subtract(grad_x, grad_y)
        gradient = cv2.convertScaleAbs(gradient)

        blurred = cv2.blur(gradient, (5, 5))  # <------ Setting
        _, thresh = cv2.threshold(blurred, 225, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))  # <------ Setting
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        closed = cv2.erode(closed, None, iterations=20)  # <------ Setting
        closed = cv2.dilate(closed, None, iterations=30)  # <------ Setting

        cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        indent = 30  # (px)
        width, height, _ = img.shape

        for cnt in cnts:

            x, y, w, h = cv2.boundingRect(cnt)

            x1 = x - indent
            if x1 < 0:
                x1 = 0
            y1 = y - indent
            if y1 < 0:
                y1 = 0
            x2 = x + w + indent
            y2 = y + h + indent

            frames.append(img[y1:y2, x1:x2])
            list_index_global_frms.append(count)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        count = count + 1

    if len(frames) > 0:
        frame_rotation(frames, list_index_global_frms)
    else:
        # ====================================================================
        client_message = 'None detected'
        print('Client: ' + client_message)
        sock.send(client_message.encode())
        # ====================================================================
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if logging:
            time = datetime.now().strftime('%H:%M:%S.%f %p')
            text = '\n=====================================================================\n'
            text += time + ' None detected'
            text += '\n=====================================================================\n'
            write2txt(text)
        # ----------------------------------------------------------------------------------------------


if __name__ == '__main__':

    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    number_of_frames = namespace.num_frames  # number of global frames
    rotations_step = namespace.rotations_step  # (deg)
    num_of_rotations = namespace.num_of_rotations
    server_ip = namespace.server_ip
    port = namespace.port

    sock = socket.socket()
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # exp_val = -13
        # cap.set(cv2.CAP_PROP_EXPOSURE, exp_val)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        print('Connecting to server...')
        sock.connect((server_ip, port))
        print('Connection established!')
        client_mes = 'Done'
        sock.send(client_mes.encode())

        while True:
            server_mes = sock.recv(1024).decode()
            print('Server: ' + server_mes)
            if server_mes == 'Go':
                cam_read_and_processing()
            if server_mes == 'Exit':
                break
            if server_mes != 'Go':
                client_mes = 'Unknown command'
                print('Client: ' + client_mes)
                sock.send(client_mes.encode())

    except Exception as err:
        print('Error: ', err)
    finally:
        sock.close()
