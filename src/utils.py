import sys
import traceback
import google.cloud.logging
from google.cloud import storage


def print_stack():
    """
    catch stack after exception
    """
    # cath exception with sys and return the error stack
    ex_type, ex_value, ex_traceback = sys.exc_info()
    # Extract unformatter stack traces as tuples
    trace_back = traceback.extract_tb(ex_traceback)
    # Format stacktrace
    stack_trace = list()
    for trace in trace_back:
        stack_trace.append(
            "File : %s , Line : %d, Func.Name : %s, Message : %s"
            % (trace[0], trace[1], trace[2], trace[3])
        )
    error = ex_type.__name__ + "\n" + str(ex_value) + "\n"
    for err in stack_trace:
        error = error + str(err) + "\n"

    return error


def create_client_logging(vertex_credentials):

    client = google.cloud.logging.Client(credentials=vertex_credentials)
    return client


def upload_blob(bucket_name, source_file_name, destination_blob_name, credentials_path):
    """Uploads a file to a Cloud Storage bucket using a credentials file.
    Args:
        bucket_name (str): Name of the bucket to upload to
        source_file_name (str): Path to the file to upload
        destination_blob_name (str): Destination path in the bucket
        credentials_path (str): Path to the service account key file
    """
    # Initialize a storage client with the service account credentials
    # using the credentials file

    storage_client = storage.Client.from_service_account_json(credentials_path)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    # Upload the file to the bucket
    # The timeout is set to 300 seconds (5 minutes)
    blob.upload_from_filename(source_file_name, timeout=300)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")
