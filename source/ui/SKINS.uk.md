# Вікна дерева («скини»): контракт

*[English](SKINS.md)*

Екран дерева досліджень (меню 135) -- ОДИН скрипт, `OZL_TreeMenu`, що малює сім вікон фракцій:
`ecolog`, `clearsky`, `duty`, `freedom`, `sop`, `bandit`, `neutral`. Вікно -- це скин: його розкладки,
картинки, кольори й шрифти і невеликий клас скрипта з даними й гачками. Меню знаходить віджети за
**ролями** (іменами) і заповнює знайдене; ролі, якої в розкладці нема, просто не малює. Тут усе, що
потрібно авторові скину, крім мокапа власника і [`STRINGS.md`](STRINGS.md). `neutral` («Записник
сталкера») -- готовий приклад: читайте його файли поруч із цим текстом.

## Файли скину

Задача скину володіє рівно цим і більше нічого не править:

| Файл | Що |
|---|---|
| `OpenZone_Research/scripts/5_Mission/OpenZone_Research/OZL_TreeSkin_<Name>.c` | клас скину (дані + гачки) |
| `ui/OpenZone_Research/ozl_tree_<skin>.json` | опис вікна; усі шаблони рядків списків -- в ньому |
| `ui/OpenZone_Research/ozl_node_<skin>.json` | опис вузла |
| `OpenZone_Research/gui/layouts/ozl_tree_<skin>.layout`, `ozl_node_<skin>.layout`, `ozl_<skin>_<row>.layout` | згенеровані з двох описів (`python -m dayz_mcp.layoutgen <repo> OpenZone_Research`) |
| `ui/tokens/<skin>.json` | кольори й шрифти скину; кожне ім'я починається з `<skin>_` |
| `source/ui/<skin>/` | маніфест запікання (`sprites.json`) і його CSS |
| `OpenZone_Research/gui/imagesets/ozl_<skin>.imageset`, `ozl_<skin>_ca.paa`, `gui/textures/tree/<skin>/` | запечене з маніфесту (`python source/ui/bake.py <skin>`) |

Спільне, НЕ для правки скином: `OZL_TreeMenu.c`, `OZL_TreePlan.c`, `OZL_TreeLines.c`,
`OZL_TreeSkin.c` (базовий клас і фабрика), `OZL_Text.c`, `ozl_tree_host.json`, набір `ozl_common`
(`source/ui/common/`), `config.cpp`, `stringtable.csv`, `dayz-mcp.toml`, файли інших скинів. Треба
новий гачок, роль чи рядок -- просіть контролера: зміна йде в спільні файли один раз для всіх.

Токени шаруються: `[build] tokens` у `dayz-mcp.toml` -- спершу файл ядра, далі сім файлів скинів.
Пізніший файл замінює однойменний запис ЦІЛИМ (шрифт повторює `face`, `size` і `fixed`); префікс
`<skin>_` розводить сім файлів.

## Як з'являється вікно

1. Власна розкладка меню -- хост (`ozl_tree_host`): затемнений екран, «Дерево завантажується...»,
   невидима рамка-проба.
2. Сервер відповідає деревом і `OZL_TreeView.Skin`, уже розв'язаним до одного з семи.
3. `OZL_TreeSkins.Make(id)` створює скин; меню створює `ozl_tree_<skin>.layout` У ХОСТІ. Вікно, чиєї
   розкладки ще немає (`FileExist` бачить і файли в pbo) або чия розкладка не дає віджетів (задача
   ще не зроблена), падає на `neutral` з одним рядком
   `[OpenZone/Research] tree: window '<id>' has no layout yet ...`; id, якого клієнт не знає, --
   рядок ERROR і теж `neutral` (захист, а не режим).
4. Ролі шукаються раз (`menu.Role(name)`, у кеші), іде `skin.OnShow(menu)`, далі кожна відповідь
   малює: шапку, гілки, пул, дерево, реєстр, картку, `skin.OnPaint(menu)`.

Вікно створюється заново лише при зміні скину; вибраний вузол і гілка переживають оновлення.

## Одиниці -- виміряні, не вгадуйте

Усе в цьому контракті -- в **одиницях розкладки вікна 1600x900** (сцена мокапа). На екрані заввишки
H пікселів одна одиниця -- `H / 1080` пікселя. Виміряно на стенді 2026-10-31 (3840x1600, 1,48 пікселя
на одиницю; і 1920x1080):

- `SetPos` / `SetSize` зі скрипта беруть **пікселі екрана** (`SetPos(100)` посунув віджет на 100 px
  і при 1600 рядках, і при 1080: там це 67,5 одиниці, тут 100) -- і для віджетів розкладки, і для
  створених `CreateWidgets`.
  `GetScreenPos` / `GetScreenSize` віддають пікселі. Тож меню переводить: `menu.PlaceUnits(w, x, y)`,
  `menu.SizeUnits(w, w, h)`, `menu.UnitsOf(w, out w, out h)` -- користуйтеся ними, не голими числами.
- Позиції прокрутки (`HScrollToPos`, `GetVScrollPos`) -- пікселі.
- `CanvasWidget.DrawLine` малює в пікселях від лівого верхнього кута канви; канва 3230 x 1659 px
  (дерево 2180 x 1120 одиниць) малює до самого краю.
- `FrameWidget` обрізає дітей своїм краєм, якщо в розкладці не сказано `clipchildren 0`. Меню знімає
  це з комірки вузла, контейнерів NodeHit і рядків підписів, тож мітка може виступати з комірки.

## Дерево: план і геометрія

`OZL_TreePlan` розкладає вибрану гілку за геометрією скину (спека §3; `SKINS` мокапа):

| Поле | Зміст |
|---|---|
| `Dir` | `"down"`, `"up"` або `"right"`: куди росте дерево |
| `NodeW`, `NodeH` | розмір ФОРМИ вузла (куди чіпляються лінії) |
| `Keep` | місце під підписом поперек смуги; 0 -- половина вузла |
| `Row`, `Col` | крок між тирами вздовж і між вузлами поперек |
| `Top`, `Side`, `Shift` | місце до першого тиру; поля поперек; зсув групи поперек |
| `AnchorX`, `AnchorY` | центр форми ВСЕРЕДИНІ комірки вузла |

Тири видимих вузлів ідуть уздовж за зростанням; у тирі вузли -- за середньою позицією вже
розставлених батьків (рівні -- за `Index`). Точка вузла -- `(u, v)`, `u = Top + Row x (номер тиру + 1/2)`;
розмір вмісту -- `max(вид, Side x 2 + Col x найширший тир)` поперек, `max(вид, Top + тирів x Row + 40)`
вздовж, плюс місце під туман, коли в гілці є приховані вузли. `(u, v)` стає `(x, y)`: вниз `(v, u)`,
вгору `(v, H - u)`, вправо `(u, v)`. Меню ставить кожну комірку в `(x - AnchorX, y - AnchorY)` у
`TreeNodes` і дає `TreeContent` розмір плану.

«Додому», коли вікно відкрилось чи змінилась гілка: вниз -- верх, вгору -- низ, вправо -- лівий край;
поперек -- середина. Натиснути й тягнути по дереву -- прокрутка (зсув понад 4 одиниці робить
відпускання перетягуванням, а не кліком); колесо прокручує саме.

## Ролі вікна (`ozl_tree_<skin>.layout`, корінь `TreeWindow`)

Корінь може бути на весь екран (neutral: стіл плиткою і `TreeStage` 1600x900 по центру).

### Дерево

| Роль | Тип | Що робить меню |
|---|---|---|
| `TreeScroll` | ScrollWidget (`clipchildren 1`, `"Scrollbar V"`/`"Scrollbar H"` за бажанням) | його розмір -- вид; «додому», перетягування; одна дитина -- `TreeContent` |
| `TreeContent` | FrameWidget, точний розмір | розмір за планом; діти нижче -- `size fill` (пропорційні), тож ідуть за ним |
| `TreeBg` | ImageWidget, fill | сюди вантажиться й показується `TreeBackground` адміна; без нього -- як у розкладці |
| `TreeTiers` | frame, fill | підписи тирів: рядки `tier_label` (дитина `TierText`), кут рядка -- у точці підпису (`x = 22` поперек, центр тиру вздовж) |
| `TreeLines` | CanvasWidget, fill, `ignorepointer 1` | сітка паперу (`GridStep`) і всі зв'язки (`OZL_TreeLines`); перемальовується на вибір, наведення, дані, розкладку |
| `TreeFogEdge` | картинка, необов'язкова | 80 одиниць переходу на початку туману; меню ставить і розтягує її за напрямком скину |
| `TreeFog` | panel чи картинка | решта туману після переходу |
| `TreeNodes` | frame, fill | комірки вузлів; написи `АБО` (рядки `or_label`, дитина `OrText`) кутом рядка на ромбі |
| `TreeTip` | frame, схований | над вузлом під мишею, завширшки з ТЕКСТ `TreeTipText` + 2 x `TipPadX`; діти `TreeTipEdge` (fill), `TreeTipBg` (відступ 1, розтягується), `TreeTipText` (на `TipPadX`, сталої ширини, ширший за будь-яку підказку -- див. «Шрифти»; решту обрізає рамка) |
| `TreeLegend` | будь-що | статична: шість пунктів легенди -- у розкладці. Neutral шикує їх за текстами: пункти лежать у контейнері `LegendRow`, а його `OnShow` кличе `menu.FlowLater(menu.Role("LegendRow"), 14, 0, false)` |

### Шапка

`BranchName` (текст), `BranchSub` (текст: `<фракція> · досліджено N з M`), `DevName` (статичний, ключ
у розкладці), `BtnClose` (кнопка).

### Списки -- шаблони рядків `ozl_<skin>_<row>.layout`

Контейнер списку -- будь-який віджет, у який меню може створювати рядки (`stack` = WrapSpacer, або
stack `list`). Шаблони рядків оголошуються як `rows` якогось `list` в описі вікна; рядки поза
списками (підписи тирів і АБО, чіпи ціни) -- на схованому списку `TreeTemplates`.

| Контейнер | Рядок | Діти, що заповнює меню |
|---|---|---|
| `BranchList` | `branch_row` | `RowHit` (кнопка, перейменована на `branch:<id>`; без неї -- корінь рядка), `RowName`, `RowCount` (`зроблено / усього`), `RowPick` (на відкритій гілці), `RowBar`/`RowBarFill` (частка зробленого) |
| `PoolList` | `pool_row` | через `PaintPoolRow`: `PoolChip` (колір лінії), `PoolName`, `PoolValue`, `PoolSeg0`..`PoolSeg9` (горять = є / найбільша ціна одного вузла), що додасть скин; `PoolEmpty` (необов'язковий) -- коли ліній нема |
| `CardCostList`, `CardItemList` | `cost_row` | через `PaintCostRow`: `CostChip`, `CostName`, `CostValue` (`є / треба`, або `треба`, коли заплачено чи невідомо), `CostBar`/`CostBarFill` |
| `CardOpensList` | `opens_chip` | у ряд зліва направо з переносом; ширину дає перша текстова дитина (`ChipText`); `ChipHit` (перейменований на `open:<id>`) і `ChipLine` розтягуються на неї; у чіпа прихованого вузла `ChipHit` нема |
| `Registry` | `registry_row` | `RegNum` (`Index + 1`, дві цифри), `RegName`, `RegTier`, `RegState`, `RegPick`; корінь -- `reg:<id>`; рядок прихованого вузла -- `— невідомо —` |
| `TreeTiers` | `tier_label` | `TierText` |
| `TreeNodes` | `or_label` | `OrText` |
| `NodePrice` (у вузлі) | `price_chip` | `PriceChip` (колір лінії), `PriceText` (число); хвіст `+N предм.` -- ще один чіп із прихованим `PriceChip` |

### Картка

`CardEmpty` (коли нічого не вибрано) / `CardBody`; `CardName`, `CardMeta`
(`тир N · після: … / після всіх: … / після будь-якого з: …`, приховані батьки -- `невідомо`),
`CardStatus` (слово й колір від скину), `CardDesc`; заголовки розділів `CardDescHead`, `CardCostHead`,
`CardItemsHead`, `CardTimeHead`, `CardOpensHead` (текст із `SectionText`; `CardItemsHead`/`CardItemList`
ховаються, коли вузол не коштує матеріалів, `CardOpensHead`/`CardOpensList` -- коли нічого не
відкриває); `CardTime`, `CardTimer` (голий годинник, поки йде дослідження); `CardSegs` +
`CardSeg0`..`CardSeg19` або `CardBar`/`CardBarFill`; `BtnResearch` (+ `BtnResearchText`,
`BtnResearchHover` під мишею, поки кнопка активна) -- видна завжди; `CardWhy` (чому кнопка неактивна,
відмова сервера, «Запит надіслано...»); `CardStamp` + `CardStampImg` (`StampOf`); `CardScroll`
(прокручується вгору при кожному виборі) і `CardFlow` (stack, оновлюється після змін картки), якщо
картка прокручується.

**Текст із переносом.** `CardName`, `CardMeta`, `CardDesc` і `NodeName` вузла можуть бути ОДНИМ
TextWidget або контейнером написів `<Name>0`, `<Name>1`, … -- тоді меню переносить текст по словах у
ці написи (міряючи першим), ховає зайві й віддає останньому решту. З власними шрифтами мода беріть
контейнер: `MultilineTextWidget` і `RichTextWidget` ігнорують із ними `"exact text size"` і малюють
клітинкою атласу (48 чи 72 одиниці), виміряно 2026-10-31. Сховані написи у `stack` місця не займають.

## Ролі вузла (`ozl_node_<skin>.layout`, корінь `NodeCell`)

`NodeCell` -- комірка (перейменовується на `cell:<id>`); дайте їй місце на все, що виступає.

| Роль | Що |
|---|---|
| `NodeHit` | ЄДИНА ціль миші: кнопка зі `style Empty`, перейменована на `node:<id>`, під формою |
| `NodeShape` | ImageWidget; `Shapes` скину вантажаться в слоти 0..7, `ShapeOf` вибирає, `ShapeColorOf` фарбує |
| `NodeRing`, `NodeSel` | обведення доступного (`RingShown`) і вибраного |
| `NodeIcon` | власний значок вузла з конфігу дерева, фарбований `IconColorOf` |
| `NodeName` | текст або контейнер `NodeName0`, `NodeName1` (з переносом) |
| `NodePrice` | контейнер, у якому стають у ряд чіпи ціни (обрізає їх) |
| `NodePriceText` | простий текст замість чіпів: `Досліджено`, `Лишилось m:ss` або ціна, коли рядка чіпа нема |
| `NodeBar`/`NodeBarFill` | видно, поки йде дослідження; заповнюється на частку зробленого |
| `NodeMark`, `NodeMarkText` | слот `Marks` з `MarkOf`, слово з `MarkTextOf`, колір `MarkColorOf` |
| `NodeNum` | `Index + 1`, дві цифри |

### Правило миші (стенд, 2026-10-31)

`FrameWidget` без `ignorepointer 1` забирає мишу собі. У першому вузлі neutral назва й ціна були в
рамках: наведення й клік працювали лише на обідку картки, де `NodeHit` не був закритий. Тому:

1. У вузлі **кожен віджет, крім `NodeHit`, має `ignorepointer 1`**. В описі контейнери -- `panel` з
   `"color": "$none"` (генератор дає панелям `ignorepointer 1`, а рамкам ні); виняток -- лише
   контейнер, що тримає `NodeHit` (він під ним і бачить тільки поля комірки). Перевіряйте
   ЗГЕНЕРОВАНИЙ `.layout`, не лише опис.
2. Усе, що клацається, -- ButtonWidget зі `style Empty` (вузол `raw` з
   `"props": {"style": "Empty", "text": ""}`): кнопка без стилю малює під мишею світлий прямокутник.
3. Меню все одно стежить за пунктом 1: створивши комірку, ставить `IGNOREPOINTER` усьому, крім
   `NodeHit` і його контейнерів, і знаходить вузол за БУДЬ-ЯКИМ віджетом, про який йому скажуть,
   піднімаючись до `node:<id>` / `cell:<id>`. Рядки підписів (`tier_label`, `or_label`, `price_chip`)
   і `TreeTip` мишу пропускають повністю.

## Клас скину (`OZL_TreeSkin`)

Дані (у конструкторі; `Named("<id>")` заповнює імена розкладок): `Id`, `WindowLayout`, `NodeLayout`,
`RowPrefix`; геометрія вище; кольори ARGB -- `Txt`, `Dim`, `Acc`, `Ok`, `Bad`, `LineDim`, `LineLit`
(= Txt), `LineHl` (= Acc), `Lcd` (заливка ромба `АБО`), `FogColor`; `LineStyle` (`"plain"` / `"sketch"`),
`LineW` (2), `LineWHl` (2,5), `DashOn`/`DashOff` (6/5); `GridStep`, `GridColor`, `GridX`, `GridY`,
`GridW` (сітка паперу на канві; не малюється під задником адміна); `Shapes`, `ShapeHover` (слот під
мишею, -1 -- нема), `ShapeColors` (статус -> колір); `Marks`; `SegOn`, `SegOff` (0 = Acc / LineDim);
`TipPadX`.

Тримайте ці числа ARGB рівними `ui/tokens/<skin>.json` скину (рушій не читає JSON під час збирання).

Гачки -- кожен працює й без перекриття:

| Гачок | Типово |
|---|---|
| `int ShapeOf(status, selected)` | слот 0, якщо `Shapes` не порожній, інакше -1 (лишити картинку розкладки) |
| `int ShapeColorOf(status)` | `ShapeColors[status]`, інакше білий |
| `bool RingShown(status, selected)` | доступний і не вибраний |
| `int NameColorOf(status)` / `PriceColorOf` / `IconColorOf` / `StatusColorOf` | як у мокапі: закритий Dim, не вистачає Bad, доступний/іде Acc, досліджений Ok (назва: Txt, закритий Dim) |
| `int MarkOf(status)` / `string MarkTextOf(status)` / `int MarkColorOf(status)` | замок / галка / крапка = слоти `Marks` 0/1/2 для закритого / дослідженого / того, що йде; без тексту |
| `string StatusText(status)` | слово ключа статусу (`StatusKey`) |
| `string SectionText(key)` | слово ключа (папір дописує `:`, clearsky ставить `// `, скини з великими -- `OZL_Text.Upper`) |
| `string NodeNameText(name)` | назва (і в картці теж) |
| `string TierText(tier)` | `I`, `II`…; дерево вправо -- `тир I` |
| `void PaintNode(menu, cell, node, status, selected)` | форма, обведення, значок, назва, мітка, номер (ціна й смуга -- меню) |
| `void PaintPoolRow(menu, row, line, have, need, color)` | назва, число, чіп, сегменти |
| `void PaintCostRow(menu, row, label, text, verdict)` | назва, число кольором вироку (1 так / -1 ні / 0 невідомо), колір смужки |
| `void PaintButton(menu, btn, enabled)` | `BtnResearchText` Acc або Dim |
| `string StampOf(status)` | нема |
| `float DrawSegment(canvas, x1, y1, x2, y2, width, color, dashed, phase)` | прямий відрізок, пунктир 6/5 із фазою через усю ламану |
| `void DrawStroke(canvas, xs, ys, width, color, dashed, seed)` | ламана; `LineStyle "sketch"` -- `sketch()` мокапа (короткі штрихи зі зсувом і вигином, другий тонкий штрих), зерно -- id ребра, тож нічого не тремтить |
| `void DrawOrKnot` / `DrawAllKnot` | ромб `АБО` (заливка Lcd, обведений) / квадрат 10 одиниць -- товста `DrawLine` і є залитим прямокутником |
| `void OnShow(menu)` | -- (статичні тексти, запуск анімацій) |
| `void OnUpdate(menu, dt)` | -- (кожен кадр: бігучий рядок, мигання, мерехтіння) |
| `void OnPaint(menu)` | -- (після кожного повного малювання) |
| `void OnSelect(menu, node, status, canResearch)` | -- (node null -- нічого не вибрано) |
| `bool OnClick(menu, w)` | false (клік, якого меню не впізнало: кнопки помічника...) |

Помічники меню для гачків: `Role(name)`, `PlaceUnits`, `SizeUnits`, `UnitsOf`, `Px()`,
`PutText(w, text, color)` (текст у роль, з переносом, якщо вона -- контейнер), `FitLater(text, target,
pad, mode)` (наступним кадром: `target` завширшки з текст -- підкреслення, закреслення; mode 0 -- лишити
x, 1 -- прив'язаний праворуч, 2 -- по центру батька), `BarLater(track, fill, fraction)`,
`FlowLater(box, gap, pad, wrap)` (наступним кадром: діти контейнера зліва направо, кожна завширшки
від свого лівого краю до правого кінця свого першого видимого тексту -- `GetTextSize`, текст
вирівняний ліворуч -- плюс `pad`, далі `gap`), `PointName(line)`, `PointColor(line)`, `PoolOf(line)`,
`ItemLabel(item)`, `LeftOf(node)`, `View()`, `CurrentBranch()`, `BranchCount()`, `SelectedId()`,
`HoveredId()`, `NodeIdAt(widget)`. Рядки: `OZL_Text.Words(key)`, `OZL_Text.Upper(text)` (латиниця й
українська кирилиця; `і` стає латинською `I`), `Duration`, `Clock`, `Roman`, `Two`.

## Картинки

Усе, що мокап малює CSS, -- картинки, запечені: напишіть `source/ui/<skin>/sprites.json`
(див. [`README.uk.md`](README.uk.md)), запустіть `python source/ui/bake.py <skin>`, гляньте
`build/ui/<skin>/preview.png`, закомітьте маніфест разом з `.imageset` і `.paa`. Спрайт --
`set:ozl_<skin> image:<name>`; те, що фарбується, малюйте білим і фарбуйте в розкладці чи `SetColor`.
Розмір в imageset включає `pad`: показуйте у віджеті `w + 2 pad` на `h + 2 pad`, на `pad` вище й
лівіше. Великі шматки -- у `textures` (`gui/textures/tree/<skin>/<name>_ca.paa`); текстура без
`"stretch mode"` лягає плиткою свого піксельного розміру (стіл і пунктир neutral). Спільний набір
`ozl_common` має білі `mark_lock`, `mark_check`, `mark_dot`, `mark_wait`, `mark_query` (24x24),
`chip`, `and_square` (10x10), `or_diamond` (16x16). Текст іде в картинку лише повернутий чи
стилізований; тоді два спрайти `_uk`/`_en` і ключ `*_IMG` (STRINGS.md). Бюджет -- до 2048x2048 на
скин. Neutral: один атлас 1024x512 і три малі текстури (0,08 МБ).

## Шрифти

Бітмапові шрифти мода лежать в `OpenZone_Research/gui/fonts/` (див. `source/fonts/README.uk.md`): у
розкладці `font "OpenZone_Research/gui/fonts/ozl_hand48"` з `"exact text size"` = висота КЛІТИНКИ в
одиницях = round(px CSS x коефіцієнт клітинки обличчя). Кладіть їх у токени скину як шрифти. Вони
працюють у написах TextWidget; текст із переносом -- рядками-написами (вище).

**TextWidget обрізає свій текст своїм краєм, а `"w": "auto"` (`"size to text h"`) робить ширину
напису сумою кроків гліфів** (виміряно 2026-10-31). Остання літера похилого шрифту виходить за
свій крок і втрачає верхівку: у Caveat англійське `locked` малювалось як `lockea`, а `after all` --
як `after alı`, і в GridSpacer, і у WrapSpacer, і в простій рамці. Українські слова здебільшого
закінчуються літерами без такого виносу, тож дивіться англійською. Давайте такому напису ширину,
більшу за будь-який його текст, а решту міряйте й шикуйте за текстом (`FitLater`, `FlowLater` і
підказка міряють `GetTextSize`, а не напис): так роблять легенда neutral і `TreeTipText`. Напис
сталої ширини, текст якого закінчується далеко від правого краю, безпечний і так.

## Перевірка скину

`python -m dayz_mcp.layoutgen <repo> OpenZone_Research`, далі MCP `mod_lint`, `mod_build`,
`client_compile_check`, `server_start`, `log_verdict`; на стенді:
`world_exec verb=oz_research args={"op":"demo","owner":"<фракція>"}` і
`{"op":"treeui","owner":"<фракція>","as":"post"}` (as=post разом із заданим `Settings.ResearchPost`
дозволяє гравцеві тратити). Дивіться при 1920x1080 і 3840x1600, англійською й українською.
Наведіть справжню мишу на середину вузла (`ui_click via=cursor` на його назву): мають з'явитися
підказка й підсвічені зв'язки, а клік -- вибрати вузол.
