import os
from google.cloud import storage
from datetime import datetime
from typing import Optional
from datetime import datetime
import datetime

class GCSLoader:
    def __init__(self, credentials_path: str):
        """Initialize GCS loader with credentials"""
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        self.client = storage.Client()
        self.bucket_input = self.client.get_bucket('weather_input')
        # self.bucket_predict = self.client.get_bucket('weather_forecast_graphcast')

    def upload_file(self, 
                   local_file_path: str, 
                   bucket_name: str, 
                   destination_blob_name: Optional[str] = None) -> str:
        """
        Upload a file to GCS bucket
        
        Args:
            local_file_path: Path to local file
            bucket_name: Name of the bucket ('input' or 'predict')
            destination_blob_name: Optional custom name for the file in GCS
            
        Returns:
            str: The blob name in GCS
        """
        bucket = self.bucket_input
        
        if destination_blob_name is None:
            destination_blob_name = os.path.basename(local_file_path)
            
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_file_path)
        
        return destination_blob_name

    def upload_prediction_files(self, 
                              first_prediction: datetime,
                              input_file: str) -> tuple[str, str]:
        """
        Upload both input and prediction files to GCS
        
        Args:
            first_prediction: Datetime object for the prediction
            input_file: Path to local input file
            prediction_file: Path to local prediction file
            
        Returns:
            tuple: (input_blob_name, prediction_blob_name)
        """
        # Upload input file
        input_blob_name = f'inputs_hanoi_{first_prediction.day}_{first_prediction.month}.csv'
        self.upload_file(input_file, 'input', input_blob_name)
        
        # Upload prediction file
        # prediction_blob_name = f'predictions_hanoi_10d_from_{first_prediction.day}_{first_prediction.month}.csv'
        # self.upload_file(prediction_file, 'predict', prediction_blob_name)
        
        return input_blob_name

def load_to_gcs(credentials_path: str,
                first_prediction: datetime,
                input_file: str) -> None:
    """
    Main function to load files to GCS
    
    Args:
        credentials_path: Path to GCS credentials JSON file
        first_prediction: Datetime object for the prediction
        input_file: Path to local input file
        prediction_file: Path to local prediction file
    """
    try:
        loader = GCSLoader(credentials_path)
        input_blob = loader.upload_prediction_files(
            first_prediction,
            input_file
        )
        print(f"Successfully uploaded files to GCS:")
        print(f"- Input file: {input_blob}")
    except Exception as e:
        print(f"Error uploading files to GCS: {str(e)}")
        raise 