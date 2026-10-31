# String index of the research tree screen

Every user-visible text of the tree screen, for all seven skins, lives in
`OpenZone_Research/stringtable.csv`. This file is the index of those keys: what each
one holds and where the mockup uses it. The menu and the skin tasks read this file to
find a key, and should not need to edit the stringtable; if a text is truly missing,
add the row to the stringtable and to this index in the same commit.

Sources: the owner's mockup (`SKINS.<skin>.dev` and `stage`, the JS render functions,
the CSS `content:` texts) and the design `E:\openzone\docs\specs\2026-10-31-research-tree-skins-design.md` section 7.

## How the strings are stored

- The table keeps its header. `original` and every non-English column hold the
  Ukrainian text; `english` holds the English one (the series' rule).
- Ukrainian text uses the LATIN capital I (U+0049) wherever a Cyrillic capital І
  (U+0406) would stand: the vanilla fonts draw U+0406 as a missing glyph (skill,
  gui-layouts section 25). Lower-case і ї є and capital Ї Є Ґ are fine, except in a
  name the game upper-cases (the next point). The tables below show every value
  exactly as it is stored.
- Names the game upper-cases take the Latin i for the lower-case і. The `displayName` of
  every item, station, module, sample and carrier in `config.cpp`, and the `name` of an
  attachment group, reach the screen upper-cased: the vanilla inventory runs
  `GetDisplayName()` through `ToUpper` before a header (skill, gui-layouts section 25), and
  an upper-casing that knows Cyrillic -- OpenZone Storage's `OZS_Case` is one -- makes і
  (U+0456) the capital І (U+0406), a box in the Metron faces. So those keys store the LATIN
  i (U+0069) for every і, in `original` and in every non-English column (`english` is
  untouched): it looks the same and upper-cases to the Latin I. Descriptions (`..._desc`)
  are not upper-cased and keep the Cyrillic і; so does any key that only our own windows
  show, because their `OZL_Text.Upper` makes the Latin I itself. The price: a name matched
  by its Cyrillic spelling (a search box, a sort key) no longer equals the stored one.
- A value never holds an ASCII double quote (English uses 'single quotes'), a line
  break, or a glyph outside Latin, Cyrillic, `«»` `—` `·` `№` `©` and plain
  punctuation. Where the mockup used something else, the glyph is dropped or replaced;
  every such place is listed under "Dropped glyphs".
- The file is UTF-8 with a BOM and CRLF line ends. Edit it with Python, not `sed -i`.
- Read a key in script with `Widget.TranslateString("#" + key)` (what `OZL_TreeMenu.Words()`
  does); in a layout write `#STR_...`.
- Naming: `STR_OZL_TREE_*` is generic and serves every skin; `STR_OZL_SKIN_<SKIN>_*` belongs
  to one skin (SKIN is ECOLOG, CLEARSKY, DUTY, FREEDOM, SOP, BANDIT or NEUTRAL; `neutral` is
  the mockup's `loner`). Every faction has a skin of its own, so there is no key set for a
  base window.
- Keys that end in `_IMG` stand for text drawn as a picture (rotated or styled text). The value
  is a sprite reference, `set:ozl_<skin> image:<what>_ua` in the Ukrainian columns and
  `set:ozl_<skin> image:<what>_en` in the English one, so the stringtable picks the language.
  Load it like a node icon: `ImageWidget.LoadImageFile(0, Widget.TranslateString("#" + key))`.
  The bake manifest of that skin must produce both sprites, `<what>_ua` and `<what>_en`
  (`<what>` is the key suffix in lower case: `GRIF` is `grif`, `SEAL_DONE` is `seal_done`).
  Where the same words also exist as a plain-text key (`..._GRIF` beside `..._GRIF_IMG`),
  that is a text twin for previews and for a skin that has no sprite yet.
- Case. The values are in the natural case of the mockup's HTML. The mockup's CSS makes
  many of them upper case (`text-transform: uppercase`: titles, `.dev`, section heads, the
  card status, the button text, the registry of duty, node names of duty and sop); DayZ has no
  such transform and `ToUpper()` only knows ASCII. A skin that wants capitals needs an upper-casing
  helper that handles UTF-8 Cyrillic (a-я to А-Я, with і becoming the LATIN I, ї є ґ to
  Ї Є Ґ), or it shows the natural case. Strings that are capitals in the mockup's own source
  (`DUTY_CARD_HEAD`, `SOP_TARGET`) are stored as capitals.
- The roles in the "where" column (`DevName`, `CardWhy`, ...) are the widget roles of the design, section 4.

## Generic keys already in the file (reused)

Existing `STR_OZL_TREE_*` keys that the new screen uses as they are. Values are read from `stringtable.csv`.

| key | Ukrainian | English | where it is used |
|---|---|---|---|
| `STR_OZL_TREE_CLOSE` | `Закрити` | `Close` | all skins: close button (`BtnClose`) |
| `STR_OZL_TREE_BRANCHES` | `Гілки` | `Branches` | plain heading over the branch list where a skin wants one (freedom has its own MENU_BAR); also used by the screen being replaced |
| `STR_OZL_TREE_POINTS` | `Бали фракції` | `Faction points` | plain heading over the pool where a skin wants one (the skins of the mockup have their own); also used by the screen being replaced |
| `STR_OZL_TREE_TIER` | `тир` | `tier` | card meta `тир N`; horizontal trees (ecolog, sop) also label the tier columns `тир I` |
| `STR_OZL_TREE_AFTER` | `після` | `after` | older plain `після` (kept; the card now uses AFTER_ONE / AFTER_ALL / AFTER_ANY) |
| `STR_OZL_TREE_RESEARCH` | `Дослідити` | `Research` | `BtnResearchText` of an available node |
| `STR_OZL_TREE_PICK` | `Оберіть вузол` | `Pick a node` | card empty state, first line (`CardEmpty`) |
| `STR_OZL_TREE_HINT` | `Клацніть вузол, щоб побачити подробиці` | `Click a node for details` | card empty state, second line (`CardEmpty`) |
| `STR_OZL_TREE_LOADING` | `Дерево завантажується...` | `Loading the tree...` | host: shown until the answer of the server arrives |
| `STR_OZL_TREE_ASKING` | `Запит надіслано...` | `Request sent...` | hint line while a request is in flight |
| `STR_OZL_TREE_STARTED` | `Дослідження розпочато` | `Research started` | notice after a research was started |
| `STR_OZL_TREE_POOL_EMPTY` | `Пул фракції порожній` | `The faction pool is empty` | pool list when the faction has no points at all |
| `STR_OZL_TREE_COST` | `Вартість` | `Cost` | card section head over the cost rows (`Вартість`) |
| `STR_OZL_TREE_ITEMS` | `Матеріали` | `Materials` | card section head over the material rows (`CardItemsHead`) |
| `STR_OZL_TREE_TIME` | `Тривалість` | `Duration` | card: `Тривалість: 1 хв 00 с` (the script adds `: ` and the duration) |
| `STR_OZL_TREE_LEFT` | `Лишилось` | `Left` | researching: node price line `Лишилось 0:41`, card timer |
| `STR_OZL_TREE_INSTANT` | `Досліджується миттєво` | `Researched at once` | card time line of a node with no duration |
| `STR_OZL_TREE_LOCKED` | `Заблоковано` | `Locked` | status `locked`: card status, tooltip, registry |
| `STR_OZL_TREE_AVAILABLE` | `Доступно` | `Available` | status `available`: card status, tooltip, registry |
| `STR_OZL_TREE_RESEARCHING` | `Досліджується` | `Researching` | status `researching`: card status, tooltip, registry |
| `STR_OZL_TREE_COMPLETED` | `Досліджено` | `Completed` | status `completed`: card status, tooltip, registry; also the node price line of a done node and the button text of a done node |

## Generic keys (new)

Used by every skin; a skin only decides where to put them. Status words for the card, the tooltip and the registry:
`LOCKED`, `SHORT`, `AVAILABLE`, `RESEARCHING`, `COMPLETED` (all but `SHORT` are the reused keys above).

| key | Ukrainian | English | where it is used |
|---|---|---|---|
| `STR_OZL_TREE_SHORT` | `Не вистачає ресурсів` | `Not enough resources` | status `short` (the pool or the materials do not cover the cost): card status, tooltip, registry |
| `STR_OZL_TREE_DESC` | `Опис` | `Description` | card section head over the description; the mockup shows it in ecolog, duty and freedom only |
| `STR_OZL_TREE_OPENS` | `Відкриває` | `Opens` | card section head over the chips of the nodes this one opens (`CardOpensHead`) |
| `STR_OZL_TREE_UNKNOWN` | `невідомо` | `unknown` | card meta: the name of a parent that is not shown (`після всіх: Назва, невідомо`) |
| `STR_OZL_TREE_UNKNOWN_OPENS` | `??? невідомо` | `??? unknown` | card, "Відкриває": the chip of a hidden child (a `Hidden` stub — the next step only); not clickable |
| `STR_OZL_TREE_UNKNOWN_ROW` | `— невідомо —` | `— unknown —` | UNUSED since 2026-10-31 (the key stays): the registry lists only visible nodes — the owner's rule that no terminal tells how many technologies remain (SKINS.md, "What the player may know") |
| `STR_OZL_TREE_OR` | `АБО` | `OR` | the label beside the diamond of a dashed (`any`) connector, drawn on the tree |
| `STR_OZL_TREE_OR_TAG` | `(АБО)` | `(OR)` | tag after the name of an "opens" chip whose node opens after ANY parent |
| `STR_OZL_TREE_MORE_TAG` | `(+ ін.)` | `(+ others)` | tag after the name of an "opens" chip whose node needs several parents (mode all) |
| `STR_OZL_TREE_AFTER_ONE` | `після:` | `after:` | card meta, a node with one parent: `тир 2 · після: Назва` |
| `STR_OZL_TREE_AFTER_ALL` | `після всіх:` | `after all:` | card meta, several parents, mode all |
| `STR_OZL_TREE_AFTER_ANY` | `після будь-якого з:` | `after any of:` | card meta, several parents, mode any |
| `STR_OZL_TREE_RESEARCHED` | `досліджено` | `researched` | `BranchSub`: `<фракція> · досліджено 3 з 10` (lower case; the status word is COMPLETED; 10 = the visible nodes, never the branch total) |
| `STR_OZL_TREE_OF` | `з` | `of` | `BranchSub` (`3 з 10`) and the card timer (`Лишилось 0:41 з 1 хв 00 с`) |
| `STR_OZL_TREE_UNIT_S` | `с` | `s` | seconds in a duration: `45 с`, `1 хв 05 с` |
| `STR_OZL_TREE_UNIT_MIN` | `хв` | `min` | minutes in a duration |
| `STR_OZL_TREE_UNIT_H` | `год` | `h` | hours in a duration (not in the mockup, which stops at minutes; research may last longer) |
| `STR_OZL_TREE_ITEMS_TAIL` | `предм.` | `items` | node price line: the word after `+N` when the node also costs materials (`2 4 +3 предм.`) |
| `STR_OZL_TREE_WHY_BUSY` | `Проєкт уже йде` | `A project is already running` | `CardWhy` under the disabled button: status researching |
| `STR_OZL_TREE_WHY_LOCKED_ALL` | `Спершу дослідіть усі попередні вузли` | `Research all the previous nodes first` | `CardWhy`: status locked, parents mode all |
| `STR_OZL_TREE_WHY_LOCKED_ANY` | `Спершу дослідіть будь-який з попередніх вузлів` | `Research any of the previous nodes first` | `CardWhy`: status locked, parents mode any |
| `STR_OZL_TREE_WHY_SHORT` | `Не вистачає балів або матеріалів` | `Not enough points or materials` | `CardWhy`: status short |
| `STR_OZL_TREE_WHY_LEADER` | `Витрачати бали може лише лідер фракції` | `Only the faction leader can spend points` | `CardWhy`: status available but `MaySpend` is false |
| `STR_OZL_TREE_LEGEND_LOCKED` | `закрито` | `locked` | `TreeLegend` item 1: dashed swatch |
| `STR_OZL_TREE_LEGEND_SHORT` | `не вистачає` | `not enough` | `TreeLegend` item 2: the `bad` swatch |
| `STR_OZL_TREE_LEGEND_OPEN` | `доступно / іде проєкт` | `available / project running` | `TreeLegend` item 3: the `acc` swatch |
| `STR_OZL_TREE_LEGEND_DONE` | `досліджено` | `researched` | `TreeLegend` item 4: the `ok` swatch |
| `STR_OZL_TREE_LEGEND_ALL` | `після всіх` | `after all` | `TreeLegend` item 5: solid line ending in a square |
| `STR_OZL_TREE_LEGEND_ANY` | `після будь-якого` | `after any` | `TreeLegend` item 6: dashed line ending in a diamond |
| `STR_OZL_TREE_MARK_WORK` | `в ділі` | `in work` | node mark text of a researching node on the paper skins (bandit, neutral; the other skins use a sprite) |
| `STR_OZL_TREE_MARK_NEW` | `NEW!` | `NEW!` | node mark text of an available node on freedom (blinking) |

## Skin `ecolog`

Mockup window: ecolog -- «Науковий термінал» (the Scientists' lab terminal).

| key | Ukrainian | English | where it is used |
|---|---|---|---|
| `STR_OZL_SKIN_ECOLOG_DEV` | `Науковий термінал` | `Scientific terminal` | `DevName`: the device name in the header plate (mockup `SKINS.ecolog.dev`) |
| `STR_OZL_SKIN_ECOLOG_TITLE` | `Дерево досліджень` | `Research tree` | header plate title (`.ehead .title`) |
| `STR_OZL_SKIN_ECOLOG_POOL` | `Бали` | `Points` | label of the readouts row of the pool (`.readouts .lab`); the mockup turns it 90 degrees, so the skin draws POOL_VERTICAL_IMG instead and keeps this key as a text twin |
| `STR_OZL_SKIN_ECOLOG_POOL_VERTICAL_IMG` | `set:ozl_ecolog image:pool_vertical_ua` | `set:ozl_ecolog image:pool_vertical_en` | sprite reference: the vertical "Бали" / "Points" label of the readouts row |

## Skin `clearsky`

Mockup window: clearsky -- «Польовий КПК» (the Clear Sky field PDA).

| key | Ukrainian | English | where it is used |
|---|---|---|---|
| `STR_OZL_SKIN_CLEARSKY_DEV` | `Польовий КПК` | `Field PDA` | `DevName`: the device name in the floating branch panel (mockup `SKINS.clearsky.dev`) |
| `STR_OZL_SKIN_CLEARSKY_LEGEND_POOL` | `Легенда · бали` | `Legend · points` | heading of the floating legend/pool panel (`.h` in the stage) |
| `STR_OZL_SKIN_CLEARSKY_SEC_MARK` | `//` | `//` | prefix of every card section head (CSS `.sec::before` is `// ` with a trailing space; the skin adds the space) |

## Skin `duty`

Mockup window: duty -- «Реєстр досліджень» (the Duty form on the cloth).

| key | Ukrainian | English | where it is used |
|---|---|---|---|
| `STR_OZL_SKIN_DUTY_ORG_NAME` | `Долг` | `Duty` | form requisites, line 1 (bold): the organisation. The Ukrainian value keeps the original name Долг on purpose (CLAUDE.md rule 3a) |
| `STR_OZL_SKIN_DUTY_ORG_UNIT` | `Штаб · відділ забезпечення` | `HQ · supply department` | form requisites, line 2 (`.dorg`) |
| `STR_OZL_SKIN_DUTY_ORG_REF` | `Вих. № 0417/Д` | `Out. No. 0417/D` | form requisites, line 3: outgoing number (the number is typed text in the mockup) |
| `STR_OZL_SKIN_DUTY_GRIF` | `Для службового користування` | `For official use only` | the classification stamp (`.dsk`); the mockup draws it rotated in a box, so the skin shows GRIF_IMG and keeps this key as a text twin |
| `STR_OZL_SKIN_DUTY_GRIF_IMG` | `set:ozl_duty image:grif_ua` | `set:ozl_duty image:grif_en` | sprite reference: the rotated "Для службового користування" stamp |
| `STR_OZL_SKIN_DUTY_TITLE_IMG` | `set:ozl_duty image:title_ua` | `set:ozl_duty image:title_en` | sprite reference: the sheet title «Реєстр досліджень» with wide letter spacing, baked (live text cannot space letters) |
| `STR_OZL_SKIN_DUTY_FORM` | `Форма № 7-Д` | `Form No. 7-D` | top right corner of the sheet (`.dform`) |
| `STR_OZL_SKIN_DUTY_APPROVE` | `Затверджую` | `I approve` | approval block, line 1 (bold) |
| `STR_OZL_SKIN_DUTY_APPROVE_CMD` | `Командир ___________` | `Commander ___________` | approval block, line 2 (the blank is typed text) |
| `STR_OZL_SKIN_DUTY_APPROVE_DATE` | `«__» __________ р.` | `«__» __________ yr.` | approval block, line 3: the date blank |
| `STR_OZL_SKIN_DUTY_TITLE` | `Реєстр досліджень` | `Research register` | sheet title, spaced capitals (`.title`) |
| `STR_OZL_SKIN_DUTY_DIRECTION` | `напрям:` | `direction:` | line under the title: `напрям: <BranchName> · <BranchSub>` (`.dsub`) |
| `STR_OZL_SKIN_DUTY_REGISTRY_HEAD` | `1. Перелік робіт` | `1. List of works` | heading of the registry table (`.reg .h`) |
| `STR_OZL_SKIN_DUTY_COL_NUM` | `№ п/п` | `No.` | registry column 1 head (the mockup breaks the line after №) |
| `STR_OZL_SKIN_DUTY_COL_NAME` | `Найменування` | `Name` | registry column 2 head |
| `STR_OZL_SKIN_DUTY_COL_TIER` | `Тир` | `Tier` | registry column 3 head (capital T; the plain word is TREE_TIER) |
| `STR_OZL_SKIN_DUTY_COL_STATE` | `Стан` | `Status` | registry column 4 head; the cells hold the status words (LOCKED, SHORT, ...) |
| `STR_OZL_SKIN_DUTY_FUND_HEAD` | `2. Фонди фракції` | `2. Faction funds` | heading over the pool table |
| `STR_OZL_SKIN_DUTY_SCHEME_HEAD` | `3. Схема послідовності робіт` | `3. Work sequence diagram` | `DevName`: heading of the tree panel (mockup `SKINS.duty.dev`) |
| `STR_OZL_SKIN_DUTY_EXECUTOR` | `Виконавець ст. сержант ________ · тел. 2-14 · прим. № 1` | `Executor Sr. Sgt. ________ · tel. 2-14 · copy No. 1` | bottom line of the sheet (`.dform`; the rank blank is typed text) |
| `STR_OZL_SKIN_DUTY_CARD_HEAD` | `КАРТКА ДОСЛIДЖЕННЯ · ФОРМА № 7-Д/2` | `RESEARCH CARD · FORM No. 7-D/2` | first line of the clipped card (CSS `.c-head::before`); already capitals |
| `STR_OZL_SKIN_DUTY_SIGN` | `Підпис ____________  /Командир/` | `Signature ____________  /Commander/` | last line of the card above the handwritten signature (CSS `.c-foot::after`) |
| `STR_OZL_SKIN_DUTY_SEAL_DONE` | `Затверджено` | `Approved` | the round seal on a completed node (`CardStamp`); the skin shows SEAL_DONE_IMG, this key is the text twin |
| `STR_OZL_SKIN_DUTY_SEAL_DONE_IMG` | `set:ozl_duty image:seal_done_ua` | `set:ozl_duty image:seal_done_en` | sprite reference: the seal "ЗАТВЕРДЖЕНО" / "APPROVED" (`CardStampImg`) |
| `STR_OZL_SKIN_DUTY_SEAL_WORK` | `В роботі` | `In progress` | the round seal on a researching node; the skin shows SEAL_WORK_IMG, this key is the text twin |
| `STR_OZL_SKIN_DUTY_SEAL_WORK_IMG` | `set:ozl_duty image:seal_work_ua` | `set:ozl_duty image:seal_work_en` | sprite reference: the seal "В РОБОТІ" / "IN PROGRESS" (`CardStampImg`) |

## Skin `freedom`

Mockup window: freedom -- «ВОЛЯ.narod» (the home-made 2000s site).

| key | Ukrainian | English | where it is used |
|---|---|---|---|
| `STR_OZL_SKIN_FREEDOM_DEV` | `ВОЛЯ.narod — найкраще в 800x600` | `FREEDOM.narod — best viewed in 800x600` | `DevName`: italic line in the banner (mockup `SKINS.freedom.dev`); the multiplication sign of the mockup is the letter x here |
| `STR_OZL_SKIN_FREEDOM_WORDART` | `~ Дерево досліджень ~` | `~ Research tree ~` | the rainbow banner title; the skin shows WORDART_IMG, this key is the text twin |
| `STR_OZL_SKIN_FREEDOM_WORDART_IMG` | `set:ozl_freedom image:wordart_ua` | `set:ozl_freedom image:wordart_en` | sprite reference: the rainbow WordArt title |
| `STR_OZL_SKIN_FREEDOM_MARQUEE` | `+++ Ласкаво просимо, брате! +++ Свобода — це коли досліджуєш що хочеш +++ Мир, дружба, жуйка +++ Нові досліди щотижня!!! +++ Не забудь залишити запис у гостьовій книзі +++` | `+++ Welcome, brother! +++ Freedom is when you research whatever you want +++ Peace, friendship, chewing gum +++ New experiments every week!!! +++ Don't forget to sign the guestbook +++` | `Marquee`: the running line, shifted in `OnUpdate`. The mockup has a peace sign on both sides of "Мир, дружба, жуйка"; dropped |
| `STR_OZL_SKIN_FREEDOM_MENU_BAR` | `:: МЕНЮ ::` | `:: MENU ::` | title bar over the branch list (`.fbar`) |
| `STR_OZL_SKIN_FREEDOM_POOL_BAR` | `:: БАЛИ ::` | `:: POINTS ::` | title bar over the pool (`.fbar`) |
| `STR_OZL_SKIN_FREEDOM_BRANCH_MARK` | `»` | `»` | prefix of every branch link in the menu (CSS `.branch .bn::before` is `» `) |
| `STR_OZL_SKIN_FREEDOM_BRANCH_HERE` | `ти тут` | `you are here` | suffix of the selected branch link (CSS `.branch.on .bn::after`); the mockup has an arrow before it, dropped (a sprite, if wanted) |
| `STR_OZL_SKIN_FREEDOM_UNDER_CONSTRUCTION` | `Сторінка в розробці!` | `Page under construction!` | the black-and-yellow sign at the bottom of the menu box (`.uc`) |
| `STR_OZL_SKIN_FREEDOM_INFO_TITLE` | `info.exe` | `info.exe` | title of the card window (`.ftitle`); its three buttons are sprites |
| `STR_OZL_SKIN_FREEDOM_COUNTER_LABEL` | `Ти відвідувач №` | `You are visitor No.` | footer: label before the visit counter (`.ffoot`) |
| `STR_OZL_SKIN_FREEDOM_COUNTER_VALUE` | `000420` | `000420` | footer: the counter value, a constant of the mockup (red seven-segment digits) |
| `STR_OZL_SKIN_FREEDOM_FOOT_NEW` | `NEW` | `NEW` | footer: the blinking word between two stars in the mockup (`★ NEW ★`); the stars are dropped |
| `STR_OZL_SKIN_FREEDOM_FOOT_GUESTBOOK` | `Гостьова книга` | `Guestbook` | footer link (underlined) |
| `STR_OZL_SKIN_FREEDOM_FOOT_LINKS` | `Лінки` | `Links` | footer link (underlined) |
| `STR_OZL_SKIN_FREEDOM_FOOT_COPY` | `© Воля · зліплено на коліні · копіюй на здоров'я` | `© Freedom · cobbled together in a hurry · copy it, enjoy` | footer: the copyright line; a peace sign ends it in the mockup, dropped |
| `STR_OZL_SKIN_FREEDOM_HELP_NEXT` | `Ага` | `Yep` | helper: button "next tip" (`HelperNext`) |
| `STR_OZL_SKIN_FREEDOM_HELP_HIDE` | `Відчепись` | `Go away` | helper: button "hide for 10 s" (`HelperHide`) |
| `STR_OZL_SKIN_FREEDOM_HELP_NONE_TITLE` | `Привіт! Я Листик.` | `Hi! I'm Leafy.` | helper, nothing selected (`HelperTitle`) |
| `STR_OZL_SKIN_FREEDOM_HELP_NONE_TEXT` | `Обери вузол — і я підкажу, що робити.` | `Pick a node and I'll tell you what to do.` | helper, nothing selected (`HelperText`) |
| `STR_OZL_SKIN_FREEDOM_HELP_AVAILABLE_TITLE` | `Схоже, ти хочеш щось дослідити!` | `Looks like you want to research something!` | helper, node available and the player may spend |
| `STR_OZL_SKIN_FREEDOM_HELP_AVAILABLE_TEXT` | `Тисни «Дослідити» — і вперед. Я вірю в тебе.` | `Press 'Research' and off you go. I believe in you.` | helper, node available and the player may spend; a peace sign follows in the mockup (dropped) |
| `STR_OZL_SKIN_FREEDOM_HELP_NOLEADER_TITLE` | `Хм, кнопка сіра...` | `Hm, the button is grey...` | helper, node available but the player may not spend; the mockup ends with an ellipsis sign, three dots here |
| `STR_OZL_SKIN_FREEDOM_HELP_NOLEADER_TEXT` | `Тиснути може тільки лідер. Поклич його, брате!` | `Only the leader can press it. Go and fetch them, brother!` | helper, node available but the player may not spend |
| `STR_OZL_SKIN_FREEDOM_HELP_SHORT_TITLE` | `Ой, балів замало.` | `Oops, not enough points.` | helper, status short |
| `STR_OZL_SKIN_FREEDOM_HELP_SHORT_TEXT` | `Збери ще трохи — і приходь, я почекаю.` | `Collect a bit more and come back, I'll wait.` | helper, status short |
| `STR_OZL_SKIN_FREEDOM_HELP_LOCKED_TITLE` | `Не поспішай, друже!` | `Don't rush, friend!` | helper, status locked |
| `STR_OZL_SKIN_FREEDOM_HELP_LOCKED_TEXT` | `Спершу відкрий попередні вузли.` | `Open the previous nodes first.` | helper, status locked |
| `STR_OZL_SKIN_FREEDOM_HELP_RESEARCHING_TITLE` | `Досліджуємо...` | `Researching...` | helper, status researching; the mockup ends with an ellipsis sign, three dots here |
| `STR_OZL_SKIN_FREEDOM_HELP_RESEARCHING_TEXT` | `Поки чекаєш — можна заварити чаю.` | `While you wait, you could brew some tea.` | helper, status researching; a cup of tea follows in the mockup (dropped) |
| `STR_OZL_SKIN_FREEDOM_HELP_DONE_TITLE` | `Це вже наше!` | `That one's ours already!` | helper, status completed |
| `STR_OZL_SKIN_FREEDOM_HELP_DONE_TEXT` | `Досліджено. Ти молодець, тримай п'ять.` | `Researched. Well done, high five.` | helper, status completed; a victory hand follows in the mockup (dropped) |
| `STR_OZL_SKIN_FREEDOM_HELP_GENERAL1_TITLE` | `До речі!` | `By the way!` | helper, general tip 1 (the general tips follow the node's own tip, round and round) |
| `STR_OZL_SKIN_FREEDOM_HELP_GENERAL1_TEXT` | `Вузол із ромбиком «АБО» відкривається після будь-якого з попередніх.` | `A node with an 'OR' diamond opens after any of the previous ones.` | helper, general tip 1 |
| `STR_OZL_SKIN_FREEDOM_HELP_GENERAL2_TITLE` | `Порада дня` | `Tip of the day` | helper, general tip 2 |
| `STR_OZL_SKIN_FREEDOM_HELP_GENERAL2_TEXT` | `Дерево росте знизу вгору. Тягни мишкою, щоб подивитися, що вище.` | `The tree grows from the bottom up. Drag with the mouse to see what is higher.` | helper, general tip 2 |
| `STR_OZL_SKIN_FREEDOM_HELP_GENERAL3_TITLE` | `А ти знав?` | `Did you know?` | helper, general tip 3 |
| `STR_OZL_SKIN_FREEDOM_HELP_GENERAL3_TEXT` | `Що вище — то в тумані. Досліди сусідній вузол, і туман відступить.` | `The higher, the foggier. Research a neighbouring node and the fog will clear.` | helper, general tip 3 |
| `STR_OZL_SKIN_FREEDOM_HELP_GENERAL4_TITLE` | `Порада дня` | `Tip of the day` | helper, general tip 4 |
| `STR_OZL_SKIN_FREEDOM_HELP_GENERAL4_TEXT` | `Бали — зліва під меню. Сірий нуль — балів цього виду ще немає.` | `Points are on the left under the menu. A grey zero means none of that kind yet.` | helper, general tip 4 |
| `STR_OZL_SKIN_FREEDOM_HELP_GENERAL5_TITLE` | `Привіт ще раз!` | `Hi again!` | helper, general tip 5 |
| `STR_OZL_SKIN_FREEDOM_HELP_GENERAL5_TEXT` | `Я Листик. Можу підказувати весь день.` | `I'm Leafy. I can give tips all day long.` | helper, general tip 5; a peace sign follows in the mockup (dropped) |

## Skin `sop`

Mockup window: sop -- «Тактичний планшет» (the tube-monitor tablet).

| key | Ukrainian | English | where it is used |
|---|---|---|---|
| `STR_OZL_SKIN_SOP_DEV` | `Тактичний планшет` | `Tactical tablet` | `DevName`: the callsign line of the HUD (mockup `SKINS.sop.dev`) |
| `STR_OZL_SKIN_SOP_TARGET` | `ЦIЛЬ` | `TARGET` | first line of the target frame (CSS `.c-head::before`); already capitals, the diamond sign before it is dropped |

## Skin `bandit`

Mockup window: bandit -- «Записи братви» (the crumpled notebook).

| key | Ukrainian | English | where it is used |
|---|---|---|---|
| `STR_OZL_SKIN_BANDIT_DEV` | `Записи братви` | `The crew's notes` | `DevName`: the handwritten line at the right of the title (mockup `SKINS.bandit.dev`) |
| `STR_OZL_SKIN_BANDIT_TITLE_PRE` | `Дерево` | `Tree of` | title, part 1: `Дерево <s>знань</s> досліджень` |
| `STR_OZL_SKIN_BANDIT_TITLE_STRUCK` | `знань` | `knowledge` | title, part 2: the struck-out word (drawn with a line over it) |
| `STR_OZL_SKIN_BANDIT_TITLE_POST` | `досліджень` | `research` | title, part 3 |
| `STR_OZL_SKIN_BANDIT_TITLE_IMG` | `set:ozl_bandit image:title_ua` | `set:ozl_bandit image:title_en` | sprite reference: the whole handwritten title with the struck word |
| `STR_OZL_SKIN_BANDIT_POOL` | `Общак` | `The pot` | heading over the pool (`.h`, handwritten, underlined with a wave); the skin shows POOL_IMG, this key is the text twin |
| `STR_OZL_SKIN_BANDIT_POOL_IMG` | `set:ozl_bandit image:pool_ua` | `set:ozl_bandit image:pool_en` | sprite reference: the handwritten pool heading |
| `STR_OZL_SKIN_BANDIT_SEC_MARK` | `:` | `:` | suffix of every card section head (CSS `.sec::after`) |

## Skin `neutral`

Mockup window: neutral -- «Записник сталкера» (the clean notebook; the mockup's `loner` skin).

| key | Ukrainian | English | where it is used |
|---|---|---|---|
| `STR_OZL_SKIN_NEUTRAL_DEV` | `Записник сталкера` | `Stalker's notebook` | `DevName`: the handwritten line at the right of the title (mockup `SKINS.loner.dev`) |
| `STR_OZL_SKIN_NEUTRAL_TITLE` | `Дерево досліджень` | `Research tree` | page title (`.title`), drawn as live text in the mod's Caveat face (`ozl_hand72`) |
| `STR_OZL_SKIN_NEUTRAL_TITLE_IMG` | `set:ozl_neutral image:title_ua` | `set:ozl_neutral image:title_en` | sprite reference: the handwritten page title. Not used: neutral draws the title as live text, and `ozl_neutral` has no `title_ua`/`title_en` sprite |
| `STR_OZL_SKIN_NEUTRAL_POOL` | `Бали` | `Points` | heading over the pool (`.h`), live text in `ozl_hand72` with an underline sized to the word |
| `STR_OZL_SKIN_NEUTRAL_POOL_IMG` | `set:ozl_neutral image:pool_ua` | `set:ozl_neutral image:pool_en` | sprite reference: the handwritten pool heading. Not used: neutral draws the heading as live text, and `ozl_neutral` has no `pool_ua`/`pool_en` sprite |
| `STR_OZL_SKIN_NEUTRAL_SEC_MARK` | `:` | `:` | suffix of every card section head (CSS `.sec::after`) |

## Dropped glyphs

Signs of the mockup that the vanilla fonts lack. The keys carry no trace of them; a skin that
wants the look draws the sign as a sprite of its own imageset. Position is where the sign stood
in the mockup text.

| glyph | where the mockup has it | what the key holds instead |
|---|---|---|
| ☮ peace sign | freedom: twice in the marquee around "Мир, дружба, жуйка"; after the helper texts "Я вірю в тебе" and "Можу підказувати весь день"; after the copyright line | nothing; the two helper texts end with a full stop where the sign stood |
| ★ star | freedom footer `★ NEW ★` | `FREEDOM_FOOT_NEW` = `NEW`, no stars |
| 🍵 cup of tea | freedom helper, researching: "можна заварити чаю 🍵" | text ends with a full stop |
| ✌ victory hand | freedom helper, completed: "тримай п'ять ✌" | text ends with a full stop |
| 🔒 ⏳ ✓ ✔ ● | the node marks of every skin (lock, hourglass, check, heavy check, dot) | not keys at all: sprites of the skin's imageset. Only the WORDS "в ділі" and "NEW!" are keys (`TREE_MARK_WORK`, `TREE_MARK_NEW`); the paper skins' `?` mark is plain punctuation and needs no key |
| ◇ diamond | sop card head `◇ ЦІЛЬ` | `SOP_TARGET` = `ЦIЛЬ` |
| ▸ pointer | sop: prefix of every card section head (CSS `.sec::before`) | no key; a sprite before the head |
| ◆ lozenge | ecolog: prefix of every card section head (CSS `.sec::before`) | no key; a sprite before the head |
| ← arrow | freedom: `← ти тут` after the selected branch link (CSS `.branch.on .bn::after`) | `FREEDOM_BRANCH_HERE` = `ти тут` |
| × multiplication sign | freedom `dev`: "800×600" | the letter x: `800x600` (as home-made sites wrote it) |
| _ □ × | freedom: the three buttons of the `info.exe` title bar | sprites, no keys |
| … ellipsis sign | freedom helper titles "Хм, кнопка сіра…", "Досліджуємо…" | three ASCII dots, as the rest of the file writes them |

Kept: `«` `»` `—` `·` `№` `©` and the apostrophe `'` (as in "п'ять", "здоров'я"). All of them,
and the Latin `I` that stands for the Cyrillic capital, were drawn by a live client in
`sdf_MetronBook24` on 2026-10-31 (a probe layout with 20 of these keys, Ukrainian and English).

## Texts that are not keys

- Roman numerals of the tiers (`I` ... `VII`) and the `m:ss` clock: drawn by the script.
- Names that come from data: faction names (the core), node names and descriptions (the tree
  file), point names (the point types file), item names (the game's config).
- The `?` mark of the paper skins, the `!!!` doodle and the other drawings on the bandit page,
  the title-bar buttons of `info.exe`: pictures, baked by the skin's manifest.
- Mockup-only controls: the tabs of the factions, "я — лідер", "туман", "усі гілки разом", "↺ демо",
  the branch "Усі гілки (демо прокрутки)".
