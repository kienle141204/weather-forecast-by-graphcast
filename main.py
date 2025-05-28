import os
from datetime import datetime
import datetime
import cdsapi
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from extract import get_single_and_pressure_values
from transform import (
    integrate_progress, format_data, get_targets,
    get_forcings, make_xarray
)

from load import load_to_gcs

def main():
    # Load environment variables
    load_dotenv('config/key_cds.txt')

    # Initialize CDS client
    client = cdsapi.Client(
        url="https://cds.climate.copernicus.eu/api",
        key=os.getenv("CDS_API_KEY")
    )

    # Set up time range for prediction
    first_prediction = (datetime.datetime.now() - datetime.timedelta(days=7)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # Extract data
    print("Extracting data from CDS...")
    single, pressure = get_single_and_pressure_values(client, first_prediction)

    # Transform data
    print("Transforming data...")
    values = {}
    values['inputs'] = pd.merge(pressure, single, left_index=True, right_index=True, how='inner')
    values['inputs'] = integrate_progress(values['inputs'])
    values['inputs'] = format_data(values['inputs'])
    values['targets'] = get_targets(first_prediction, values['inputs'])
    values['forcings'] = get_forcings(values['targets'])
    
    # Convert to xarray format
    values = {value: make_xarray(values[value]) for value in values}

    # Save input data
    input_file = f'inputs_hanoi_{first_prediction.day}.csv'
    values['inputs'].to_dataframe().to_csv(input_file, sep=',')

    # Load files to GCS
    print("Loading files to Google Cloud Storage...")
    load_to_gcs(
        credentials_path='config/silicon-stock-452315-h4-1159b7c155af.json',
        first_prediction=first_prediction,
        input_file=input_file,
        # prediction_file=prediction_file
    )

if __name__ == "__main__":
    main() 