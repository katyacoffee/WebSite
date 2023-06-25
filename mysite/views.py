import ftplib
import os

from ftplib import FTP
from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponse
from . import terms_work, core
import json
import datetime
import http.client as https

# from bootstrap_datepicker_plus.widgets import DateTimePickerInput
# from django.views import generic
# from .models import Question # for calendar


unknown_guest = "unknown guest"


# class CreateView(generic.edit.CreateView):
#     model = Question
#     fields = ["question_text", "pub_date"]
#
#     def get_form(self):
#         form = super().get_form()
#         form.fields["pub_date"].widget = DateTimePickerInput()
#         return form # for calendar


def index(request):
    return render(request, "index.html")


def get_menu(request):
    return render(request, "menu.html")


def date_selection(request):
    return render(request, "date_selection.html")


def equipment(request):
    return render(request, "equipment.html")


def get_vlf_data(request):
    if request.method == "POST":
        cache.clear()
        date = str(request.POST.get("mydate"))
        context = {"mydate": date}
        parsed_date = date.split('/')
        if len(parsed_date) != 3:
            context["success"] = False
            context[
                "comment"] = "Неверный формат даты. Введите заново в формате DD/MM/YYYY"
            return render(request, "date_selection.html", context)
        day = parsed_date[0]
        mon = parsed_date[1]
        yr = parsed_date[2]
        if not day.isnumeric() or not mon.isnumeric() or not yr.isnumeric():
            context["success"] = False
            context[
                "comment"] = "Неверный формат даты. День, месяц и год должны быть числами"
            return render(request, "date_selection.html", context)
        day_int = int(day)
        mon_int = int(mon)
        yr_int = int(yr)
        try:
            try_date = datetime.date(yr_int, mon_int, day_int)
            context["success"] = True
            context["comment"] = ""
        except ValueError:
            context["success"] = False
            context["comment"] = "Введена несуществующая дата"
            return render(request, "date_selection.html", context)
        if context["success"]:
            context["success-title"] = ""
        print(date)
        print(len(date))
        # base_dir = '/Users/ekaterinakozakova/Desktop/Data for Website'
        # base_dir = '\\192.168.9.49\Metronix\DataBase\Figures'

        server_dir = 'idg-comp.chph.ras.ru'
        base_dir_serv = '~mikhnevo/metronix/METRONIX_SDVamp'
        data_path = base_dir_serv + '/' + yr + '/' + mon + '/' + day + '/'

        no_data = False

        connection = https.HTTPSConnection(server_dir)
        connection.request("GET", "/" + data_path)
        response = connection.getresponse()
        html_body = response.read().decode()
        tmp = html_body.split('alt="[IMG]"></td><td><a href="')
        img_list = []
        for i in range(1,len(tmp)):
            preparsed_dir = tmp[i].split("\"")
            if len(preparsed_dir) > 0:
                img_list.append(preparsed_dir[0])
        print(f'{response.status}')
        img_list.sort()
        print(img_list)

        new_image_list = []
        if f'{response.status}' == '200':
            for img in img_list:
                new_image_list.append('https://' + server_dir + '/' + data_path + img)
            if len(img_list) == 0:
                no_data = True
        else:
            no_data = True

        connection.close()

        context["images"] = new_image_list
        context["no_data"] = no_data
        context["num_pics"] = len(new_image_list)
        print(data_path)
        return render(request, "vlf_data.html", context)
    else:
        date_selection(request)


def contacts(request):
    words = core.cards_to_tuple(core.get_all_cards())
    return render(request, "contacts.html", context={"words": words})


def lessons(request):
    lessons = core.get_lessons()
    return render(request, "lessons.html", context={"lessons": lessons})


def cards(request):
    words = core.cards_to_tuple_with_pics(core.get_all_cards())
    return render(request, "cards.html", context={"words": words})


def test(request):
    words = core.cards_to_tuple(core.get_all_cards())
    return render(request, "test.html", context={"words": words})


def send_term(request):
    if request.method == "POST":
        cache.clear()
        user_name = request.POST.get("name")
        lesson_id = request.POST.get("lesson_id", "")
        lesson = request.POST.get("lesson", "")
        word = request.POST.get("new_term", "")
        translation = request.POST.get("new_definition", "").replace(";", ",")
        context = {"user": user_name}
        if len(translation) == 0:
            context["success"] = False
            context["comment"] = "Перевод должен быть не пустым"
        elif len(word) == 0:
            context["success"] = False
            context["comment"] = "Слово должно быть не пустым"
        elif len(lesson_id) == 0 or not lesson_id.isnumeric() or int(lesson_id) <= 0:
            context["success"] = False
            context["comment"] = "Номер урока должен быть целым положительным числом"
        elif len(lesson) == 0:
            context["success"] = False
            context["comment"] = "Тема урока должна быть не пустой"
        else:
            context["success"] = True
            context["comment"] = "Ваш термин принят"
            terms_work.write_word_with_translation(lesson_id, lesson, word, translation)
        if context["success"]:
            context["success-title"] = ""
        return render(request, "term_request.html", context)
    else:
        date_selection(request)


def send_answers(request):
    if request.method == "POST":
        cache.clear()
        lesson_id = request.POST.get("lesson_id")
        user_name = request.POST.get("user_login")
        if user_name == "":
            user_name = unknown_guest
        context = {"user": user_name, "lesson_id": lesson_id}
        cards_for_lesson = core.get_cards(int(lesson_id))
        context["success"] = True
        points = 0
        for card in cards_for_lesson:
            answer = request.POST.get("answer_" + card.word)
            if answer.lower() == card.word.lower():
                points += 1
        if context["success"]:
            context["success-title"] = "Тест успешно заполнен"
            context["comment"] = "Тест пройден с результатом " + \
                                 f'{points}/{len(cards_for_lesson)}'
            if user_name is not unknown_guest:
                core.add_result(user_name, int(lesson_id), points / len(cards_for_lesson))
        return render(request, "test_request.html", context)
    else:
        date_selection(request)


def submit_login(request):
    data = json.loads(request.body)
    user = data['title']
    pwd = data['body']
    if user == "":
        return HttpResponse("Имя пользователя не заполнено.")
    print(user, pwd)
    correct_pwd = core.get_password(user)
    if correct_pwd is None:
        return HttpResponse("Пользователь '" + user +
                            "' не найден. Пожалуйста, зарегистрируйтесь.")
    elif correct_pwd != pwd:
        return HttpResponse("Неверный пароль для пользователя '" + user + "'!")
    return HttpResponse("TRUE")


def submit_register(request):
    data = json.loads(request.body)
    user = data['title']
    pwd = data['body']
    if user == "":
        return HttpResponse("Имя пользователя не заполнено.")
    print(user, pwd)
    all_users = core.get_all_logins()
    if user in all_users:
        return HttpResponse("Пользователь уже зарегистрирован.")
    if len(pwd) < 3:
        return HttpResponse("Пароль слишком короткий.")
    core.new_user(user, pwd)
    return HttpResponse("TRUE")


def show_stats(request):
    all_res = core.get_all_stats()
    return render(request, "stats.html", context={"results": all_res})

# def sign_in(request):
#     users = core.get_all_logins()
#     return render(request, "equipment.html", context={"users": users})
