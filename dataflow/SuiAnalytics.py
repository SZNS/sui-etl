# TODO: Add license
import argparse
import logging
import json

from apache_beam import (
    DoFn,
    io,
    ParDo,
    Pipeline,
    WindowInto,
    Map
)
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.window import FixedWindows
from apache_beam.error import TransformError

# Format the csv row into a BigQuery row
class FormatRow(DoFn):
    def __init__(self, schema, type):
        self.schema = schema
        self.type = type

    def process(self, element):
        # Get column names
        col_names_itr = map(lambda field: field['name'], self.schema['fields'])
        col_names = list(col_names_itr)

        # Split row data delimited by the '|' char
        # For type object the `object_json` sometimes contains '|' characters in the 'object_json' column so we need to set max splits to the number of columns for this data type
        values = element.split("|", len(col_names) - 1)

        # Check number of columns match number of values in csv
        if len(col_names) != len(values):
            raise TransformError('Mismatch length between columns and values')

        # Correlate column and values
        # Remove any null values since the BigQuery SDK cannot import '' as NULL
        key_val = ((col, val)
                   for col, val in zip(col_names, values) if col and val)

        # Turn into row
        row = dict(key_val)


        # Object types need the JSON cleanup for the object_json column
        if self.type == "object" :
            # ref: https://cloud.google.com/bigquery/docs/json-data#use_the_legacy_streaming_api
            # Convert csv encoded json to json string
            object_json = row.get('object_json')
            if object_json:
                # remove extra quotes
                tmp = object_json[1:-1]

                # Replace double quotes
                updated_obj = tmp.replace('""', '"')
                row.update({
                    'object_json': updated_obj
                })

        return [row]


def run(type, input_sub, output_table, window_size=1.0, pipeline_args=None):
    # Set `save_main_session` to True so DoFns can access globally imported modules.
    pipeline_options = PipelineOptions(
        pipeline_args, streaming=True, save_main_session=True
    )

    # Set the schema
    with open((f'schema/{type}.json'), 'r') as f:
        schema = json.load(f)

    with Pipeline(options=pipeline_options) as pipeline:
        # Get the number of appearances of a word.
        def getFileFromMessage(message):
            message_body_object = json.loads(message)

            # The id field contains the full path
            bucket = message_body_object['bucket']
            name = message_body_object['name']

            file_path = f"gs://{bucket}/{name}"

            return file_path
        print(input_sub)
        # Pub/Sub
        (
            pipeline
            | "Read from Pub/Sub" >> io.ReadFromPubSub(subscription=input_sub)
            | "Window into" >> WindowInto(FixedWindows(window_size * 60))
            | "Get new file names" >> Map(getFileFromMessage)
            | "Read files" >> io.ReadAllFromText()
            | 'Format' >> ParDo(FormatRow(schema, type))
            | 'Write to bigquery' >> io.WriteToBigQuery(
                table=output_table,
                schema=schema,
                create_disposition=io.BigQueryDisposition.CREATE_NEVER,
                write_disposition=io.BigQueryDisposition.WRITE_APPEND
            )
        )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--type",
        help="The type of data to process.",
        choices=["checkpoint", "event", "move_call", "move_package", "object", "transaction_object", "transaction"]
    )

    parser.add_argument(
        "--input_sub",
        help="The Cloud Pub/Sub subscription to read from."
        '"projects/<PROJECT_ID>/subscriptions/<SUB_ID>".',
    )
    parser.add_argument(
        "--output_table",
        help="Table to write data. In format [PROJECT:DATASET.TABLE] or [DATASET.TABLE]",
    )

    parser.add_argument(
        "--window_size",
        type=float,
        default=1.0,
        help="Output file's window size in minutes.",
    )

    known_args, pipeline_args = parser.parse_known_args()

    run(
        known_args.type,
        known_args.input_sub,
        known_args.output_table,
        known_args.window_size,
        pipeline_args,
    )
