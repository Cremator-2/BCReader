#!/usr/bin/python
import cv2
import imutils
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
import argparse
import sys
import logging


def measure_time_processing(func):  # decorator

    from datetime import datetime

    def wrapper(*args, **kwargs):
        start_time = float(datetime.now().strftime('%S.%f'))
        f = func(*args, **kwargs)
        print(round(float(datetime.now().strftime('%S.%f')) - start_time, 3))
        return f
    return wrapper


def create_parser():

    parser = argparse.ArgumentParser()
    parser.add_argument('-frms', '--number_of_frames', nargs='?', default='1', type=int)
    parser.add_argument('-stp', '--step_rotation', nargs='?', default='15', type=int)
    parser.add_argument('-rot', '--number_of_rotations', nargs='?', default='5', type=int)
    parser.add_argument('-scl', '--scale', nargs='?', default='25', type=int)

    namespace = parser.parse_args(sys.argv[1:])

    return [namespace.number_of_frames,
            namespace.step_rotation,
            namespace.number_of_rotations,
            namespace.scale]


def start_logger():

    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    handler = logging.FileHandler('BCReader.log', mode='a')
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


@measure_time_processing
def cam_read_and_processing():

    frames = []

    for i in range(number_of_frames):
        _, img = cap.read()
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

    if len(barcodes) == 0:
        print('No read')
        logger.info(f'No read')
    else:
        for bc in barcodes:
            print(bc)
            logger.info(bc)


if __name__ == '__main__':

    [number_of_frames,
     step_rotation,
     number_of_rotations,
     scale] = create_parser()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    logger = start_logger()

    logger.info(f'Start program with arguments: -frms {number_of_frames} -stp {step_rotation} -rot '
                f'{number_of_rotations} -scl {scale}')

    try:
        while True:
            trig = input('Trigger: ')
            if trig == '1':
                cam_read_and_processing()
            if trig == '0':
                break

    except Exception as err:
        print(err)
        logger.error(err)
    finally:
        cap.release()
        cv2.destroyAllWindows()
