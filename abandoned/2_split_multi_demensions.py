import pandas as pd

##bookId,Title,description,authors,image,previewLink,publisher,publishedDate,infoLink,categories,ratingsCount

#FIRST file: bookId, description, image, previewLink, publisher, publishedDate,infoLink, categories, ratingsCount
#SECOND file: bookId, Title
#Third File: Title, author

def split_csv_by_criteria(input_file, output_prefix):  
  df = pd.read_csv(input_file)

  exclude_cols = ['categories', 'publisher']
  third_file_cols = ['Title', 'authors'] ##has multi author, so need to seperate to multiple
  fourth_file_cols = ['Title', 'categories']
  fifth_file_cols = ['Title', 'publisher']

  # Split dataframes based on criteria
  first_file_df = df.drop(exclude_cols, axis=1)
  # second_file_df = df[second_file_cols]
  third_file_df = df[third_file_cols]
  fourth_file_df = df[fourth_file_cols]
  fifth_file_df = df[fifth_file_cols]

  # Generate filenames
  first_file = f"{output_prefix}_title_information.csv"
  # second_file = f"{output_prefix}_id_title.csv"
  third_file = f"{output_prefix}_title_authors.csv"
  fourth_file = f"{output_prefix}_title_categories.csv"
  fifth_file = f"{output_prefix}_title_publisher.csv"

  # Save dataframes to separate CSV files
  first_file_df.to_csv(first_file, index=False)
  # second_file_df.to_csv(second_file, index=False)
  third_file_df.to_csv(third_file, index=False)
  fourth_file_df.to_csv(fourth_file, index=False)
  fifth_file_df.to_csv(fifth_file, index=False)
  
  print(f"Split CSV completed. Files generated: {first_file}, {third_file}, {fourth_file}, {fifth_file}")

# Example usage
input_file = "./archive/books_data_0.csv"
output_prefix = "./archive/split_data"
split_csv_by_criteria(input_file, output_prefix)
