import datetime


def dateToStr(date):
    return date.strftime("%Y-%m-%d")


def dateFromStr(dateStr):
    try:
        return datetime.datetime.strptime(dateStr, "%Y%m%d")
    except:
        return datetime.datetime.strptime(dateStr, "%Y-%m-%d")

