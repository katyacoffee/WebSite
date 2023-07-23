import ftplib
import os

from ftplib import FTP
from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponse
from . import terms_work, core
import json
import datetime
from datetime import date
# import pyzed as sl
import http.client as https


unknown_guest = "unknown guest"


def index(request):
    return render(request, "index.html")


def get_menu(request):
    return render(request, "menu.html")


def data(request):
    return render(request, "data.html")


def gps(request):
    if request.method == "POST":
        cache.clear()
        #stat = str(request.POST.get("stat"))
        new_stat = str(request.POST.get("new_stat"))
        print(new_stat)
        no_data = False
        # im_list = core.get_img_list(str(prev_yr), prev_mon_str, prev_day_str, source) # TODO - получать im_all и im_list !!
        im_all = 'test.jpg'
        im_list = ['test.jpg', 'test.jpg', 'test.jpg']
        context = {"success": True,
                   "new_stat": new_stat,
                   "im_all": im_all,
                   "images": im_list,
                   "no_data": no_data
                   }
        return render(request, "gps.html", context=context)
    return render(request, "index.html")


def date_selection(request):
    if request.method == "POST":
        cache.clear()
        source = request.POST.get("source")
        current_date = date.today()
        current_month = str(current_date.month)
        if len(current_month) == 1:
            current_month = '0' + current_month
        current_year = str(current_date.year)
        try:
            source = str(source)
            days = core.get_available_days(current_year, current_month, source)
            return render(request, "date_selection.html", context={
                "current_month": current_month,
                "current_year": current_year,
                "avail_days": days,
                "source": source,
            })
        except core.ServerDownException:
            return render(request, "date_selection.html", context={
                "server_error": 'some error',
                "current_month": 0,
                "current_year": 0,
                "avail_days": [],
                "source": source,
            })


def equipment(request):
    return render(request, "equipment.html")


def get_data(request):
    if request.method == "POST":
        cache.clear()
        source = str(request.POST.get("source"))
        date = str(request.POST.get("mydate"))
        new_year = request.POST.get("new_year")
        new_month = request.POST.get("new_month")
        new_day = request.POST.get("new_day")
        selected_new_month = request.POST.get("selected_new_month")
        button_name = request.POST.get("button_name")

        if source == core.source_gps:
            return gps(request)

        context = {
            "success": True,
            "source": source,
        }

        if button_name is not None:
            yr_int = int(new_year)
            mon_int = int(new_month)
            day_int = int(new_day)
            if button_name == 'next':
                nextday_date = datetime.date(yr_int, mon_int, day_int) + datetime.timedelta(days=1)
                next_day = nextday_date.day
                next_mon = nextday_date.month
                next_yr = nextday_date.year
                next_day_str = str(next_day)
                next_mon_str = str(next_mon)
                if len(next_day_str) == 1:
                    next_day_str = '0' + next_day_str
                if len(next_mon_str) == 1:
                    next_mon_str = '0' + next_mon_str
                im_list = core.get_img_list(str(next_yr), next_mon_str, next_day_str, source)
                no_data = False
                if len(im_list) == 0:
                    no_data = True
                context["current_day"] = next_day
                context["current_month"] = next_mon
                context["current_year"] = next_yr
                context["images"] = im_list
                context["no_data"] = no_data
            else:
                previous_date = datetime.date(yr_int, mon_int, day_int) - datetime.timedelta(days=1)
                prev_day = previous_date.day
                prev_mon = previous_date.month
                prev_yr = previous_date.year
                prev_day_str = str(prev_day)
                prev_mon_str = str(prev_mon)
                if len(prev_day_str) == 1:
                    prev_day_str = '0' + prev_day_str
                if len(prev_mon_str) == 1:
                    prev_mon_str = '0' + prev_mon_str
                im_list = core.get_img_list(str(prev_yr), prev_mon_str, prev_day_str, source)
                no_data = False
                if len(im_list) == 0:
                    no_data = True
                context["current_day"] = prev_day
                context["current_month"] = prev_mon
                context["current_year"] = prev_yr
                context["images"] = im_list
                context["no_data"] = no_data
            return render(request, "vlf_data.html", context)

        mon_str = str(int(new_month) + 1)
        if len(mon_str) == 1:
            mon_str = '0' + mon_str

        context = {
            "mydate": date,
            "avail_days": core.get_available_days(str(new_year), mon_str, source),
            "current_day": str(new_day),
            "current_month": str(int(new_month) + 1),
            "current_year": str(new_year),
            "source": source,
        }

        if selected_new_month != '':
            return render(request, "date_selection.html", context)

        parsed_date = date.split('/')
        if len(parsed_date) != 3:
            context["success"] = False
            # context[
            #     "comment"] = "Неверный формат даты. Введите заново в формате DD/MM/YYYY"
            context[
                "comment"] = "Invalid date format. Enter again in the format DD/MM/YYYY"
            return render(request, "date_selection.html", context)
        day = parsed_date[0]
        mon = parsed_date[1]
        yr = parsed_date[2]
        if not day.isnumeric() or not mon.isnumeric() or not yr.isnumeric():
            context["success"] = False
            # context[
            #     "comment"] = "Неверный формат даты. День, месяц и год должны быть числами"
            context[
                "comment"] = "Invalid date format. Day, month and year must be numbers"
            return render(request, "date_selection.html", context)
        if len(day) == 1:
            day = '0' + day
        day_int = int(day)
        mon_int = int(mon)
        yr_int = int(yr)

        try:
            datetime.date(yr_int, mon_int, day_int)
            context["success"] = True
            context["comment"] = ""
        except ValueError:
            context["success"] = False
            # context["comment"] = "Введена несуществующая дата"
            context["comment"] = "Invalid date entered"
            return render(request, "date_selection.html", context)
        im_list = core.get_img_list(str(yr), str(mon), day, source)
        if len(im_list) == 0:
            context["success"] = False
            # context[
            #     "comment"] = "В выбранном дне нет данных"
            context["comment"] = "There is no data for the selected day"
            return render(request, "date_selection.html", context)
        if context["success"]:
            context["success-title"] = ""

        no_data = False
        img_list = core.get_img_list(yr, mon, day, source)
        if len(img_list) == 0:
            no_data = True

        context["images"] = img_list
        context["no_data"] = no_data
        context["num_pics"] = len(img_list)
        context["current_day"] = day
        context["current_month"] = mon
        context["current_year"] = yr
        context["source"] = source
        return render(request, "vlf_data.html", context)
    else:
        date_selection(request)


def contacts(request):
    return render(request, "contacts.html")
