"""Проверка доставки обновлений: запасной путь в обход прокси + разбор релиза."""
import sys, json, urllib.request
sys.path.insert(0, r"D:\Творчество\dist")
import app

print("VERSION в коде:", app.VERSION)
print("прямая ссылка :", app.DIRECT_INSTALLER_URL)

# 1) запрос к GitHub API через нашу обёртку (системный прокси → при неудаче напрямую)
data = json.loads(app.fetch_url(f"https://api.github.com/repos/{app.GITHUB_REPO}/releases/latest", 15))
tag = data.get("tag_name")
asset = app.get_asset_url(data)
print("последний релиз:", tag, "| ассет:", (asset or "НЕ НАЙДЕН").split("/")[-1])
assert asset, "ассет TaskaSetup.exe не найден в релизе — авто-обновление сломается"

# 2) сравнение версий (локальная может быть новее выпущенной — это норма перед релизом)
assert app.parse_ver(tag) > (0,), f"тег релиза не разобрался: {tag}"
if app.parse_ver(app.VERSION) > app.parse_ver(tag):
    print(f"   (локальная {app.VERSION} новее выпущенной {tag} — ещё не релизили)")
assert app.parse_ver("v1.8.1") > app.parse_ver("1.7.6")
assert app.parse_ver("v1.10.0") > app.parse_ver("v1.9.9"), "двузначные версии сравниваются неверно"

# 3) имитация «прокси сломан»: первый opener заведомо нерабочий → должен помочь второй
real_openers = app._openers
app._openers = lambda: (urllib.request.build_opener(urllib.request.ProxyHandler({"https": "http://127.0.0.1:9"})),
                        urllib.request.build_opener(urllib.request.ProxyHandler({})))
try:
    d2 = json.loads(app.fetch_url(f"https://api.github.com/repos/{app.GITHUB_REPO}/releases/latest", 15))
    print("через битый прокси → запасной путь сработал, релиз:", d2.get("tag_name"))
finally:
    app._openers = real_openers

# 4) начало файла установщика по прямой ссылке — реально ли это exe (MZ)
head = app.fetch_url(app.DIRECT_INSTALLER_URL, 30)[:2]
print("первые байты установщика:", head)
assert head == b"MZ", "по прямой ссылке отдаётся не exe"

print("OK: обновления доступны и запасной путь работает")
