-- Автор (пополняемый словарь)
DROP TABLE IF EXISTS author;
CREATE TABLE author (
    uid SERIAL PRIMARY KEY,
    firstname varchar(40) NOT NULL,
    lastname varchar(40) DEFAULT NULL,
    middlename varchar(40) DEFAULT NULL,
    nickname varchar(40) DEFAULT NULL,
    email varchar(40) DEFAULT NULL
    );

-- Книга (основной объект)
DROP TABLE IF EXISTS book;
CREATE TABLE book (
    uid SERIAL PRIMARY KEY,
    title varchar(300) NOT NULL,
    encoding varchar(20) NOT NULL,
    lang varchar(15) DEFAULT NULL,
    fb2id varchar(100) CONSTRAINT fb2id_must_be_different UNIQUE NOT NULL, 
    version float NOT NULL,
    annotation text DEFAULT NULL,
    coverfile text NOT NULL,
    coverexist boolean DEFAULT NULL,
    zipfile text NOT NULL
    );

-- Жанр (пополняемый словарь)
DROP TABLE IF EXISTS genre;
CREATE TABLE genre (
    uid SERIAL PRIMARY KEY,
    genrename varchar(40)  NOT NULL, 
    genrecode varchar(40)  CONSTRAINT genrecode_must_be_different UNIQUE NOT NULL 
    );
    
-- Инициализируем таблицу жанров
INSERT INTO genre (genrecode, genrename) VALUES 
                ('sf_history', 'Альтернативнаяистория'),
                ('sf_action', 'БоеваяФантастика'),
                ('sf_epic', 'ЭпическаяФантастика'),
                ('sf_heroic', 'Героическаяфантастика'),
                ('sf_detective', 'ДетективнаяФантастика'),
                ('sf_cyberpunk', 'Киберпанк'),
                ('sf_space', 'КосмическаяФантастика'),
                ('sf_social', 'Социальнаяфантастика'),
                ('sf_horror', 'УжасыиМистика'),
                ('sf_humor', 'Юмористическаяфантастика'),
                ('sf_fantasy', 'Фэнтези'),
                ('sf', 'НаучнаяФантастика'),
                ('det_classic', 'КлассическийДетектив'),
                ('det_police', 'ПолицейскийДетектив'),
                ('det_action', 'Боевики'),
                ('det_irony', 'ИроническийДетектив'),
                ('det_history', 'ИсторическийДетектив'),
                ('det_espionage', 'ШпионскийДетектив'),
                ('det_crime', 'КриминальныйДетектив'),
                ('det_political', 'ПолитическийДетектив'),
                ('det_maniac', 'Маньяки'),
                ('det_hard', 'КрутойДетектив'),
                ('thriller', 'Триллеры'),
                ('detective', 'Детектив'),
                ('love_detective', 'ОстросюжетныеЛюбовныеРоманы'),
                ('prose', 'Проза'),
                ('prose_classic', 'КлассическаяПроза'),
                ('prose_history', 'ИсторическаяПроза'),
                ('prose_contemporary', 'СовременнаяПроза'),
                ('prose_counter', 'Контркультура'),
                ('prose_rus_classic', 'РусскаяКлассика'),
                ('prose_su_classics', 'СоветскаяКлассика'),
                ('child_prose', 'ДетскаяПроза'),
                ('love', 'Любовныероманы'),
                ('love_contemporary', 'СовременныеЛюбовныеРоманы'),
                ('love_history', 'ИсторическиеЛюбовныеРоманы'),
                ('love_short', 'КороткиеЛюбовныеРоманы'),
                ('love_erotica', 'Эротика'),
                ('adv_western', 'Вестерны'),
                ('adv_history', 'ИсторическиеПриключения'),
                ('adv_indian', 'Приключения:Индейцы'),
                ('adv_maritime', 'МорскиеПриключения'),
                ('adv_geo', 'ПутешествияиГеография'),
                ('adventure', 'Приключения:Прочее'),
                ('children', 'Детское'),
                ('child_tale', 'Сказки'),
                ('child_verse', 'ДетскиеСтихи'),
                ('child_sf', 'ДетскаяФантастика'),
                ('child_det', 'ДетскиеОстросюжетные'),
                ('child_adv', 'ДетскиеПриключения'),
                ('child_education', 'ДетскаяОбразовательнаялитература'),
                ('poetry', 'Поэзия'),
                ('dramaturgy', 'Драматургия'),
                ('humor_verse', 'ЮмористическиеСтихи'),
                ('antique_ant', 'АнтичнаяЛитература'),
                ('antique_european', 'ЕвропейскаяСтариннаяЛитература'),
                ('antique_russian', 'ДревнерусскаяЛитература'),
                ('antique_east', 'ДревневосточнаяЛитература'),
                ('antique_myths', 'Мифы.Легенды.Эпос'),
                ('antique', 'СтариннаяЛитература:Прочее'),
                ('sci_history', 'История'),
                ('sci_psychology', 'Психология'),
                ('sci_culture', 'Культурология'),
                ('sci_religion', 'Религиоведение'),
                ('sci_philosophy', 'Философия'),
                ('sci_politics', 'Политика'),
                ('sci_business', 'Деловаялитература'),
                ('sci_juris', 'Юриспруденция'),
                ('sci_linguistic', 'Языкознание'),
                ('sci_medicine', 'Медицина'),
                ('sci_phys', 'Физика'),
                ('sci_math', 'Математика'),
                ('sci_chem', 'Химия'),
                ('sci_biology', 'Биология'),
                ('sci_tech', 'Технические'),
                ('science', 'Научно-образовательная:Прочее'),
                ('comp_www', 'Интернет'),
                ('comp_programming', 'Программирование'),
                ('comp_hard', 'КомпьютерноеЖелезо'),
                ('comp_soft', 'Программы'),
                ('comp_db', 'БазыДанных'),
                ('comp_osnet', 'ОСиСети'),
                ('computers', 'Компьютеры:Прочее'),
                ('ref_encyc', 'Энциклопедии'),
                ('ref_dict', 'Словари'),
                ('ref_ref', 'Справочники'),
                ('ref_guide', 'Руководства'),
                ('reference', 'СправочнаяЛитература:Прочее'),
                ('nonf_biography', 'БиографиииМемуары'),
                ('nonf_publicism', 'Публицистика'),
                ('nonf_criticism', 'Критика'),
                ('nonfiction', 'Документальное:Прочее'),
                ('design', 'Искусство,Дизайн'),
                ('adv_animal', 'ПриродаиЖивотные'),
                ('religion', 'Религия'),
                ('religion_rel', 'Религия'),
                ('religion_esoterics', 'Эзотерика'),
                ('religion_self', 'Самосовершенствование'),
                ('humor_anecdote', 'Анекдоты'),
                ('humor_prose', 'ЮмористическаяПроза'),
                ('humor', 'Юмор:Прочее'),
                ('home_cooking', 'Кулинария'),
                ('home_pets', 'ДомашниеЖивотные'),
                ('home_crafts', 'Хобби,Ремесла'),
                ('home_entertain', 'Развлечения'),
                ('home_health', 'Здоровье'),
                ('home_garden', 'СадиОгород'),
                ('home_diy', 'СделайСам'),
                ('home_sport', 'Спорт'),
                ('home_sex', 'Эротика,Секс'),
                ('home', 'ДомиСемья:Прочее');

-- Книга(m) - Автор(m)
DROP TABLE IF EXISTS bookauthor;
CREATE TABLE bookauthor (
    uid SERIAL PRIMARY KEY,
    bookid integer NOT NULL,
    authorid integer NOT NULL,
    CONSTRAINT check_book FOREIGN KEY (bookid) REFERENCES book (uid),
    CONSTRAINT check_author FOREIGN KEY (authorid) REFERENCES author (uid)
    );

-- Книга(m) - Жанр(m)
DROP TABLE IF EXISTS bookgenre;
CREATE TABLE bookgenre (
    uid SERIAL PRIMARY KEY,
    bookid integer NOT NULL,
    genreid integer NOT NULL,
    CONSTRAINT check_book FOREIGN KEY (bookid) REFERENCES book (uid),
    CONSTRAINT check_genre FOREIGN KEY (genreid) REFERENCES genre (uid)
    );

-- Серия (пополняемый словарь)
DROP TABLE IF EXISTS sequence;
CREATE TABLE sequence (
    uid SERIAL PRIMARY KEY,
    name text NOT NULL
    );

-- Книга(m) - Серия(m)
DROP TABLE IF EXISTS booksequence;
CREATE TABLE booksequence (
    uid SERIAL PRIMARY KEY,
    bookid integer NOT NULL,
    sequenceid integer NOT NULL,
    volume integer NOT NULL,
    CONSTRAINT check_book FOREIGN KEY (bookid) REFERENCES book (uid),
    CONSTRAINT check_sequence FOREIGN KEY (sequenceid) REFERENCES sequence (uid)  
    );

-- Издательская серия (пополняемый словарь)
DROP TABLE IF EXISTS pubsequence;
CREATE TABLE pubsequence (
    uid SERIAL PRIMARY KEY,
    name text NOT NULL
    );

-- Книга(m) - Издательская серия (m)
DROP TABLE IF EXISTS bookpubsequence;
CREATE TABLE bookpubsequence (
    uid SERIAL PRIMARY KEY,
    bookid integer NOT NULL,
    pubsequenceid integer NOT NULL,
    volume integer NOT NULL,
    CONSTRAINT check_book FOREIGN KEY (bookid) REFERENCES book (uid),
    CONSTRAINT check_pubsequence FOREIGN KEY (pubsequenceid) REFERENCES pubsequence (uid)
    );

-- Язык (пополняемый словарь)
DROP TABLE IF EXISTS lang;
CREATE TABLE lang (
    uid SERIAL PRIMARY KEY,
    langcode varchar(40) DEFAULT NULL CONSTRAINT langcode_must_be_different UNIQUE,
    altercode1 varchar(40) DEFAULT NULL CONSTRAINT altercode1_must_be_different UNIQUE,
    altercode2 varchar(40) DEFAULT NULL CONSTRAINT altercode2_must_be_different UNIQUE,
    langname varchar(40) NOT NULL CONSTRAINT langname_must_be_different UNIQUE
    );

-- Инициализируем таблицу жанров
INSERT INTO lang (altercode1, altercode2, langcode, langname) VALUES
                ('alb', 'sqi', 'sq', 'Албанский'),
                ('dut', 'nla', 'nl', 'Голландский'),
                ('ell', 'gre', 'el', 'Греческий современный'),
                ('esl', 'spa', 'es', 'Испанский'),
                ('chi', 'zho', 'zh', 'Китайский'),
                ('mac', 'mak', 'mk', 'Македонийский'),
                ('deu', 'ger', 'de', 'Немецкий'),
                ('fas', 'per', 'fa', 'Персидский'),
                ('slk', 'slo', 'sk', 'Словакский'),
                ('cym', 'wel', 'cy', 'Уэльский'),
                ('fra', 'fre', 'fr', 'Французский'),
                ('ces', 'cze', 'cs', 'Чешский'),
                ('sve', 'swe', 'sv', 'Шведский'),
                ('arm', 'hye', 'hy', 'Армянский');
INSERT INTO lang (altercode1, langname) VALUES
                ('che', 'Чеченский'),
                ('BA', 'Башкирский'),
                ('grc', 'Древнегреческий'),
                ('mul', 'Несколько языков'),
                ('und', 'Неопределенный');
INSERT INTO lang (langcode, langname) VALUES                
                ('hr', 'Хорватский');
INSERT INTO lang (altercode1, langcode, langname) VALUES
                ('abk', 'ab', 'Абхазский'),
                ('aze', 'az', 'Азербайджанский'),
                ('eng', 'en', 'Английский'),
                ('bel', 'be', 'Белорусский'),
                ('bul', 'bg', 'Болгарский'),
                ('hun', 'hu', 'Венгерский'),
                ('vie', 'vi', 'Вьетнамский'),
                ('dan', 'da', 'Данийский'),
                ('heb', 'he', 'Иврит'),
                ('ita', 'it', 'Итальянский'),
                ('kaz', 'kk', 'Казахский'),
                ('kir', 'ky', 'Киргизский'),
                ('kor', 'ko', 'Корейский'),
                ('lat', 'la', 'Латинский'),
                ('lav', 'lv', 'Латвийский'),
                ('lit', 'lt', 'Литовский'),
                ('mol', 'mo', 'Молдавский'),
                ('mon', 'mn', 'Монгольский'),
                ('nor', 'no', 'Норвежский'),
                ('pol', 'pl', 'Польский'),
                ('por', 'pt', 'Португальский'),
                ('rus', 'ru', 'Русский'),
                ('san', 'sa', 'Санскрит'),
                ('slv', 'sl', 'Словенский'),
                ('tgk', 'tg', 'Таджикский'),
                ('tat', 'tt', 'Татарский'),
                ('tur', 'tr', 'Турецкий'),
                ('uzb', 'uz', 'Узбекский'),
                ('ukr', 'uk', 'Украинский'),
                ('fin', 'fi', 'Финский'),
                ('epo', 'eo', 'Эсперанто'),
                ('est', 'et', 'Эстонский'),
                ('jpn', 'ja', 'Японский');

-- Издатель (пополняемый словарь)
DROP TABLE IF EXISTS publisher;
CREATE TABLE publisher (
    uid SERIAL PRIMARY KEY,
    publishername varchar(200) NOT NULL
    );