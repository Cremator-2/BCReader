#!/usr/bin/python
import cv2
import imutils
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
import argparse
import socket
import sys
from ximea import xiapi
import logging


def measure_time_processing(func):  # decorator

    from datetime import datetime

    def wrapper(*args, **kwargs):
        start_time = float(datetime.now().strftime('%S.%f'))
        f = func(*args, **kwargs)
        print(round(float(datetime.now().strftime('%S.%f')) - start_time, 3))
        return f
    return wrapper


def server_start_callback(func):  # decorator
    def wrapper(*args, **kwargs):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        print("IP: {}. Waiting connection...".format(s.getsockname()[0]))
        f = func(*args, **kwargs)
        print('Connection established')
        return f
    return wrapper


def create_parser():

    parser = argparse.ArgumentParser()
    parser.add_argument('-frms', '--number_of_frames', nargs='?', default='1', type=int)
    parser.add_argument('-stp', '--step_rotation', nargs='?', default='15', type=int)
    parser.add_argument('-rot', '--number_of_rotations', nargs='?', default='5', type=int)
    parser.add_argument('-p', '--port', nargs='?', default='1235', type=int)
    parser.add_argument('-scl', '--scale', nargs='?', default='25', type=int)
    parser.add_argument('-exp', '--exposure', nargs='?', default='8000', type=int)
    parser.add_argument('-g', '--gain', nargs='?', default='24', type=int)
    parser.add_argument('-t', '--start_trigger_type', nargs='?', default='tcp', type=str)

    namespace = parser.parse_args(sys.argv[1:])

    return [namespace.number_of_frames,
            namespace.step_rotation,
            namespace.number_of_rotations,
            namespace.port,
            namespace.scale,
            namespace.exposure,
            namespace.gain,
            namespace.start_trigger_type]


def start_logger():

    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    handler = logging.FileHandler('BCReader.log', mode='a')
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


def start_cam(exp: int, gain: int):

    xi_cam = xiapi.Camera()
    xi_cam.open_device()
    xi_cam.set_exposure(exp)
    xi_cam.set_gain(gain)
    xi_image = xiapi.Image()
    xi_cam.start_acquisition()
    xi_cam.set_param("gpi_mode", 'XI_GPI_TRIGGER')
    return xi_image, xi_cam


@server_start_callback
def start_server(p: int):

    sckt = socket.socket()
    sckt.bind(("", p))
    sckt.listen(1)
    cnct, addr = sckt.accept()
    logger.info('Connection established')
    return cnct, sckt


@measure_time_processing
def cam_read_and_processing():

    frames = []

    for i in range(number_of_frames):
        cam.get_image(xi_img)
        img = xi_img.get_image_data_numpy()
        img = frame_scale(scale, img)
        frames.append(img)

    decode(frames)


def frame_scale(scl: int, frm):

    width = int(frm.shape[1] * scl / 100)
    height = int(frm.shape[0] * scl / 100)
    dim = (width, height)
    frm = cv2.resize(frm, dim, interpolation=cv2.INTER_AREA)
    return frm


def decode(frames: list):

    barcodes = set()

    for frame in frames:

        frame_copy = frame.copy()

        for i in range(number_of_rotations):

            angle = i * step_rotation

            frame = imutils.rotate_bound(frame_copy, angle)
            decoded_objects = pyzbar.decode(frame, symbols=[ZBarSymbol.CODE128])
            for obj in decoded_objects:
                barcodes.add('<' + bytes.decode(obj.data) + '>')

    send(barcodes)


def send(bcs: set):
    if len(bcs) == 0:
        conn.send('<No read>'.encode())
        logger.info(f'No read')
    else:
        for bc in bcs:
            conn.send(bc.encode())
            logger.info(bc)


if __name__ == '__main__':

    [number_of_frames,
     step_rotation,
     number_of_rotations,
     port,
     scale,
     exposure,
     gain,
     start_trigger_type] = create_parser()

    logger = start_logger()
    xi_img, cam = start_cam(exposure, gain)
    conn, sock = start_server(port)

    logger.info(f'Start program with arguments: -frms {number_of_frames} -stp {step_rotation} -rot '
                f'{number_of_rotations} -p {port} -scl {scale} -exp {exposure} -g {gain} -t {start_trigger_type}')

    try:
        if start_trigger_type == 'tcp':

            while True:
                client_mes = conn.recv(1024).decode()
                if client_mes == 'Start':
                    cam_read_and_processing()
                if not client_mes:
                    logger.error('Connection closed by client')
                    sock.close()
                    conn, sock = start_server(port)
        elif start_trigger_type == 'gpio':
            while True:
                trig = cam.get_gpi_level()
                if trig == 1:
                    cam_read_and_processing()
        else:
            while True:
                trig = input('Trigger: ')
                if trig == '1':
                    cam_read_and_processing()

    except Exception as err:
        print(err)
        logger.error(err)
    finally:
        cam.stop_acquisition()
        cam.close_device()
        sock.close()
