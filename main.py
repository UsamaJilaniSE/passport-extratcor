from fastapi import FastAPI
from typing import List, Sequence

from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai
import pandas as pd
import json

app = FastAPI()


@app.get("/")
async def root():

    PROJECT_ID = "model-finetuning"
    LOCATION = "us"  # Format is 'us' or 'eu'
    PROCESSOR_ID = "50bb661f94252acd"  # Create processor in Cloud Console

    # The local file in your current working directory
    FILE_PATH = "sample3.jpg"
    # Refer to https://cloud.google.com/document-ai/docs/processors-list
    # for supported file types
    MIME_TYPE = "image/jpeg"

    document = online_process(
        project_id=PROJECT_ID,
        location=LOCATION,
        processor_id=PROCESSOR_ID,
        file_path=FILE_PATH,
        mime_type=MIME_TYPE,
    )
    passport_data =extract_types_and_mention_text(document)
    passport_data_final = convert_dict_format(passport_data)
    return passport_data_final



#------------functions------------------

# mypy: disable-error-code="1"
# pylint: skip-file
"""
Makes a Online Processing Request to Document AI
"""


def online_process(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
) -> documentai.Document:
    """
    Processes a document using the Document AI Online Processing API.
    """

    # Instantiates a client
    docai_client = documentai.DocumentProcessorServiceClient(
        client_options=ClientOptions(
            api_endpoint=f"{location}-documentai.googleapis.com"
        )
    )

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first
    resource_name = docai_client.processor_path(project_id, location, processor_id)

    # Read the file into memory
    with open(file_path, "rb") as file:
        file_content = file.read()

    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)

    # Configure the process request
    request = documentai.ProcessRequest(name=resource_name, raw_document=raw_document)

    # Use the Document AI client to process the sample form
    result = docai_client.process_document(request=request)

    return result.document.entities


def extract_types_and_mention_text(data):
    results = []
    for entry in data:
        type_ = entry.type_
        mention_text = entry.mention_text
        result = {
            "type": type_,
            "mention_text": mention_text
        }
        results.append(result)

    return json.dumps(results, indent=2)


def convert_dict_format(data):
    data_list = json.loads(data)
    converted_data = []
    for item in data_list:
        new_item = {item['type']: item['mention_text']}
        converted_data.append(new_item)
    return converted_data