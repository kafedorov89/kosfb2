SELECT 
	B.coverfile, -- Файл обложки
    B.uid, -- PRIMARY KEY
	MIN(B.title), -- Название
	array_agg(A.lastname), array_agg(A.firstname), array_agg(A.middlename), array_agg(A.nickname), -- Авторы 
	array_agg(G.name), -- Жанры
	array_agg(PS.name), array_agg(PS.volume), -- Серии
	MIN(P.name), -- Издатель
	array_agg(PS.name), array_agg(PS.name), -- Издательские серии
    B.zipfile, -- Файл архива книги
    B.annotation, -- Описание книги
    B.fb2id -- FB2 идентификатор книги

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
        ON BA.author = A.uid
    LEFT JOIN 
    	genre G
        ON BG.genreid = G.uid
    LEFT JOIN 
    	sequence S
        ON BS.sequenceid = S.uid
    LEFT JOIN 
    	pubsequence PS
        ON BPS.pubsequenceid = PS.uid
    LEFT JOIN 
    	publisher P
    	ON B.publisherid = P.uid

WHERESTRING

GROUP BY
	B.uid

ORDERBYSTRING

;