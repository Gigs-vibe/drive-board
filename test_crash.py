"""Проверка сохранности доски (критические баги 1-6 из БАГИ.md).
Работает на временных файлах — реальную доску не трогает."""
import sys, os, json, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app

TMP = tempfile.mkdtemp(prefix="taska-test-")
app.DATA_FILE = os.path.join(TMP, "drive-board.json")
app.NOTIFIED_FILE = os.path.join(TMP, "notified.json")
app.data_dir = lambda: TMP
api = app.Api()
BOARD = '{"columns":[{"role":"backlog","cards":[{"id":"a","title":"важная задача"}]}]}'
FAILED = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "БАГ  ") + name + (f"\n       → {detail}" if not cond and detail else ""))
    if not cond:
        FAILED.append(name)


def reset(content=BOARD):
    for suffix in ("", ".bak", ".tmp"):
        p = app.DATA_FILE + suffix
        if os.path.exists(p):
            os.remove(p)
    if content is not None:
        with open(app.DATA_FILE, "w", encoding="utf-8") as f:
            f.write(content)


# --- 1. Ошибка чтения не выдаётся за «доски нет»
reset(None)
check("нет файла → пустая строка (новый пользователь)", api.load() == "")

reset('{"columns":[{"role":"backl')  # обрыв записи
check("битый файл → признак ошибки, а не пустота", api.load() == app.LOAD_ERROR,
      f"вернул {api.load()!r}")

reset('{"columns":[{"role":"backl')
with open(app.DATA_FILE + ".bak", "w", encoding="utf-8") as f:
    f.write(BOARD)
check("битый файл + есть копия → поднимаем копию", "важная задача" in (api.load() or ""))

reset(None)
with open(app.DATA_FILE + ".bak", "w", encoding="utf-8") as f:
    f.write(BOARD)
check("файл пропал, копия есть → поднимаем копию", "важная задача" in (api.load() or ""))

# --- 2. Запись атомарна, прошлая версия уходит в .bak
reset()
api.save('{"columns":[{"role":"backlog","cards":[{"id":"b","title":"новая"}]}]}')
check("после записи в файле новая доска", "новая" in open(app.DATA_FILE, encoding="utf-8").read())
check("прошлая версия сохранена в .bak",
      os.path.exists(app.DATA_FILE + ".bak") and "важная задача" in open(app.DATA_FILE + ".bak", encoding="utf-8").read())
check("временный файл убран", not os.path.exists(app.DATA_FILE + ".tmp"))

reset()
before = open(app.DATA_FILE, encoding="utf-8").read()
for junk in (None, "", "не json", '{"нет":"колонок"}', '{"columns":[{"role":'):
    api.save(junk)
after = open(app.DATA_FILE, encoding="utf-8").read()
check("мусор и обрывки не попадают в файл", after == before, f"файл изменился: {after[:60]!r}")

# --- 4. Доска прежнего аккаунта откладывается в отдельный файл
reset()
api.archive_board("user-42")
copy = os.path.join(TMP, "drive-board-user-42.json")
check("archive_board делает копию доски прежнего аккаунта",
      os.path.exists(copy) and "важная задача" in open(copy, encoding="utf-8").read())
api.archive_board("../../побег")  # имя файла не должно выводить за папку
check("archive_board не даёт вырваться из папки данных",
      not any("побег" in n and os.sep in n for n in os.listdir(TMP)))

# --- целостность: сохранение → чтение по кругу
reset(None)
big = json.dumps({"columns": [{"role": "backlog", "cards": [{"id": str(i), "title": "з" * 200} for i in range(500)]}],
                  "notes": [{"id": "n", "text": "стикер"}]}, ensure_ascii=False)
t = time.time()
api.save(big)
got = api.load()
check("доска на 500 задач сохраняется и читается без потерь", got == big)
check("сохранение большой доски быстрее 300 мс", (time.time() - t) < 0.3, f"{int((time.time()-t)*1000)} мс")

print("\n" + ("ВСЁ ХОРОШО: критические сценарии потери доски закрыты" if not FAILED
              else f"ОСТАЛИСЬ ПРОБЛЕМЫ ({len(FAILED)}): " + "; ".join(FAILED)))
sys.exit(1 if FAILED else 0)
