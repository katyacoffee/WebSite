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


no_pic = 'NONE'
sep = '|'
dir_path = pathlib.Path.cwd()
data_path = Path(dir_path, 'mysite', 'data', 'data.txt')
res_path = Path(dir_path, 'mysite', 'data', 'results.txt')
users_path = Path(dir_path, 'mysite', 'data', 'users.txt')
print(str(data_path))


class ServerDownException(Exception):
    pass


def get_cards(lesson_id: int) -> list[Card]:
    f = open(data_path, 'r')
    res = []
    for line in f:
        line_data = line.split(sep)
        if len(line_data) < 5:
            continue
        i = int(line_data[0])
        if i != lesson_id:
            continue
        res.append(Card(i, line_data[1], line_data[2], line_data[3], line_data[4]))
    return res


def get_all_cards() -> list[Card]:
    i = 1
    res = []
    while i < 100:
        data = get_cards(i)
        if len(data) == 0:
            break
        res.extend(data)
        i += 1
    return res


def cards_to_tuple(cards: list[Card]):
    res = []
    for card in cards:
        res.append([card.lesson_id, card.lesson, card.word, card.translation])
    return res


def cards_to_tuple_with_pics(cards: list[Card]):
    res = []
    for card in cards:
        pic = "Null.png"
        if card.pic_name != "NONE":
            pic = card.pic_name
        res.append([card.lesson_id, card.lesson, card.word, card.translation, pic])
    return res


def add_cards(cards: list[Card]) -> None:
    f = open(data_path, 'a')
    if len(cards) > 0:
        f.write('\n')
    for card in cards:
        line = f'{card.lesson_id}' + sep + \
               card.lesson + sep + \
               card.word + sep + \
               card.translation + sep + \
               card.pic_name + sep
        f.write(line)


def get_lessons():
    i = 1
    res = []
    while i < 100:
        data = get_cards(i)
        if len(data) == 0:
            break
        res.append([data[0].lesson_id, data[0].lesson])
        i += 1
    return res


def new_user(user: str, pwd: str):
    f = open(users_path, 'a')
    f.write(user + sep + pwd + '\n')
    f.close()


def get_users() -> {str: str}:
    f = open(users_path, 'r')
    res = {}
    lines = f.read().splitlines()
    for line in lines:
        line_data = line.split(sep)
        if len(line_data) != 2:
            continue
        res[line_data[0]] = line_data[1]
    return res


def get_all_logins() -> list[str]:
    res = []
    for user in get_users().keys():
        res.append(user)
    return res


def get_password(user: str) -> str | None:
    user_passes = get_users()
    if user not in user_passes:
        return None
    return user_passes[user]


def get_all_results() -> {str: list[float]}:
    f = open(res_path, 'r')
    res = {}
    lines = f.read().splitlines()
    for line in lines:
        line_data = line.split(sep)
        if len(line_data) < 2:
            continue
        results = []
        for i, r in enumerate(line_data):
            if i == 0:
                continue
            try:
                r = float(r)
            except ValueError:
                r = 0.0
            results.append(r)
        res[line_data[0]] = results
    return res


def get_all_results_int_percent() -> {str: list[int]}:
    all_res = get_all_results()
    res = {}
    for user in all_res.keys():
        int_res = []
        for value in all_res[user]:
            int_res.append(int(value*100))
        res[user] = int_res
    return res


def get_all_stats():
    all_res = get_all_results_int_percent()
    res = []
    for user in all_res.keys():
        user_res = all_res[user]
        if len(user_res) == 0:
            continue
        res.append([user, sum(user_res), sum(user_res)//len(user_res),
                    max(user_res), min(user_res)])
    return res


def add_result(user: str, lesson_id: int, points: float):
    all_results = get_all_results()
    if user not in all_results.keys():
        user_results = []
        for _ in [1, lesson_id]:
            user_results.append(0.0)
        user_results.append(points)
        all_results[user] = user_results
    else:
        user_results = all_results[user]
        user_results[lesson_id-1] = points
        all_results[user] = user_results

    f = open(res_path, 'w')
    for u in all_results.keys():
        f.write(make_str_of_results(u, all_results[u]))
    f.close()


def make_str_of_results(user: str, results: list[float]) -> str:
    res = user
    for r in results:
        res += f'|{r}'
    res += '\n'
    return res


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
    img_list.sort(key=lambda pic: compare(get_station_name(pic)))

    return img_list


def get_img_list(yr: str, mon: str, day: str) -> list[str]:
    # base_dir = '/Users/ekaterinakozakova/Desktop/Data for Website'
    # base_dir = '\\192.168.9.49\Metronix\DataBase\Figures'

    server_dir = 'idg-comp.chph.ras.ru'
    base_dir_serv = '~mikhnevo/metronix/METRONIX_SDVamp'

    s = sess()
    data_path = base_dir_serv + '/' + yr + '/' + mon + '/' + day
    site = 'https://' + server_dir + '/' + data_path
    resp = s.get(site)
    img_list = get_images(resp)
    new_image_list = []
    for img in img_list:
        new_image_list.append('https://' + server_dir + '/' + data_path + '/' + img)
    return new_image_list


def get_available_days(year: str, mon: str) -> list[int]:
    days = []
    server_dir = 'idg-comp.chph.ras.ru'
    base_dir_serv = '~mikhnevo/metronix/METRONIX_SDVamp'

    s = sess()

    for i in range(1, 32):
        day = str(i)
        if len(day) == 1:
            day = '0' + day
        data_path = base_dir_serv + '/' + year + '/' + mon + '/' + day
        site = 'https://' + server_dir + '/' + data_path

        try:
            resp = s.get(site, timeout=2)
            print(resp)
            img_list = get_images(resp)
            new_image_list = []
            for img in img_list:
                new_image_list.append('https://' + server_dir + '/' + data_path + img)

            if len(new_image_list) != 0:
                days.append(i)
        except ConnectTimeout:
            raise ServerDownException('server down')
    return days
