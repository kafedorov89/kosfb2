SELECT 

MIN(BB.uid) as uid, -- 1 PRIMARY KEY
	MIN(BB.coverfile) as coverfile, -- 0 Файл обложки
	MIN(BB.title) as title, -- 2 Название
	MIN(BB.lastname) as lastname, MIN(BB.firstname) as firstname, MIN(BB.middlename) as middlename, MIN(BB.nickname) as nickname, -- 3 4 5 6 Авторы
	array_agg(G.name)

FROM (SELECT 
	MIN(B.uid) as uid, -- 1 PRIMARY KEY
	MIN(B.coverfile) as coverfile, -- 0 Файл обложки
	MIN(B.title) as title, -- 2 Название
	array_agg(A.lastname) as lastname, array_agg(A.firstname) as firstname, array_agg(A.middlename) as middlename, array_agg(A.nickname)as nickname -- 3 4 5 6 Авторы 
FROM
	book B
    LEFT JOIN 
    	bookauthor BA
        ON B.uid = BA.bookid
    INNER JOIN 
    	author A
        ON BA.authorid = A.uid

WHERE B.title like '%%'

GROUP BY B.uid
ORDER BY B.uid) as BB

LEFT JOIN 
    	bookgenre BG
        ON BB.uid = BG.bookid
    INNER JOIN 
    	genre G
        ON BG.genreid = G.uid

-- WHERE G.name like '%%'

GROUP BY BB.uid
ORDER BY BB.uid

;