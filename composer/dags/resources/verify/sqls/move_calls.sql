select if(
(
  SELECT SUM(move_calls)  FROM `{{params.project_id}}.{{params.dataset_name}}.TRANSACTION` where epoch = {{ti.xcom_pull(key="epoch", task_ids="current_epoch")}}

) =
(
SELECT COUNT(*) FROM `{{params.project_id}}.{{params.dataset_name}}.MOVE_CALL` where epoch = {{ti.xcom_pull(key="epoch", task_ids="current_epoch")}}
), 1, 0)