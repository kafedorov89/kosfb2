SELECT 
	MIN(B.uid), -- 1 PRIMARY KEY
	MIN(B.coverfile), -- 0 Файл обложки
	MIN(B.title), -- 2 Название
	array_agg(G.name) -- 7 Жанры 
FROM 
	book B
    LEFT JOIN 
    	bookgenre BG
        ON B.uid = BG.bookid
    INNER JOIN 
    	genre G
        ON BG.genreid = G.uid

WHERE B.title like '%%'

GROUP BY B.uid
ORDER BY B.uid

;