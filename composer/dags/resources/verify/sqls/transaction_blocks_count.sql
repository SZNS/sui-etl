select if(
(
  SELECT SUM(total_transaction_blocks)  FROM `{{params.project_id}}.{{params.dataset_name}}.CHECKPOINT` where epoch = {{ti.xcom_pull(key="epoch", task_ids="current_epoch")}}

) =
(
SELECT COUNT(*) FROM `{{params.project_id}}.{{params.dataset_name}}.TRANSACTION` where epoch = {{ti.xcom_pull(key="epoch", task_ids="current_epoch")}}
), 1, 0 )