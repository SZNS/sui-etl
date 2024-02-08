select if(
(
  SELECT SUM(total_transaction_blocks)  FROM `{{params.target_project_id}}.{{params.target_dataset_name}}.CHECKPOINT` where epoch = {{ti.xcom_pull(key="epoch", task_ids="current_epoch")}}

) =
(
SELECT COUNT(*) FROM `{{params.target_project_id}}.{{params.target_dataset_name}}.TRANSACTION` where epoch = {{ti.xcom_pull(key="epoch", task_ids="current_epoch")}}
), 1, 0 )