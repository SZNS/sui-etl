select if(
(
  SELECT (MAX(sequence_number) - MIN(sequence_number)) as highest_checkpoint,  FROM `{{params.target_project_id}}.{{params.target_dataset_name}}.CHECKPOINT` where epoch = {{ti.xcom_pull(key="epoch", task_ids="prepare")}}

) + 1 =
(
SELECT count(*) FROM `{{params.target_project_id}}.{{params.target_dataset_name}}.CHECKPOINT` where epoch = {{ti.xcom_pull(key="epoch", task_ids="prepare")}}
), 1, 0)