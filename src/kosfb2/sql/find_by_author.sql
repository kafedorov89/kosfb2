SELECT 
	MIN(B.uid), -- 1 PRIMARY KEY
	MIN(B.coverfile), -- 0 Файл обложки
	MIN(B.title), -- 2 Название
	array_agg(A.lastname), array_agg(A.firstname), array_agg(A.middlename), array_agg(A.nickname) -- 3 4 5 6 Авторы
	array_agg(G.name), -- 7 Жанры 
FROM 
	book B
    LEFT JOIN 
    	bookauthor BA
        ON B.uid = BA.bookid
    INNER JOIN 
    	author A
        ON BA.authorid = A.uid
    LEFT JOIN 
    	bookgenre BG
        ON B.uid = BG.bookid

WHERE B.title like '%%'

-- ORDER BY MIN(A.lastname
GROUP BY B.uid

;