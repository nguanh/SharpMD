CREATE FULLTEXT INDEX `cluster_ft_idx`  
ON `storage`.`ingester_cluster` (name);
CREATE FULLTEXT INDEX `authors_model_ft_idx`  
ON `storage`.`ingester_authors_model` (block_name);
