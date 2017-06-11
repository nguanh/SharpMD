SELECT * 
FROM analysis.`references` 
WHERE source_paper in (
						SELECT source_paper FROM (
								SELECT source_paper,count(*) as numb 
                                FROM analysis.`references` 
                                group by source_paper 
                                order by numb desc) as x 
						WHERE x.numb > 10);


