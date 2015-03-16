SELECT 
	B.uid, 
	MIN(B.title), -- Название
	array_agg(A.lastname), array_agg(A.firstname), array_agg(A.middlename), array_agg(A.nickname), -- Авторы 
	array_agg(G.name), -- Жанры
	array_agg(PS.name), -- Серии
	MIN(P.name), -- Издатель
	array_agg(PS.name) -- Издательские серии

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
    	ON PS.publisherid = P.uid

WHERE 
	-- Название
	B.title like keyword

	-- Автор
	A.firstname like keyword 
	OR A.lastname like keyword
	OR A.middlename like keyword
	OR A.nickname like keyword

	-- Жанр
	G.name like keyword

	-- Серия
	S.name like keyword

	-- Издательская серия
	PS.name like keyword

GROUP BY
	B.uid

ORDER BY
	-- по Жанру
	G.name
	-- по Серии
	S.name
	-- по Издательской серии
	PS.name
	-- по Автору
	A.lastname
;

