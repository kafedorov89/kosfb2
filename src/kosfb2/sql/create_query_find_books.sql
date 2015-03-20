SELECT 
    books.coverfile as coverfile, -- 0 Файл обложки
    books.uid as uid, -- 1 PRIMARY KEY
    books.title as title, -- 2 Название
    -- authors.fullauthorname as fullauthorname, -- 3 4 5 6 Авторы 
    authors.lastname as lastname, authors.firstname as firstname, authors.middlename as middlename, authors.nickname as nickname, -- 3 4 5 6 Авторы 
    genres.gname as genres, -- 7 Жанры
    sequences.sname as sequences, sequences.svolume as svolume, -- 8 9 Серии
    publisher.pname as publisher, -- 10 Издатель
    pubsequences.psname as pubsequences, pubsequences.psvolume as psvolume, -- 11 12 Издательские серии
    books.zipfile as zipfile, -- 13 Файл архива книги
    books.annotation as annotation, -- 14 Описание книги
    books.fb2id as fb2id -- 15 FB2 идентификатор книги

    FROM 
        (SELECT
            B.uid as uid,
            B.coverfile as coverfile, -- 0 Файл обложки
            B.title as title, -- 2 Название
            B.zipfile as zipfile, -- 13 Файл архива книги
            B.annotation as annotation, -- 14 Описание книги
            B.fb2id as fb2id -- 15 FB2 идентификатор книги 
        FROM
            book B

        WHERETITLESTRING
        -- WHERE B.title like '%%'
        GROUP BY B.uid) as books          

        INNER JOIN
            (SELECT 
                MIN(B.uid) as uid, -- 1 PRIMARY KEY
                -- array_agg((A.lastname, A.firstname, A.middlename, A.nickname)::authortype) as fullauthorname
                array_agg(A.lastname) as lastname, array_agg(A.firstname) as firstname, array_agg(A.middlename) as middlename, array_agg(A.nickname)as nickname -- 3 4 5 6 Авторы 
            FROM 
                book B
                LEFT JOIN 
                    bookauthor BA
                    ON B.uid = BA.bookid
                LEFT JOIN 
                    author A
                    ON BA.authorid = A.uid
              
            WHEREAUTHORSTRING
            -- WHERE A.lastname like '%%' OR A.firstname like '%%' OR A.middlename like '%%' OR A.nickname like '%%'

            GROUP BY B.uid) as authors
            ON books.uid = authors.uid

        INNER JOIN     
            (SELECT 
                MIN(B.uid) as uid, -- 1 PRIMARY KEY
                array_agg(G.name) as gname -- 7 Жанры 
            FROM 
                book B
                LEFT JOIN 
                    bookgenre BG
                    ON B.uid = BG.bookid
                LEFT JOIN 
                    genre G
                    ON BG.genreid = G.uid

            WHEREGENRESTRING
            -- WHERE G.name like '%%'

            GROUP BY B.uid) as genres 
            ON books.uid = genres.uid

        INNER JOIN     
            (SELECT 
                MIN(B.uid) as uid, -- 1 PRIMARY KEY
                array_agg(S.name) as sname, array_agg(BS.volume) as svolume -- 8 9 Серии 
            FROM 
                book B
                LEFT JOIN 
                    booksequence BS
                    ON B.uid = BS.bookid
                LEFT JOIN 
                    sequence S
                    ON BS.sequenceid = S.uid

            WHERESEQSTRING
            -- WHERE G.name like '%%'

            GROUP BY B.uid) as sequences 
            ON books.uid = sequences.uid

        INNER JOIN     
            (SELECT 
                MIN(B.uid) as uid, -- 1 PRIMARY KEY
                array_agg(PS.name) as psname, array_agg(BPS.volume) as psvolume -- 11 12 Издательские серии
            FROM 
                book B
                LEFT JOIN 
                    bookpubsequence BPS
                    ON B.uid = BPS.bookid
                LEFT JOIN 
                    pubsequence PS
                    ON BPS.sequenceid = PS.uid

            WHEREPUBSEQSTRING
            -- WHERE PS.name like '%%'

            GROUP BY B.uid) as pubsequences 
            ON books.uid = pubsequences.uid

        INNER JOIN     
            (SELECT 
                MIN(B.uid) as uid, -- 1 PRIMARY KEY
                MIN(P.name) as pname -- 10 Издатель
            FROM 
                book B
                LEFT JOIN 
                    publisher P
                    ON B.publisherid = P.uid

            WHEREPUBSTRING
            -- WHERE P.name like '%%'

            GROUP BY B.uid) as publisher 
            ON books.uid = publisher.uid

ORDERBYSTRING
-- ORDER BY gname
-- ORDER BY sname
-- ORDER BY psname
-- ORDER BY fullauthorname
;
