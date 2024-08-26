import pandas as pd

filename = "./archive/books_raw_data.csv"
outputFilename1 = "./archive/books01.csv"
outputFilename2 = "./archive/books02.csv"

def read_save_csv(input_file, output_file1, output_file2):
    df = pd.read_csv(input_file)
    df = df.dropna(subset=['Title', 'authors'])
    df = df[['Title', 'authors']]
    # Save the first 2000 rows to the first output file
    df.iloc[:2000].to_csv(output_file1, index=False)
    # Save rows 2001 to 4000 to the second output file
    if len(df) > 2000:
        df.iloc[2000:4000].to_csv(output_file2, index=False)
        
read_save_csv(filename, output_file1=outputFilename1, output_file2=outputFilename2)
