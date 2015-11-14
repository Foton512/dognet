# -*- coding: utf-8 -*-

walkTimeout = 10  # In seconds
pointsDistanceThreshold = 2  # In meters
closeDogsDistanceThreshold = 10 # In meters
homeDistanceThreshold = 500  # In meters
closeDogEventsToStore = 500

breeds = [
    u"Австралийская борзая (кенгуровая собака)",
    u"Австралийская овчарка (Аусси)",
    u"Австралийская пастушья собака",
    u"Австралийская короткохвостая пастушья собака",
    u"Австралийский бандог",
    u"Австралийский бульдог",
    u"Австралийский динго",
    u"Австралийский келпи",
    u"Австралийский шелковистый терьер (силки терьер)",
    u"Австрийская гончая (брандл бракк)",
    u"Австрийский  пинчер (Австрийский короткошерстный пинчер)",
    u"Азавак (Африканская борзая)",
    u"Айну (хоккайдская собака)",
    u"Акбаш",
    u"Акита-ину",
    u"Алано (Испанский алано)",
    u"Алапахский бульдог",
    u"Алопекис",
    u"Альпийская овчарка",
    u"Альпийский таксообразный бракк",
    u"Аляскинский Кли Кэй",
    u"Аляскинский маламут",
    u"Американская акита",
    u"Американская белая овчарка",
    u"Американская тундровая овчарка (Американская тундровая собака)",
    u"Американский бандог",
    u"Американский бульдог",
    u"Американский кокер-спаниель",
    u"Американский питбультерьер",
    u"Американский стаффордшир-терьер",
    u"Американский той-фокстерьер",
    u"Американская эскимосская собака",
    u"Английская овчарка",
    u"Английский бульдог",
    u"Английский кокер-спаниель",
    u"Английский мастиф",
    u"Английский сеттер",
    u"Английский той-терьер",
    u"Аппенцеллер Зенненхунд",
    u"Аргентинский дог",
    u"Арубская деревенская собака",
    u"Атласская овчарка (Аиди)",
    u"Афганская борзая",
    u"Аффенпинчер",
    u"Басенджи",
    u"Бассет бретонский",
    u"Бассет-хаунд",
    u"Бедлингтон терьер",
    u"Белая швейцарская овчарка",
    u"Бельгийская овчарка",
    u"Бернский зенненхунд",
    u"Бигль",
    u"Бишон фризе",
    u"Бладхаунд",
    u"Бобтейл",
    u"Боксер",
    u"Болгарская овчарка",
    u"Болоньез",
    u"Большой швейцарский зенненхунд",
    u"Бордер колли",
    u"Бордоский дог (Французский мастиф)",
    u"Бостон терьер",
    u"Бразильский терьер",
    u"Бриар",
    u"Бульмастиф",
    u"Бультерьер",
    u"Бультерьер миниатюрный",
    u"Бурбуль",
    u"Веймаранер",
    u"Вельш корги",
    u"Вельштерьер",
    u"Венгерская короткошерстная легавая",
    u"Вест терьер",
    u"Волкодав ирландский",
    u"Восточноевропейская овчарка",
    u"Гампр",
    u"Голая мексиканская собака",
    u"Голландская овчарка (Хердер)",
    u"Гончая греческая (Греческая заячья гончая)",
    u"Гончая малая (англо-французская)",
    u"Гончая плотта",
    u"Гончая Стефена",
    u"Гончая тирольская",
    u"Гончая Шиллера",
    u"Грейхаунд",
    u"Греческая овчарка",
    u"Гренландская собака",
    u"Гриффон",
    u"Грюнендаль",
    u"Далматин",
    u"Денди динмонд",
    u"Джек Рассел терьер",
    u"Дизайнерские собаки",
    u"Доберман-пинчер",
    u"Дрентская куропаточная собака",
    u"Золотистый ретривер",
    u"Ирландский сеттер",
    u"Ирландский глен-оф-имаал-терьер",
    u"Йоркширский терьер",
    u"Ка-де-бо",
    u"Кавалер кинг чарльз спаниель",
    u"Кавказская овчарка",
    u"Канадская эскимосская собака",
    u"Канарский дог",
    u"Кане корсо",
    u"Карабаш анатолийский",
    u"Карабаш кангальский",
    u"Карельская медвежья собака",
    u"Карликовый пинчер (цвергпинчер)",
    u"Карская собака",
    u"Кеесхонд",
    u"Керн терьер",
    u"Керри-блю-терьер",
    u"Китайская хохлатая собачка",
    u"Кламбер-спаниель",
    u"Колли",
    u"Крашская овчарка",
    u"Комондор",
    u"Кpапчато-голубой кунхаунд (енотовая гончая)",
    u"Ксолоитцкуинтли (мексиканская голая собака)",
    u"Кувас",
    u"Курцхаар",
    u"Курчавошерстный ретривер",
    u"Кыргызская борзая",
    u"Лабрадор-ретривер",
    u"Лайка западно-сибирская",
    u"Лайка камчатская ездовая",
    u"Лайка ненецкая оленегонная",
    u"Лайка самоедская",
    u"Лайка финская оленегонная",
    u"Лайка чукотская ездовая",
    u"Лайка эскимосская",
    u"Лайка якутская",
    u"Лакенуа",
    u"Ландсир",
    u"Лапландская пастушья собака",
    u"Левретка",
    u"Леонбергер",
    u"Литовская гончая (латвийская гончая)",
    u"Лопарская оленегонная собака",
    u"Лукас терьер",
    u"Лхасский апсо",
    u"Люцернская гончая",
    u"Малая греческая домашняя собака",
    u"Малинуа",
    u"Мальтезе (Мальтийская болонка)",
    u"Мареммано-абруццкая овчарка (мареммано абруццеле)",
    u"Мастино наполетано (Неаполетанский мастиф)",
    u"Миттельшнауцер",
    u"Монгольская овчарка (банхар)",
    u"Мопс",
    u"Московская сторожевая",
    u"Московский дракон",
    u"Немецкий дог (Датский дог)",
    u"Немецкая овчарка",
    u"Немецкий дратхаар (жесткошерстная легавая)",
    u"Пинчер немецкий",
    u"Новогвинейская поющая собака",
    u"Норботтен-шпиц (Скандинавская лайка)",
    u"Норвежский эльгхунд серый",
    u"Норвежский эльгхунд чёрный",
    u"Норвич терьер",
    u"Норфолк терьер",
    u"Ньюфаундленд",
    u"Орхидея петербургская",
    u"Папильон",
    u"Парсон рассел терьер",
    u"Пекинес",
    u"Перуанская голая собака",
    u"Пинчеры",
    u"Пиренейская горная собака",
    u"Пиренейский мастиф",
    u"Поденгу португезе",
    u"Подгалянская овчарка",
    u"Пойнтер английский",
    u"Пойнтер Герта",
    u"Пойнтер немецкий",
    u"Пойнтер пудель (Пудель-пойнтер)",
    u"Пойнтер старо-датский (старо-датская легавая)",
    u"Польская гончая",
    u"Польская низинная овчарка",
    u"Португальская водяная собака",
    u"Португальская овчарка",
    u"Португальский рафейру",
    u"Пражский крысарик",
    u"Пти-брабансон",
    u"Пудель",
    u"Пули",
    u"Перро де преса канарио (Канарская собака)",
    u"Риджбек родезийский",
    u"Риджбек тайский",
    u"Ризеншнауцер",
    u"Ротвейлер",
    u"Русская гончая",
    u"Русская псовая борзая",
    u"Русская салонная собака",
    u"Русский спаниель",
    u"Русская цветная болонка",
    u"Русский длинношерстный той терьер",
    u"Русский той терьер",
    u"Русский черный терьер",
    u"Салюки",
    u"Сарлосская волчья собака",
    u"Сенбернар",
    u"Силихем-терьер",
    u"Сицилийская борзая (Чирнеко дель этна)",
    u"Сиба Ину",
    u"Скай-терьер",
    u"Скотч-терьер",
    u"Словацкий чувач",
    u"Слюги",
    u"Среднеазиатская овчарка",
    u"Стаффордширский бультерьер",
    u"Суссекс-спаниель",
    u"Тазы (Среднеазиатская борзая)",
    u"Тайский риджбек",
    u"Такса",
    u"Тамасканская собака",
    u"Тервюрен",
    u"Терьер пшеничный",
    u"Тибетский терьер",
    u"Тоса-ину",
    u"Уиппет",
    u"Утонаган",
    u"Фараонова собка",
    u"Фила бразилейро",
    u"Финская оленегонная лайка",
    u"Финско-шведская оленегонная собака",
    u"Фландрский бувье",
    u"Фокстерьер",
    u"Фоксхаунд английский",
    u"Французская овчарка",
    u"Французский бульдог",
    u"Ханаанская собака",
    u"Хаски аляскинский",
    u"Хаски лабрадорский",
    u"Хаски сахалинский",
    u"Хаски сибирский",
    u"Ховаварт",
    u"Хорватская планинская собака",
    u"Хортая борзая",
    u"Цвергшнауцер",
    u"Цвергпинчер",
    u"Чау-чау",
    u"Чесапик бей ретривер",
    u"Чехословацкая волчья собака",
    u"Чинук",
    u"Чихуахуа",
    u"Шар-пей",
    u"Шарпланинац",
    u"Шведский вальхунд",
    u"Шведский лапхунд",
    u"Шведский элькхунд",
    u"Швейцарская юрская гончая",
    u"Шелти",
    u"Ши-тцу",
    u"Шиба-Ину",
    u"Шилонская овчарка",
    u"Шипперке",
    u"Шотландский сеттер",
    u"Шпиц карликовый (померанский)",
    u"Шпиц малый (немецкий)",
    u"Шпиц финский",
    u"Шпиц шведский (лапхунд) – Лапдандские собаки",
    u"Шпиц японский",
    u"Энтлебухер зенненхунд",
    u"Эрдельтерьер",
    u"Эстонская гончая",
    u"Эштрельская гладкошерстная овчарка",
    u"Эштрельская длинношерстная овчарка",
    u"Югославская горная гончая (Планинская гончая)",
    u"Югославская трехцветная гончая",
    u"Южнорусская овчарка",
    u"Южнорусская степная борзая",
    u"Ягдтерьер",
    u"Японский хин",
]
