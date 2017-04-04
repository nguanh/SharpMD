# ===========================================URL========================================================================
GLOBAL_URL = (
    "CREATE TABLE `global_url` ("
    "  `id` INT NOT NULL AUTO_INCREMENT,"
    "  `domain` TEXT NOT NULL ,"
    "  `url` TEXT NOT NULL ,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE={} CHARSET=utf8mb4")

LOCAL_URL = (
    "CREATE TABLE `local_url` ("
    "  `id` INT NOT NULL AUTO_INCREMENT,"
    "  `global_url_id` INT NOT NULL ,"
    "  `type_id` INT ,"
    "  `study_field_id` INT,"
    "  `pub_source_id` INT,"
    "  `url` TEXT NOT NULL ,"
    "  `last_updated` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE={} CHARSET=utf8mb4")

# ===========================================KEYWORDS===================================================================

# stores, which keyword belongs to which publication url
PUBLICATION_KEYWORDS = (
    "CREATE TABLE `keywords` ("
    "  `id` INT NOT NULL AUTO_INCREMENT,"
    "  `url_id` INT NOT NULL,"
    "  `keyword_id` INT NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE={} CHARSET=utf8mb4")

# stores keywords and description
KEYWORDS = (
    "CREATE TABLE `keywords` ("
    "  `id` INT NOT NULL AUTO_INCREMENT,"
    "  `main_name` VARCHAR(150) NOT NULL ,"
    "  `block_name`VARCHAR(150) NOT NULL ,"
    "  `description` TEXT,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE={} CHARSET=utf8mb4")

KEYALIAS = (
    "CREATE TABLE `keyword_alias` ("
    "  `id` INT NOT NULL AUTO_INCREMENT,"
    "  `keyword_id` INT NOT NULL,"
    "  `alias` VARCHAR(150) NOT NULL ,"
    "  PRIMARY KEY (`id`),"
    "  UNIQUE KEY (`keyword_id`,`alias`)"
    ") ENGINE={} CHARSET=utf8mb4")

KEYSOURCE = (
    "CREATE TABLE `key_source` ("
    "  `id` INT NOT NULL AUTO_INCREMENT,"
    "  `url_id` INT NOT NULL,"
    "  `alias_id` INT  NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  UNIQUE KEY (`url_id`,`alias_id`)"
    ") ENGINE={} CHARSET=utf8mb4")


# ===========================================REFERENCE==================================================================

REFERENCE = (
    "CREATE TABLE `reference` ("
    "  `id` INT NOT NULL AUTO_INCREMENT,"
    "  `url_id` INT NOT NULL ,"
    "  `cluster_id` INT NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE={} CHARSET=utf8mb4")
