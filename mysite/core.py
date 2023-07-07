from dataclasses import dataclass
import pathlib
from pathlib import Path
import http.client as https
from requests import Session as sess
from requests.models import Response
from requests import ConnectTimeout


@dataclass
class Card:
    lesson_id: int
    lesson: str
    word: str
    translation: str
    pic_name: str


server_dir = 'idg-comp.chph.ras.ru'
base_dir_serv_vlf = '~mikhnevo/metronix/METRONIX_SDVamp'
base_dir_serv_tec = '~madrigal/IMG/WorldPlotAnim'
base_dir_serv_gps = '~madrigal/IMG/WorldPlotAnim' #!!
source_vlf = 'vlf'
source_tec = 'tec'
source_gps = 'gps'


class ServerDownException(Exception):
    pass


def get_station_to_freq_dict() -> dict[str:int]:
    return {
        'VTX1': 16.3,
        'JXN': 16.4,
        'VTX2': 17,
        'HWU1': 18.3,
        'GBZ': 19.58,
        'NWC': 19.8,
        'ICV': 20.27,
        'FTA': 20.9,
        'HWU': 21.75,
        'GQD': 22.1,
        'DHO': 23.4,
        'NAA': 24,
        'NRK': 57.5,
        'GYW': 51.95,
        'GXH': 57.4,
        'NPM': 21.4,
        'TBB': 26.7,
        'A1F3': 29.7,
        'NSY': 45.9,
        'SXA': 49,
        'NDI': 54,
    }


def get_station_name(pic: str) -> str:
    s = pic.split('_')
    return s[4]


def compare(st: str) -> str:
    st_dict = get_station_to_freq_dict()
    freq = st_dict.get(st)
    if freq is None:
        return 'b' + st
    return f'a{freq}'


def get_images(response: Response) -> list[str]:
    if f'{response.status_code}' != '200':
        return []
    html_body = response.text
    tmp = html_body.split('alt="[IMG]"></td><td><a href="')
    img_list = []
    for i in range(1, len(tmp)):
        preparsed_dir = tmp[i].split("\"")
        if len(preparsed_dir) > 0:
            img_list.append(preparsed_dir[0])

    return img_list
# TODO: для других данных сделать условия


def get_img_list(yr: str, mon: str, day: str, source: str) -> list[str]:
    # base_dir = '/Users/ekaterinakozakova/Desktop/Data for Website'
    # base_dir = '\\192.168.9.49\Metronix\DataBase\Figures'

    base_dir_serv = ''
    print(source)
    if source == source_vlf:
        base_dir_serv = base_dir_serv_vlf
    elif source == source_tec:
        base_dir_serv = base_dir_serv_tec
    elif source == source_gps:
        base_dir_serv = base_dir_serv_gps
    print(base_dir_serv)

    s = sess()
    data_path = ''
    if source == source_vlf:
        data_path = base_dir_serv + '/' + yr + '/' + mon + '/' + day
    elif source == source_tec:
        data_path = base_dir_serv + '/' + yr + '/' + mon
    elif source == source_gps:
        data_path = base_dir_serv + '/' + yr + '/' + mon #!!

    new_image_list = []
    try:
        site = 'https://' + server_dir + '/' + data_path
        resp = s.get(site, timeout=2)
        img_list = get_images(resp)
        # TODO для gps!
        if source == source_vlf:
            img_list.sort(key=lambda pic: compare(get_station_name(pic)))
        elif source == source_tec:
            no_data = True
            for pic in img_list:
                if get_day_from_tec_pic(pic) == int(day):
                    img_list = [pic]
                    no_data = False
                    break
            if no_data:
                img_list = []

        for img in img_list:
            new_image_list.append('https://' + server_dir + '/' + data_path + '/' + img)
    except ConnectTimeout:
        raise ServerDownException('server down')

    return new_image_list


def get_available_days(year: str, mon: str, source: str) -> list[int]:
    days = []
    base_dir_serv = ''
    # print(source)
    if source == source_vlf:
        base_dir_serv = base_dir_serv_vlf
    elif source == source_tec:
        base_dir_serv = base_dir_serv_tec
    elif source == source_gps:
        base_dir_serv = base_dir_serv_gps

    s = sess()

    for i in range(1, 32):
        day = str(i)
        if len(day) == 1:
            day = '0' + day
        data_path = ''
        # TODO для gps!
        if source == source_vlf:
            data_path = base_dir_serv + '/' + year + '/' + mon + '/' + day
        elif source == source_tec:
            data_path = base_dir_serv + '/' + year + '/' + mon
        site = 'https://' + server_dir + '/' + data_path

        try:
            resp = s.get(site, timeout=2)
            img_list = get_images(resp)
            # TODO для gps!
            if source == source_vlf:
                img_list.sort(key=lambda pic: compare(get_station_name(pic)))
            elif source == source_tec:
                no_data = True
                for pic in img_list:
                    if get_day_from_tec_pic(pic) == int(day):
                        img_list = [pic]
                        no_data = False
                        break
                if no_data:
                    img_list = []

            new_image_list = []
            for img in img_list:
                new_image_list.append('https://' + server_dir + '/' + data_path + img)

            if len(new_image_list) != 0:
                days.append(i)
        except ConnectTimeout:
            raise ServerDownException('server down')
    return days


def get_day_from_tec_pic(pic: str) -> int:
    a = pic.split('_')
    if len(a) < 3:
        return 0
    b = a[2].split('.')
    if len(b) < 1:
        return 0
    return int(b[0])
