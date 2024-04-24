import pandas as pd
import os

def split_csv_pandas(input_file, output_prefix, chunksize=10000):
  reader = pd.read_csv(input_file, iterator=True, chunksize=chunksize)
  file_counter = 0
  for chunk in reader:
    output_file = f"{output_prefix}_{file_counter}.csv"
    # Check if file already exists and create a new filename with a counter if needed
    while os.path.exists(output_file):
      file_counter += 1
      output_file = f"{output_prefix}_{file_counter}.csv"
    chunk.to_csv(output_file, index=False)

# Example usage
split_csv_pandas("./archive/books_data.csv", "./archive/books_data", 2000)
