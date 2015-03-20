-- Автор (пополняемый словарь)
DROP TABLE IF EXISTS author CASCADE;
CREATE TABLE author (
    uid SERIAL PRIMARY KEY,
    firstname varchar(40) NOT NULL,
    lastname varchar(40) DEFAULT NULL,
    middlename varchar(40) DEFAULT NULL,
    nickname varchar(40) DEFAULT NULL,
    email varchar(40) DEFAULT NULL
    );

-- Книга (основной объект)
DROP TABLE IF EXISTS book CASCADE;
CREATE TABLE book (
    uid SERIAL PRIMARY KEY,
    iscorrect boolean DEFAULT FALSE,
    title varchar(300) NOT NULL,
    encoding varchar(20) NOT NULL,
    langid integer DEFAULT NULL,
    publisherid integer DEFAULT NULL,
    fb2id varchar(100) CONSTRAINT fb2id_must_be_different UNIQUE NOT NULL, 
    version float NOT NULL,
    annotation text DEFAULT NULL,
    coverfile text NOT NULL,
    coverexist boolean DEFAULT NULL,
    zipfile text NOT NULL
    );

-- Книга(m) - Автор(m)
DROP TABLE IF EXISTS bookauthor CASCADE;
CREATE TABLE bookauthor (
    uid SERIAL PRIMARY KEY,
    bookid integer NOT NULL,
    authorid integer NOT NULL,
    CONSTRAINT check_book FOREIGN KEY (bookid) REFERENCES book (uid) ON DELETE CASCADE,
    CONSTRAINT check_author FOREIGN KEY (authorid) REFERENCES author (uid) ON DELETE CASCADE
    );

-- Книга(m) - Жанр(m)
DROP TABLE IF EXISTS bookgenre CASCADE;
CREATE TABLE bookgenre (
    uid SERIAL PRIMARY KEY,
    bookid integer NOT NULL,
    genreid integer NOT NULL,
    CONSTRAINT check_book FOREIGN KEY (bookid) REFERENCES book (uid) ON DELETE CASCADE,
    CONSTRAINT check_genre FOREIGN KEY (genreid) REFERENCES genre (uid) ON DELETE CASCADE
    );

-- Серия (пополняемый словарь)
DROP TABLE IF EXISTS sequence CASCADE;
CREATE TABLE sequence (
    uid SERIAL PRIMARY KEY,
    name text CONSTRAINT sequence_name_must_be_different UNIQUE NOT NULL
    );

-- Книга(m) - Серия(m)
DROP TABLE IF EXISTS booksequence CASCADE;
CREATE TABLE booksequence (
    uid SERIAL PRIMARY KEY,
    bookid integer NOT NULL,
    sequenceid integer NOT NULL,
    volume integer NOT NULL,
    CONSTRAINT check_book FOREIGN KEY (bookid) REFERENCES book (uid) ON DELETE CASCADE,
    CONSTRAINT check_sequence FOREIGN KEY (sequenceid) REFERENCES sequence (uid) ON DELETE CASCADE 
    );

-- Издательская серия (пополняемый словарь)
DROP TABLE IF EXISTS pubsequence CASCADE;
CREATE TABLE pubsequence (
    uid SERIAL PRIMARY KEY,
    publisherid integer DEFAULT NULL,
    name text CONSTRAINT pubsequence_name_must_be_different UNIQUE NOT NULL
    );

-- Книга(m) - Издательская серия (m)
DROP TABLE IF EXISTS bookpubsequence CASCADE;
CREATE TABLE bookpubsequence (
    uid SERIAL PRIMARY KEY,
    bookid integer NOT NULL,
    sequenceid integer NOT NULL,
    volume integer NOT NULL,
    CONSTRAINT check_book FOREIGN KEY (bookid) REFERENCES book (uid) ON DELETE CASCADE,
    CONSTRAINT check_pubsequence FOREIGN KEY (sequenceid) REFERENCES pubsequence (uid) ON DELETE CASCADE
    );

-- Язык (пополняемый словарь)
DROP TABLE IF EXISTS language CASCADE;
CREATE TABLE language (
    uid SERIAL PRIMARY KEY,
    langcode varchar(40) CONSTRAINT langcode_must_be_different UNIQUE,
    altercode1 varchar(40) CONSTRAINT altercode1_must_be_different UNIQUE,
    altercode2 varchar(40) CONSTRAINT altercode2_must_be_different UNIQUE,
    name varchar(40) CONSTRAINT lang_name_must_be_different UNIQUE NOT NULL
    );

-- Инициализируем таблицу жанров
INSERT INTO language (altercode1, altercode2, langcode, name) VALUES
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
INSERT INTO language (altercode1, name) VALUES
                ('che', 'Чеченский'),
                ('BA', 'Башкирский'),
                ('grc', 'Древнегреческий'),
                ('mul', 'Несколько языков'),
                ('und', 'Неопределенный');
INSERT INTO language (langcode, name) VALUES                
                ('hr', 'Хорватский');
INSERT INTO language (altercode1, langcode, name) VALUES
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
DROP TABLE IF EXISTS publisher CASCADE;
CREATE TABLE publisher (
    uid SERIAL PRIMARY KEY,
    name varchar(200) CONSTRAINT publisher_name_must_be_different UNIQUE NOT NULL
    );

CREATE UNIQUE INDEX bookuid_idx ON book (uid);

CREATE TYPE fullauthorname AS (
  lastname      text
 ,firstname     text
 ,middlename    text
 ,nickname      text
 );

CREATE TYPE fullseqname AS (
  sname      text
 ,svolume    text
 );
