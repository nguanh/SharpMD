CREATE TABLE IF NOT EXISTS analysis.references (
	ID int NOT NULL AUTO_INCREMENT,
    source_paper int,
	ref_paper int,
    primary key(ID),
    index( source_paper),
    index(ref_paper)
);
#: \\Users\\anhtu\\PycharmProjects\\SharpMD\\scripts\\test.csv
LOAD DATA CONCURRENT LOCAL INFILE '/home/nguyen/raw_file/PaperReferences.txt' INTO TABLE analysis.references
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\r\n'
(@hexvar, @hexvar2) 
set 
source_paper = CONV( @hexvar, 16, 10), 
ref_paper    = CONV( @hexvar2, 16, 10); 