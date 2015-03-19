SELECT 
	B.coverfile, -- 0 Файл обложки
    B.uid, -- 1 PRIMARY KEY
	MIN(B.title), -- 2 Название
	array_agg(A.lastname), array_agg(A.firstname), array_agg(A.middlename), array_agg(A.nickname), -- 3 4 5 6 Авторы 
	MIN(G.name), -- 7 Жанры
	MIN(S.name), MIN(BS.volume), -- 8 9 Серии
	MIN(P.name), -- 10 Издатель
	MIN(PS.name), MIN(BPS.volume), -- 11 12 Издательские серии
    B.zipfile, -- 13 Файл архива книги
    B.annotation, -- 14 Описание книги
    B.fb2id -- 15 FB2 идентификатор книги

FROM 
    	book B
    LEFT JOIN 
    	bookauthor BA
        ON B.uid = BA.bookid
    LEFT JOIN 
    	bookgenre BG
        ON B.uid = BG.bookid
    LEFT JOIN 
    	booksequence BS
        ON B.uid = BS.bookid
    LEFT JOIN 
    	bookpubsequence BPS
        ON B.uid = BPS.bookid
    LEFT JOIN 
    	author A
        ON BA.authorid = A.uid
    LEFT JOIN 
    	genre G
        ON BG.genreid = G.uid
    LEFT JOIN 
    	sequence S
        ON BS.sequenceid = S.uid
    LEFT JOIN 
    	pubsequence PS
        ON BPS.sequenceid = PS.uid
    LEFT JOIN 
    	publisher P
    	ON B.publisherid = P.uid

WHERESTRING

GROUP BY
	B.uid

ORDERBYSTRING

;