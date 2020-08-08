import datetime as dt

def today(request):
    date = dt.datetime.now()
    return {"today" : date}      