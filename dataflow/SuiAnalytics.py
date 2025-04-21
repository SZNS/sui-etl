# TODO: Add license
import argparse
import logging
import json

from apache_beam import DoFn, io, ParDo, Pipeline, WindowInto, Map
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.window import FixedWindows
from apache_beam.error import TransformError

from google.cloud import bigquery


class UploadToBigQuery(DoFn):
    def __init__(self, target_project, dataset_name, table_name):
        self.target_project = target_project
        self.dataset_name = dataset_name
        self.table_name = table_name

    def process(self, element):
        client = bigquery.Client(project=self.target_project)
        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.CSV
        job_config.field_delimiter = "|"
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
        job_config.allow_quoted_newlines = True
        job_config.ignore_unknown_values = True

        table_ref = client.dataset(self.dataset_name).table(self.table_name)
        load_job = client.load_table_from_uri(element, table_ref, job_config=job_config)

        try:
            logging.info("Loading in: {file}".format(file=element))
            logging.info("Job metadata: " + json.dumps(job_config.to_api_repr()))
            result = load_job.result()
            logging.info(result)
            assert load_job.errors is None or len(load_job.errors) == 0
        except Exception:
            logging.info(load_job.errors)
            raise


def run(
    input_sub,
    target_project,
    dataset_name,
    table_name,
    window_size=1.0,
    pipeline_args=None,
):
    # Set `save_main_session` to True so DoFns can access globally imported modules.
    pipeline_options = PipelineOptions(
        pipeline_args, streaming=True, save_main_session=True
    )

    with Pipeline(options=pipeline_options) as pipeline:
        # Get the number of appearances of a word.
        def getFileFromMessage(message):
            message_body_object = json.loads(message)

            # The id field contains the full path
            bucket = message_body_object["bucket"]
            name = message_body_object["name"]

            file_path = f"gs://{bucket}/{name}"

            return file_path

        # Pub/Sub
        (
            pipeline
            | "Read from Pub/Sub" >> io.ReadFromPubSub(subscription=input_sub)
            | "Window into" >> WindowInto(FixedWindows(window_size * 60))
            | "Get new file names" >> Map(getFileFromMessage)
            | "Write to BigQuery"
            >> ParDo(UploadToBigQuery(target_project, dataset_name, table_name))
        )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input_sub",
        help="The Cloud Pub/Sub subscription to read from. In format "
        '"projects/<project_id>/subscriptions/<SUB_ID>".',
        required=True,
    )
    parser.add_argument(
        "--target_project",
        help="Project ID where where BigQuery table exists",
        required=True,
    )

    parser.add_argument(
        "--dataset_name",
        help="Dataset name where where BigQuery table exists",
        required=True,
    )

    parser.add_argument(
        "--table_name", help="The BigQuery table to export data", required=True
    )

    parser.add_argument(
        "--window_size",
        type=float,
        default=1.0,
        help="Output file's window size in minutes.",
    )

    known_args, pipeline_args = parser.parse_known_args()

    run(
        known_args.input_sub,
        known_args.target_project,
        known_args.dataset_name,
        known_args.table_name,
        known_args.window_size,
        pipeline_args,
    )
