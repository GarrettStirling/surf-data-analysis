import re
import pandas as pd
import statistics
import matplotlib.pyplot as plt
from datetime import datetime
import os

# function to assert that two dataframes have the same number of rows
def check_row_counts(df1, df2):
  assert len(df1) == len(df2), "Number of rows have changed"


# Function to convert a string to snake_case
def to_snake_case(string):
    string = re.sub(r'(?<=[a-z])(?=[A-Z])|[^a-zA-Z]', ' ', string).strip().replace(' ', '_')
    return string.lower()


# Function to convert columns to numeric if all values are numeric
def convert_numeric_columns(df):
    for col in df.columns:
        try:
            # Attempt to convert the entire column to numeric
            df[col] = pd.to_numeric(df[col], errors='raise')
        except (ValueError, TypeError):
            # If conversion fails for any value, skip this column
            pass
    return df


# Function to average the wave height for a sheet
def calc_avg_wave_height(df):

  # initialize vector
  wave_ht_avg = []
  for wave_height in df["wave_height"]:
    # if NA value, keep NA
    if pd.isna(wave_height):
      wave_ht_avg.append(pd.NA)
    # If we have a single numeric value, use that
    elif wave_height.isnumeric():
      wave_ht_avg.append(wave_height)
    # if not single numeric value, then calculate the average
    else:
      # force all these values to be strings
      wave_height_str = str(wave_height)
      # change all '-' to ',' then split by comma
      vals = wave_height_str.replace('-', ',').split(',')
      # now make each str we split and turn them into ints
      vals_int = map(int, vals)
      # get average of the two values
      avg = statistics.mean(vals_int)
      # append this avg to the vector we initialized
      wave_ht_avg.append(avg)
  # Put values into the dataframe
  df["wave_height_avg"] = wave_ht_avg
  return df


# Add a column, based on a dictionary map using vals in a reference column
def new_col_from_dict(row, dict_map, ref_col):
    return dict_map.get(row[ref_col], 'Other')


# Assign seasons based on month
def assign_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Fall'
    else:
        return 'Unknown'  # Handle cases outside the 1-12 range


def check_n_distinct(df, col):
    val_counts = df[col].value_counts().reset_index().sort_values(by=col)
    for row in val_counts.itertuples():
        print(f"{row[1]}: {row[2]}")


# save two versions of a file, 
# 1. undated, in main folder
# 2. dated, in a subfolder with the current date (to keep historical versions)
def save_plt_dated(plot_folder, filename):
    current_date = datetime.now().strftime("%Y%m%d")
    filename_dated = f'{current_date}_{filename}'
    
    output_file_path = os.path.join(plot_folder, filename)
    output_file_path_dated = os.path.join(plot_folder, current_date, filename_dated)
    # if output_file_path_dated doesn't exist, create the folder
    if not os.path.exists(os.path.dirname(output_file_path_dated)):
        os.makedirs(os.path.dirname(output_file_path_dated))

    plt.savefig(output_file_path)
    plt.savefig(output_file_path_dated)

# save two versions of a file, 
# 1. undated, in main folder
# 2. dated, in a subfolder with the current date (to keep historical versions)
def save_csv_dated(plot_folder, filename, df):
    current_date = datetime.now().strftime("%Y%m%d")
    filename_dated = f'{current_date}_{filename}'
    
    output_file_path = os.path.join(plot_folder, filename)
    output_file_path_dated = os.path.join(plot_folder, current_date, filename_dated)
    # if output_file_path_dated doesn't exist, create the folder
    if not os.path.exists(os.path.dirname(output_file_path_dated)):
        os.makedirs(os.path.dirname(output_file_path_dated))

    df.to_csv(output_file_path, index=False)
    df.to_csv(output_file_path_dated, index=False)