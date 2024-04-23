import pandas as pd

columns_to_string = ['Title', 'description', 'image', 'previewLink', 'publisher','publishedDate','infoLink', 'categories']

singleQuotationReplace="&#25"
doubleQuotationReplace="&#26"

def clean_cell_quotes(df):
    def clean_cell(value):
        if isinstance(value,str) and (len(value) > 1):
            # if value.startswith('"'): #dont know why not work
            #     value = value[1:]
            
            # if value.endswith('"'): #dont know why not work
            #     value = value[:-1]
                
            if any(char in value for char in ('"', "'")):
                value = value.translate(str.maketrans({'"': doubleQuotationReplace, "'": singleQuotationReplace}))
        return value
    return df.applymap(clean_cell)

def read_add_index_save_csv(input_file, output_file):
  # Read the CSV file using pandas
  df = pd.read_csv(input_file)
  #Index,Title,description,authors,image,previewLink,publisher,publishedDate,infoLink,categories,ratingsCount
  df = df[df['authors'].notna()]
  df = df[df['Title'].notna()]
  df = df[df['description'].notna()]
  df = df[df['categories'].notna()]
  df = df[df['ratingsCount'].notna()]
  df = df[df['publisher'].notna()]
  # Add an index column starting from 1 and insert it at the first position (loc=0)
  df.insert(loc=0, column='bookId', value=range(1, len(df) + 1))
  # df = df.astype({col: str for col in columns_to_string})
  
  # df = clean_cell_quotes(df)
  # Save the dataframe to a new CSV file
  df.to_csv(output_file, index=False)  # Don't save the index column in the output

# Example usage
input_file = "./archive/books_raw_data.csv"
output_file = "./archive/books_data.csv"
read_add_index_save_csv(input_file, output_file)
