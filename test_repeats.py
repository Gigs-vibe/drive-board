"""Проверка repeats_today из app.py: конвертация дней недели Python(0=пн) → доска(0=вс)."""
import time, datetime

src = open(r"D:\Творчество\dist\app.py", encoding="utf-8").read()
ns = {"datetime": datetime}
exec(src[src.index("def repeats_today"):src.index("def reminder_loop")], ns)
repeats_today = ns["repeats_today"]

def lt(d):
    return time.localtime(time.mktime(d.timetuple()))

def ts(d):
    return time.mktime(d.timetuple())

mon, tue, wed = (datetime.date(2026, 8, d) for d in (24, 25, 26))
assert tue.strftime("%A") == "Tuesday", tue.strftime("%A")

w_tue = {"repeat": "weekly", "repeatDays": [2]}          # каждый вторник (JS getDay: вт=2)
assert repeats_today(w_tue, lt(tue), ts(tue)) is True, "вторник должен совпасть"
assert repeats_today(w_tue, lt(wed), ts(wed)) is False, "среда не должна совпасть"
assert repeats_today(w_tue, lt(mon), ts(mon)) is False, "понедельник не должен совпасть"

w_mon_thu = {"repeat": "weekly", "repeatDays": [1, 4]}   # пн и чт
assert repeats_today(w_mon_thu, lt(mon), ts(mon)) is True
assert repeats_today(w_mon_thu, lt(tue), ts(tue)) is False

start = datetime.date(2026, 8, 21)
n3 = {"repeat": "everyN", "repeatEvery": 3, "created": ts(start) * 1000}
got = [repeats_today(n3, lt(start + datetime.timedelta(days=o)), ts(start + datetime.timedelta(days=o)))
       for o in (0, 1, 2, 3, 6)]
assert got == [True, False, False, True, True], got

assert repeats_today({"repeat": "daily"}, lt(wed), ts(wed)) is True
assert repeats_today({"repeat": "weekly"}, lt(wed), ts(wed)) is False       # дни не заданы — не шлём
assert repeats_today({"repeat": "everyN", "repeatEvery": 3}, lt(wed), ts(wed)) is True  # без created — не молчим

print("OK: все проверки повторов прошли")
