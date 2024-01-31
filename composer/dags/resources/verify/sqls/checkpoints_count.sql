select if(
(
  SELECT MAX(sequence_number) as highest_checkpoint,  FROM `{{params.project_id}}.{{params.dataset_name}}.CHECKPOINT` LIMIT 1

) + 1 =
(
SELECT row_count FROM `{{params.project_id}}.{{params.dataset_name}}.__TABLES__` where table_id ="CHECKPOINT"
), 1, 0)