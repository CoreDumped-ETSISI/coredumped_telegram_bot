#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import re
from data_loader import DataLoader
from logger import get_logger

settings = DataLoader()
logger = get_logger("network_scan")
logger.setLevel(0)


def scan_for_devices():
    logger.info("scanning for devices")
    try:
        scan = subprocess.check_output(
            "echo \"" + settings.admin_password + "\" | sudo -S nmap -sP " + settings.network, shell=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    #p = re.compile(ur'(?:[0-9a-fA-F]:?){12}')
    p =  re.compile(ur'\d{1,3}\.\d{1,3}\.\d{1,3}\.1\d\d')
    return re.findall(p, scan)


def room_members_parser(people):
    answer_string = ""
    for member in people:
        answer_string += "- " + member + "\n"
    if answer_string == "":
        answer_string = "No parece haber nadie :'("
    else:
        answer_string = "Presentes:\n" + answer_string
    return answer_string
    
def room_ips_parser(people):
    answer_string = ""
    if len(people) == 0:
        answer_string = "No parece haber nadie :'("
    else:
        answer_string = "Hay "+ str(len(people)) +" dispositivos conectados al Wi-Fi." 
    print (answer_string)
    return answer_string


def scan_for_people_in_network():
    present_people = []
    parsed_answer = ""
    devices_macs = scan_for_devices()
    for mac in scan_for_devices():
        present_people.append(mac)
        print(mac)
    #    if mac in list(settings.devices.keys()):
    #present_people = sorted(set(present_people))
    #parsed_answer = room_members_parser(present_people)
    print("after loop")
    parsed_answer = room_ips_parser(present_people)
    print("after parser")
    return parsed_answer, present_people


def is_someone_there():
    who = scan_for_people_in_network()[1]
    return len(who) != 0


if __name__ == "__main__":
    print ("Bienvenido, se va a escanear la red.")
    print(scan_for_devices())
    print ("Adios")
