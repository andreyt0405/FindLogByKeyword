from colorama import Fore
from subprocess import call, Popen, TimeoutExpired
from terminaltables import DoubleTable
import adbutils
import multiprocessing
import time
import os
import sys
import json


def show_result(forbidden_dict):
    table_data = [forbidden_word for forbidden_word in forbidden_dict.keys()]
    table_result = [forbidden_res for forbidden_res in forbidden_dict.values()]
    TABLE_DATA = [
        table_data, table_result
    ]
    table_instance = DoubleTable(TABLE_DATA, "Test Results")
    table_instance.justify_columns[2] = 'right'
    input(f"{table_instance.table}")


def read_log(forbidden_list):
    project_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    fileBytePos = 0
    try:
        while True:
            inFile = open(os.path.join(project_path, 'log.txt'), 'rt', encoding="utf8", errors='ignore')
            inFile.seek(fileBytePos)
            data = inFile.read()
            for word in forbidden_list:
                print(f"{Fore.LIGHTCYAN_EX + data.casefold()} \
                " if str(word).casefold() not in data.casefold() else Fore.LIGHTRED_EX + data.casefold())
            fileBytePos = inFile.tell()
            inFile.close()
            time.sleep(0.25)
    except KeyboardInterrupt:
        print(Fore.RESET + "Stopped!")


def search_string():
    try:
        with open(os.path.join(running_path, 'log.txt'), 'rt', encoding="utf8", errors='ignore') \
                as log:
            forbidden_dict = dict(forbidden)
            for line in log.readlines():
                for word_log in line.split(' '):
                    for word_forbidden in forbidden_dict.keys():
                        if str(word_forbidden).casefold() in word_log.casefold():
                            forbidden_dict[word_forbidden] += 1
                            break
        show_result(forbidden_dict)
    except FileNotFoundError:
        print(f"{'File Not found or File were removed'}")


def init_logcat():
    clear_log()
    proc = multiprocessing.Process(target=read_log, args=(forbidden,))
    proc.start()
    try:
        with open(os.path.join(running_path, 'log.txt'), 'wt', encoding="utf8", errors='ignore') as f:
            call(['adb', 'logcat', ], stdout=f)
    except KeyboardInterrupt:
        search_string()


def clear_log():
    try:
        process = Popen(['adb', 'logcat', '-c'])
        process.wait(timeout=10)
        process.communicate()
    except TimeoutExpired:
        clear_log()


def open_json_file():
    return json.load(open(os.path.join(running_path, r'forbidden_word.json')))


def main():
    table_data = [
        ['Show Last Test Results', 'Start New Logcat'],
        ["Press 'Space+Enter'", "Press 'ENTER'"],
    ]
    table_instance = DoubleTable(table_data)
    table_instance.justify_columns[2] = 'right'
    print(table_instance.table)
    if not input():
        init_logcat()
    else:
        search_string()


if __name__ == '__main__':
    running_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
    forbidden = open_json_file()
    main()
