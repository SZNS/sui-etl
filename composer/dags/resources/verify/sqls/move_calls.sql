select if(
(
  SELECT SUM(move_calls)  FROM `{{params.target_project_id}}.{{params.target_dataset_name}}.TRANSACTION` where epoch = {{ti.xcom_pull(key="epoch", task_ids="prepare")}}

) =
(
SELECT COUNT(*) FROM `{{params.target_project_id}}.{{params.target_dataset_name}}.MOVE_CALL` where epoch = {{ti.xcom_pull(key="epoch", task_ids="prepare")}}
), 1, 0)