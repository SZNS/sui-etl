select if(
(
  SELECT count(sequence_number) FROM `{{params.project_id}}.{{params.dataset_name}}.CHECKPOINT` where epoch = {{ti.xcom_pull(key="epoch", task_ids="current_epoch")}}

) > 0, 1, 0)