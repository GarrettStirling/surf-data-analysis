from tracemalloc import start
import pandas as pd
import time

from src.utils import to_snake_case, convert_numeric_columns, calc_avg_wave_height, check_row_counts, new_col_from_dict

def process_surf_data(df,
                      rm_cols = ['Visuals', 'Notes', 'BUOY Data'],
                      rm_incomplete_yrs = True):
    """
    Main function to process the raw surf data DataFrame.
    """
    # Make a copy of the df so we can check row counts later
    df_0 = df.copy()
    
    # Remove the specified columns
    df = df.drop(columns=rm_cols, errors='ignore')

    # Update columns to snake case
    df.columns = [to_snake_case(col) for col in df.columns]

    # Replace empty values with NA
    df = df.replace(['', ' ', 'NA', 'N/A', 'n/a', 'na'], pd.NA)
    # Replace NaN values with NA
    df.fillna(pd.NA, inplace=True)

    # Convert columns to numeric if all values are numeric
    df = convert_numeric_columns(df)

    # Create date column
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

    # Sort by date and rename columns
    df = (df
        .sort_values(by='date', ignore_index=True)
        .rename(columns={'region': 'sub_region'}))
    
    # Calculate Average Wave Height
    df = calc_avg_wave_height(df)

    # check that row counts are the same (before filtering step below)
    check_row_counts(df_0, df)

    # Remove incomplete years. i.e.;
    #  - 2017 because it starts with Feb
    #  - the current year because only partly through
    if rm_incomplete_yrs:
        # current_year = datetime.now().year
        df = df.query("year != 2017 and year != @current_year")

    # Add regions
    df = add_regions(df)

    return df


# add regions (level above the regions in the sheet)
def add_regions(df):
    """
    Add regions to the DataFrame based on sub_region.
    """

    # read in the region_general_dictionary .csv file in the input folder
    region_map = pd.read_csv('input/region_map.csv', index_col='sub_region').to_dict()['region']

    # map the sub_region to the region
    df['region'] = df['sub_region'].map(region_map).fillna('Other')

    return df