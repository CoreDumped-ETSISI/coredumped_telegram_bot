#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from time import sleep
import datetime
import telepot
import os
import shutil
from logger import get_logger
from data_loader import DataLoader


def take_rtsp_screenshot(id):
    os.system('ffmpeg -i \"' + settings.cam_url(id) + '\" -y -f image2  -frames 1 ' + working_directory + '/snapshot.jpeg')


def take_rtsp_tagged_screenshot(cam_id, screenshot_number):
    os.system(
        'ffmpeg -i \"' + settings.cam_url(cam_id) +
        '\"  -y -f image2 -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf:'
        ' text="%{localtime}": x=15: y=h-(2*lh): fontcolor=white: box=1: boxcolor=0x00000000@1:'
        ' fontsize=20" -frames 1  -loglevel panic ' +
        working_directory + '/capturas/captura' + str(screenshot_number).zfill(5) + '.jpeg')


def make_movie():
    os.system(
        "ffmpeg -f image2 -loglevel panic -r 30 -i " +
        working_directory + "/capturas/captura%05d.jpeg"
                            " -vcodec mpeg4 -y " + working_directory + "/timelapse.mp4")


logger = get_logger(__name__)
settings = DataLoader()
working_directory = settings.working_directory

now = datetime.datetime.now()
video_caption = '[ ' + str(now.strftime('%y-%m-%d')) + " ]"


def make_gif(number_of_pictures):
    try:
        os.system('mkdir ' + settings.working_directory + '/capturas')

        for screenshot_number in range(1, number_of_pictures):
            time.sleep(10)
            take_rtsp_tagged_screenshot(0, screenshot_number)
            logger.debug(video_caption + " Capturando fotograma numero: " + str(screenshot_number))

        make_movie()

        bot = telepot.Bot(settings.telegram_token)
        video = open(working_directory + '/timelapse.mp4', 'rb')
        bot.sendVideo(chat_id=settings.president_chatid, video=video, caption=video_caption)
        video.close()

        os.remove(working_directory + '/timelapse.mp4')
        shutil.rmtree(working_directory + '/capturas')
    except Exception as ex:
        logger.exception("Error durante la creación del timelapse.")


if __name__ == "__main__":
    make_gif(3700)
