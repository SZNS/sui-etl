select if(
(
  SELECT count(sequence_number) FROM `{{params.target_project_id}}.{{params.target_dataset_name}}.CHECKPOINT` where epoch = {{ti.xcom_pull(key="epoch", task_ids="prepare")}}

) > 0, 1, 0)