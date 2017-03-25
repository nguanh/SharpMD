
OAI_DATASET = (
    "CREATE TABLE `oaipmh_articles` ("
    "  `identifier` varchar(150) NOT NULL,"
    "  `author` TEXT NOT NULL," #author =creator(s)
    "  `title` TEXT NOT NULL,"
    "  `description` TEXT,"
    "  `contributor` VARCHAR(200),"
    "  `coverage` varchar(200),"
    "  `dates` TEXT NOT NULL ," #array
    "  `formats` varchar(200),"
    "  `languages` varchar(50),"
    "  `publisher` varchar(200),"
    "  `relation` varchar(200),"
    "  `rights` TEXT,"
    "  `sources` varchar(200),"
    "  `subjects` TEXT,"
    "  `type` varchar(200),"
    "  `last_updated` TIMESTAMP,"
    "  `last_harvested` TIMESTAMP,"
    "  PRIMARY KEY (`identifier`)"
    #") ENGINE=TokuDB CHARSET=utf8mb4")
    ") ENGINE=InnoDB CHARSET=utf8mb4")

ADD_OAI_DEFAULT = ("INSERT INTO oaipmh_articles"
                    " (identifier,author, title,description,contributor,coverage,dates,"
                    "formats,languages,publisher,relation,rights,sources,"
                    "subjects,type,last_updated,last_harvested) "
                    "VALUES ( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, CURRENT_TIMESTAMP, 0  )"
                    "ON DUPLICATE KEY UPDATE last_updated= CURRENT_TIMESTAMP,"
                    "author =VALUES(author),"
                    "title =VALUES(title),"
                    "description =VALUES(description),"
                    "contributor =VALUES(contributor),"
                    "coverage =VALUES(coverage),"
                    "dates =VALUES(dates),"
                    "formats =VALUES(formats),"
                    "languages =VALUES(languages),"
                    "publisher =VALUES(publisher),"
                    "relation =VALUES(relation),"
                    "rights =VALUES(rights),"
                    "sources =VALUES(sources)"

                   )




ARXIV_ARTICLE = (
    "CREATE TABLE `arxiv_articles` ("
    "  `identifier` varchar(150) NOT NULL,"
    "  `created` DATE,"
    "  `updated` DATE,"
    "  `author` TEXT NOT NULL,"
    "  `title` TEXT NOT NULL,"
    "  `mscclass` varchar(200),"
    "  `acmclass` varchar(200),"
    "  `reportno` varchar(200),"
    "  `journalref` TEXT,"
    "  `comments` TEXT,"
    "  `description` TEXT,"
    "  `categories` VARCHAR(200),"
    "  `doi` varchar(200),"
    "  `mdate` DATE NOT NULL,"
    "  `last_updated` TIMESTAMP,"
    "  `last_harvested` TIMESTAMP,"
    "  PRIMARY KEY (`identifier`)"
    # ") ENGINE=TokuDB CHARSET=utf8mb4")
    ") ENGINE=InnoDB CHARSET=utf8mb4")


ADD_ARXIV = ("INSERT INTO arxiv_articles"
             "(identifier,created, updated,author,title,mscclass,acmclass,"
             "reportno,journalref,comments,description,categories,doi,mdate,"
             "last_updated, last_harvested) "
             "VALUES ( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, CURRENT_TIMESTAMP, 0)"
             "ON DUPLICATE KEY UPDATE last_updated= CURRENT_TIMESTAMP,"
             "created =VALUES(created),"
             "updated =VALUES(updated),"
             "author =VALUES(author),"
             "title =VALUES(title),"
             "mscclass =VALUES(mscclass),"
             "acmclass =VALUES(acmclass),"
             "reportno =VALUES(reportno),"
             "journalref =VALUES(journalref),"
             "comments =VALUES(comments),"
             "description =VALUES(description),"
             "categories =VALUES(categories),"
             "doi =VALUES(doi),"
             "mdate =VALUES(mdate)"
             )
