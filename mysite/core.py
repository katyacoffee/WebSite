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
base_dir_serv_gps = '~mikhnevo/gnss/tec_rot/prego/png' #!!
base_dir_serv_lem = '~mikhnevo/LEMI018/PNG'
base_dir_serv_k_ind = '~mikhnevo/K-INDEX/PNG'
source_vlf = 'vlf'
source_tec = 'tec'
source_gps = 'gps'
source_lem = 'lem'
source_k_ind = 'k_ind'


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


# def get_par_lem() -> dict[str:int]:
#     return {
#         'VTX1': 16.3,
#     }


def get_station_name(pic: str) -> str:
    s = pic.split('_')
    return s[4]


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
#             print(img_list_k)
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


def get_img_list(yr: str, mon: str, day: str, source: str) -> list[str]:
    base_dir_serv = ''
    if source == source_vlf:
        base_dir_serv = base_dir_serv_vlf
    elif source == source_tec:
        base_dir_serv = base_dir_serv_tec
    elif source == source_gps:
        base_dir_serv = base_dir_serv_gps
    elif source == source_lem:
        base_dir_serv = base_dir_serv_lem
    elif source == source_k_ind:
        base_dir_serv = base_dir_serv_k_ind

    s = sess()
    data_path = ''
    if source == source_vlf or source == source_lem:
        data_path = base_dir_serv + '/' + yr + '/' + mon + '/' + day
        print(data_path)
    elif source == source_tec or source == source_gps or source == source_k_ind:
        data_path = base_dir_serv + '/' + yr + '/' + mon
    # elif source == source_k_ind:
    #     data_path = base_dir_serv
        # print(data_path)

    # print(data_path)
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
        #     print(r.status_code)
        resp = s.get(site, timeout=2)
        img_list = get_images(resp)
        img_list1 = []
        # TODO для gps!
        if source == source_vlf:
            img_list.sort(key=lambda pic: compare(get_station_name(pic)))
        elif source == source_lem:
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
        #     print("imglist", img_list)
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
        elif source == source_gps:
            no_data = True
            for pic in img_list:
                if get_day_from_gps_pic(pic) == int(day):
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
    if source == source_vlf:
        base_dir_serv = base_dir_serv_vlf
    elif source == source_tec:
        base_dir_serv = base_dir_serv_tec
    elif source == source_gps:
        base_dir_serv = base_dir_serv_gps
    elif source == source_lem:
        base_dir_serv = base_dir_serv_lem
    elif source == source_k_ind:
        base_dir_serv = base_dir_serv_k_ind

    with sess() as s:
        for i in range(1, 32):
            day = str(i)
            if len(day) == 1:
                day = '0' + day
            data_path = ''
            # TODO для gps!
            if source == source_vlf or source == source_lem:
                data_path = base_dir_serv + '/' + year + '/' + mon + '/' + day
            elif source == source_tec or source == source_gps or source == source_k_ind:
                data_path = base_dir_serv + '/' + year + '/' + mon
            # elif source == source_k_ind:
            #     data_path = base_dir_serv
            # elif source == source_gps:
            #     data_path = base_dir_serv + '/' + year + '/' + mon
            site = 'https://' + server_dir + '/' + data_path
            # print(site)

            try:
                if source == source_gps or source == source_lem or source == source_k_ind:
                    payload = {
                        'inUserName': 'guest',  # TODO! password!!
                        'inUserPass': 'qwe123'
                    }
                    r = s.post(site, data=payload)
                    # print(r.text)
                resp = s.get(site, timeout=2)
                # if i == 1: #TODO remove!
                print(resp.text)
                img_list = get_images(resp)
                if source == source_vlf:
                    img_list.sort(key=lambda pic: compare(get_station_name(pic)))
                elif source == source_lem:
                    img_list.sort()
                    print(img_list)
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
                #     print("imglist", img_list)
                #     img_list = get_img_k_index(img_list, year, mon)
                #     no_data = True
                #     for pic in img_list:
                #         if get_day_from_k_pic(pic) == int(day):
                #             img_list = [pic]
                #             no_data = False
                #             break
                #     if no_data:
                #         img_list = []
                    print("imglist2", img_list)
                elif source == source_tec:
                    no_data = True
                    for pic in img_list:
                        if get_day_from_tec_pic(pic) == int(day):
                            img_list = [pic]
                            no_data = False
                            break
                    if no_data:
                        img_list = []
                elif source == source_gps:
                    no_data = True
                    for pic in img_list:
                        if get_day_from_gps_pic(pic) == int(day):
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


def get_day_from_gps_pic(pic: str) -> int:
    a = pic.split('_')
    if len(a) < 5:
        return 0
    b = a[4].split('-')
    # num = a[5] # number of station?
    print(int(b[2]))
    return int(b[2])


def get_day_from_k_pic(pic: str) -> int:
    a = pic.split('_')
    if len(a) < 5:
        return 0
    return int(a[4])

