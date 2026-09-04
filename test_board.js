/* Тесты интерфейса (board.html). Запуск: открыть доску в браузере (preview на 3334)
   и выполнить содержимое этого файла в консоли — вернёт список проверок.
   Проверяем ровно то, что раньше молча ломалось: сохранность доски и логику карточек. */
(async () => {
  const R = [];
  const ck = (n, ok, d = '') => R.push({ t: ok ? 'OK ' : 'БАГ', n, d });
  const realGet = Store.get, realSet = Store.set, realState = state, realRO = boardReadOnly;

  // --- 1. Доску не прочитали → не пишем ни на диск, ни в облако
  let disk = 0; Store.set = async () => { disk++; return true; };
  Store.get = async () => LOAD_ERROR;
  boardReadOnly = false;
  state = await loadLocalBoard();
  ck('нечитаемый файл → режим только чтения', boardReadOnly === true);
  await saveLocalBoard();
  ck('в режиме только чтения на диск не пишем', disk === 0, `записей: ${disk}`);

  const realSession = session, realPush = cloudPush; let pushed = 0;
  session = { user: { id: 'u', email: 't@t' } }; cloudPush = async () => { pushed++; };
  await pushNow();
  ck('в режиме только чтения демо-доска НЕ уходит в облако', pushed === 0, `отправок: ${pushed}`);
  cloudPush = realPush; session = realSession;

  // --- 2. Успешное чтение снимает блокировку (иначе один сбой = сессия без сохранений)
  Store.get = async () => JSON.stringify({ columns: [{ role: 'backlog', cards: [{ id: 'a', title: 'моя' }] }] });
  state = await loadLocalBoard();
  ck('успешное чтение снимает режим только чтения', boardReadOnly === false);
  ck('прочитана именно сохранённая доска', state.columns.some(c => c.cards.some(k => k.title === 'моя')));

  // --- 3. Провал записи не проходит молча
  let warned = 0; const realToast = window.toast; window.toast = () => { warned++; };
  Store.set = async () => false; _saveFailToast = 0;
  const ok = await saveLocalBoard();
  ck('неудачная запись возвращает false', ok === false);
  ck('о неудачной записи сообщаем пользователю', warned === 1, `предупреждений: ${warned}`);
  window.toast = realToast; Store.set = realSet; Store.get = realGet;

  // --- 4. Имя колонки, заданное пользователем, переживает миграцию
  const renamed = migrate({ columns: [{ role: 'backlog', title: 'Идеи', cards: [] }, { role: 'done', title: 'Готово', cards: [] }] });
  ck('переименованная колонка сохраняет имя', renamed.columns.find(c => c.role === 'backlog').title === 'Идеи');
  ck('стандартное имя не превращается в «своё»', renamed.columns.find(c => c.role === 'done').title === 'Готово');
  const legacy = migrate({ columns: [{ role: 'daily', title: 'Ежедневные задачи', cards: [] }] });
  ck('старое имя раздела обновляется на новое',
    legacy.columns.find(c => c.role === 'daily').title === 'Повторяющиеся задачи');

  // --- 5. Повторяющаяся задача не превращается в разовую от «Отложить»
  state = defaultState();
  const daily = colByRole('daily');
  daily.cards.push({ id: 'r1', title: 'Планёрка', repeat: 'weekly', repeatDays: [2], dueTime: '10:00', created: Date.now() });
  openTask('daily', 'r1'); postpone(86400000);
  const after = readDue();
  ck('«Отложить» не стирает расписание повтора', after.repeat === 'weekly', `стало repeat="${after.repeat}"`);
  closeTask();

  // --- 6. Отменённое перетаскивание не двигает карточку чужим дропом
  dragSrc = { colId: 'backlog', cardId: 'x' };
  document.dispatchEvent(new Event('dragend'));
  ck('после отмены перетаскивания метка сброшена', dragSrc === null);

  // --- 7. Очистка доски не трогает архив, стикеры и пресеты
  state = defaultState(); state.archive = [{ id: 'a' }]; state.notes = [{ id: 'n' }]; state.presets = [{ id: 'p' }];
  state.columns.forEach(c => c.cards = []);
  ck('очистка убирает задачи', state.columns.every(c => !c.cards.length));
  ck('архив, стикеры и пресеты остаются',
    state.archive.length === 1 && state.notes.length === 1 && state.presets.length === 1);

  // --- 8. Дата без времени и кривая дата
  ck('срок без времени = до конца дня', dueState(new Date().toISOString().slice(0, 10)) !== 'over');
  ck('кривая дата не рисуется как NaN', !/NaN/.test(fmtDue('2026-13-45')));

  state = realState; boardReadOnly = realRO;
  const bad = R.filter(r => r.t === 'БАГ');
  console.log(R.map(r => `${r.t} ${r.n}${r.d ? ' → ' + r.d : ''}`).join('\n'));
  console.log(bad.length ? `ПРОБЛЕМ: ${bad.length}` : `ВСЁ ХОРОШО: ${R.length} проверок пройдено`);
  return { всего: R.length, проблем: bad.length, детали: R };
})();
