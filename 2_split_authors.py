import pandas as pd

##bookId,Title,description,authors,image,previewLink,publisher,publishedDate,infoLink,categories,ratingsCount

#FIRST file: bookId, description, image, previewLink, publisher, publishedDate,infoLink, categories, ratingsCount
#SECOND file: bookId, Title
#Third File: Title, author

def split_csv_by_criteria(input_file, output_prefix):  
  df = pd.read_csv(input_file)

  exclude_cols = ['bookId', 'authors']
  third_file_cols = ['Title', 'authors'] ##has multi author, so need to seperate to multiple

  # Split dataframes based on criteria
  first_file_df = df.drop(exclude_cols, axis=1)
  # second_file_df = df[second_file_cols]
  third_file_df = df[third_file_cols]

  # Generate filenames
  first_file = f"{output_prefix}_no_author.csv"
  # second_file = f"{output_prefix}_id_title.csv"
  third_file = f"{output_prefix}_title_authors.csv"

  # Save dataframes to separate CSV files
  first_file_df.to_csv(first_file, index=False)
  # second_file_df.to_csv(second_file, index=False)
  third_file_df.to_csv(third_file, index=False)
  
  print(f"Split CSV completed. Files generated: {first_file}, {third_file}")

# Example usage
input_file = "./archive/books_data.csv"
output_prefix = "./archive/split_data"
split_csv_by_criteria(input_file, output_prefix)
