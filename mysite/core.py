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
base_dir_serv_gps = '~mikhnevo/GNSS/Prego/PNG' #!! https://idg-comp.chph.ras.ru/~mikhnevo/GNSS/Prego/PNG/2022/01/01/
base_dir_serv_javad_sigma = '~mikhnevo/GNSS/Sigma/PNG'
base_dir_serv_lem = '~mikhnevo/LEMI018/PNG'
base_dir_serv_k_ind = '~mikhnevo/K-INDEX/PNG'
base_dir_serv_meteo = '~mikhnevo/METEO/PNG/'
base_dir_serv_elf = '~mikhnevo/metronix/METRONIX_FULL/'
source_vlf = 'vlf'
source_tec = 'tec'
source_gps = 'gps'
source_javad_sigma = 'javad_sigma'
source_lem = 'lem'
source_k_ind = 'k_ind'
source_meteo = 'meteo'
source_elf = 'elf'


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
        'SRC1': 40.4,
        'SRC2': 42.5,
        'SRC3': 44.2
    }


def get_par_sat() -> dict[str:int]:
    return {
        'ROT': 1,
        'Lat': 2,
        'Lon': 3,
        'Elev': 4,
        'Az': 5,
    }


def get_freq_elf() -> dict[str:int]:
    return {
        'Hx_0-0.05': 10,
        'Hy_0-0.05':11,
        'Hx_0-0.4': 12,
        'Hy_0-0.4': 13,
        'Hx_0-4': 14,
        'Hy_0-4': 15,
        'Hx_0-50': 16,
        'Hy_0-50': 17,
        'Hz_0-50': 18,
        'Hx_50-100': 19,
        'Hy_50-100': 20,
    }


# def get_par_lem() -> dict[str:int]:
#     return {
#         'VTX1': 16.3,
#     }


def get_station_name(pic: str) -> str:
    s = pic.split('_')
    return s[4]


def get_station_name_gps(pic: str) -> str:
    s = pic.split('_')
    s2 = s[4].split('.')
    return s2[0]


def get_num_freq_elf(pic: str) -> str:
    s = pic.split('_')
    return f'{s[1]}_{s[2]}'


def get_par_name(pic: str) -> str:
    s = pic.split('_')
    if s[5] == 'en.png':
        return s[4]
    return ''
    # TODO переделать потом!


def get_k_ind_name(pic: str) -> str:
    s = pic.split('_')
    if s[5] == 'en.png':
        return pic
    return ''


# ВОЗМОЖНО ЭТО ПРИГОДИТСЯ ДЛЯ k-index
def get_img_k_index(img_list: list[str], year, mon) -> list[str]:
    img_list_k = []
    for im in img_list:
        s = im.split('_')
        if len(s) < 4:
            continue
        if int(s[2]) == int(year) and int(s[3]) == int(mon):
            img_list_k.append(im)
    return img_list_k


# ВОЗМОЖНО ЭТО ПРИГОДИТСЯ ДЛЯ k-index
# def get_img_k_index_for_day(img_list: list[str], year, mon, day) -> list[str]:
#     img_list_k = []
#     i = 0
#     for im in img_list:
#         s = im.split('_')
#         if len(s) < 5:
#             continue
#         if int(s[2]) == int(year) and int(s[3]) == int(mon) and int(s[4]) == int(day):
#             img_list_k.append(img_list[i-4])
#             img_list_k.append(img_list[i-2])
#             img_list_k.append(im)
#             img_list_k.append(img_list[i+2])
#             img_list_k.append(img_list[i+4])
#             return img_list_k
#             # помещаем две предыдущих из img_list + im + две следующих из img_list в список img_list_k
#             # и тут же делаем return img_list_k
#         i += 1
#     return img_list_k


def compare(st: str) -> str:
    st_dict = get_station_to_freq_dict()
    freq = st_dict.get(st)
    if freq is None:
        return 'b' + st
    return f'a{freq}'


def compare_sat(st: str) -> str:
    sat_dict = get_par_sat()
    num = sat_dict.get(st)
    # if num is None:
    #     return 'b' + st
    return f'{num}'


def compare_elf(st: str) -> str:
    par_dict = get_freq_elf()
    freq = par_dict.get(st)
    return f'{freq}'

# def sort_lem(par: str) -> str:
#     par_lem = par.sort()


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


def get_img_list(yr: str, mon: str, day: str, source: str, stat: int = 0) -> list[str]:
    base_dir_serv = ''
    if source == source_vlf:
        base_dir_serv = base_dir_serv_vlf
    elif source == source_tec:
        base_dir_serv = base_dir_serv_tec
    elif source == source_gps:
        base_dir_serv = base_dir_serv_gps
    elif source == source_javad_sigma:
        base_dir_serv = base_dir_serv_javad_sigma
    elif source == source_lem:
        base_dir_serv = base_dir_serv_lem
    elif source == source_k_ind:
        base_dir_serv = base_dir_serv_k_ind
    elif source == source_meteo:
        base_dir_serv = base_dir_serv_meteo
    elif source == source_elf:
        base_dir_serv = base_dir_serv_elf

    s = sess()
    data_path = ''
    if source == source_vlf or source == source_lem or source == source_meteo or source == source_gps or source == source_javad_sigma:
        data_path = base_dir_serv + '/' + yr + '/' + mon + '/' + day
    elif source == source_tec or source == source_k_ind or source == source_elf:
        data_path = base_dir_serv + '/' + yr + '/' + mon
    # elif source == source_elf:
    #     data_path = base_dir_serv + yr + '/' + mon
    # elif source == source_k_ind:
    #     data_path = base_dir_serv

    # elif source == source_gps:
    #     data_path = base_dir_serv + '/' + yr + '/' + mon

    new_image_list = []
    try:
        site = 'https://' + server_dir + '/' + data_path
        # if source == source_gps or source == source_lem:
        #     payload = {
        #         'inUserName': 'guest',  # TODO! password!!
        #         'inUserPass': 'qwe123'
        #     }
        #     r = s.post(site, data=payload)
        resp = s.get(site, timeout=2)
        img_list = get_images(resp)
        img_list1 = []

        if source == source_vlf:
            img_list.sort(key=lambda pic: compare(get_station_name(pic)))
        elif source == source_gps or source == source_javad_sigma:
            img_list.sort(key=lambda pic: compare_sat(get_station_name_gps(pic)))
        elif source == source_lem or source == source_meteo:
            for pic in img_list:
                if get_par_name(pic) != '':
                    img_list1.append(pic)
                    img_list1.sort()
            img_list = img_list1
        # elif source == source_k_ind:
        #     img_list = get_img_k_index_for_day(img_list, yr, mon, day)  # TODO: тут надо брать из get_img_k_index_for_day()
        #     # и no_data делать True только если img_list пустой
        #     if len(img_list) == 0:
        #         no_data = True
        #
        #     # for pic in img_list: # TODO: убрать
        #     #     if get_day_from_k_pic(pic) == int(day):
        #     #         img_list = [pic]
        #     #         no_data = False
        #     #         break
        #     else: # TODO: а тут наоборот условие
        #         no_data = False
        elif source == source_tec:
            no_data = True
            for pic in img_list:
                if get_day_from_tec_pic(pic) == int(day):
                    img_list = [pic]
                    no_data = False
                    break
            if no_data:
                img_list = []
        elif source == source_k_ind:
            no_data = True
            for pic in img_list:
                if get_day_from_k_pic(pic) == int(day):
                    img_list = [pic]
                    no_data = False
                    break
            if no_data:
                img_list = []
        elif source == source_elf:
            new_image_list1 = []
            no_data = True
            for pic in img_list:
                # print(get_day_from_elf(pic), int(day))
                if get_day_from_elf(pic) == int(day):
                    new_image_list1.append(pic)
                    no_data = False
            new_image_list1.sort(key=lambda pic: compare_elf(get_num_freq_elf(pic)))
            # print(new_image_list1)
            new_image_list = []
            for im in new_image_list1:
                new_image_list.append('https://' + server_dir + '/' + data_path + '/' + im)
                # no_data = False
            if no_data:
                img_list = []
            # new_image_list.sort(key=lambda pic: compare_elf(get_num_freq_elf(pic)))
            # print(new_image_list)

        if source != source_elf:
            for img in img_list:
                if (source == source_gps or source == source_javad_sigma) and get_sat_from_gps(img) != stat:
                    continue
                new_image_list.append('https://' + server_dir + '/' + data_path + '/' + img)
    except ConnectTimeout:
        raise ServerDownException('server down')
    return new_image_list


def get_available_days(year: str, mon: str, source: str) -> list[int]:
    days = []
    base_dir_serv = ''
    if source == source_vlf:
        base_dir_serv = base_dir_serv_vlf
    elif source == source_tec:
        base_dir_serv = base_dir_serv_tec
    elif source == source_gps:
        base_dir_serv = base_dir_serv_gps
    elif source == source_javad_sigma:
        base_dir_serv = base_dir_serv_javad_sigma
    elif source == source_lem:
        base_dir_serv = base_dir_serv_lem
    elif source == source_k_ind:
        base_dir_serv = base_dir_serv_k_ind
    elif source == source_meteo:
        base_dir_serv = base_dir_serv_meteo
    elif source == source_elf:
        base_dir_serv = base_dir_serv_elf

    with sess() as s:
        for i in range(1, 32):
            day = str(i)
            if len(day) == 1:
                day = '0' + day
            data_path = ''
            # TODO для gps!
            if source == source_vlf or source == source_lem or source == source_meteo or source == source_gps or source == source_javad_sigma:
                data_path = base_dir_serv + '/' + year + '/' + mon + '/' + day
            elif source == source_tec or source == source_k_ind or source == source_elf:
                data_path = base_dir_serv + '/' + year + '/' + mon
            # elif source == source_k_ind:
            #     data_path = base_dir_serv
            site = 'https://' + server_dir + '/' + data_path

            try:
                if source == source_gps or source == source_javad_sigma or source == source_lem or source == source_k_ind:
                    payload = {
                        'inUserName': 'guest',  # TODO! password!!
                        'inUserPass': 'qwe123'
                    }
                    r = s.post(site, data=payload)
                resp = s.get(site, timeout=2)
                img_list = get_images(resp)
                if source == source_vlf:
                    img_list.sort(key=lambda pic: compare(get_station_name(pic)))
                elif source == source_lem or source == source_meteo:
                    img_list.sort()
                # TODO для LEMI
                elif source == source_k_ind:
                    no_data = True
                    for pic in img_list:
                        if get_day_from_k_pic(pic) == int(day):
                            img_list = [pic]
                            no_data = False
                            break
                    if no_data:
                        img_list = []
                # elif source == source_k_ind:
                #     img_list = get_img_k_index(img_list, year, mon)
                #     no_data = True
                #     for pic in img_list:
                #         if get_day_from_k_pic(pic) == int(day):
                #             img_list = [pic]
                #             no_data = False
                #             break
                #     if no_data:
                #         img_list = []
                elif source == source_tec:
                    no_data = True
                    for pic in img_list:
                        if get_day_from_tec_pic(pic) == int(day):
                            img_list = [pic]
                            no_data = False
                            break
                    if no_data:
                        img_list = []
                elif source == source_elf:
                    no_data = True
                    for pic in img_list:
                        if get_day_from_elf(pic) == int(day):
                            img_list = [pic]
                            no_data = False
                            break
                    if no_data:
                        img_list = []

                if len(img_list) != 0:
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


def get_day_from_elf(pic: str) -> int:
    a = pic.split('_')
    if len(a) < 5:
        return 0
    b = a[0].split('-')
    if len(b) < 1:
        return 0
    return int(b[2])


def get_sat_from_gps(pic: str) -> int:
    a = pic.split('.')
    if len(a) != 4:
        return 0
    b = a[2]
    if len(b) < 5:
        return 0
    sat = b[3:5]
    sat_int = 0
    try:
        sat_int = int(sat)
    except Exception:
        return 0
    return sat_int


def get_day_from_k_pic(pic: str) -> int:
    a = pic.split('_')
    if len(a) < 5:
        return 0
    return int(a[4])


