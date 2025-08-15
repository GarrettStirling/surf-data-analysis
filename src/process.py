from tracemalloc import start
import pandas as pd

from src.utils import to_snake_case, convert_numeric_columns, calc_avg_wave_height, check_row_counts, assign_season


# add regions (level above the regions defined in the sheet)
def add_regions(df):
    """
    Add regions to the DataFrame based on subregion.
    """

    # read in the region_general_dictionary .csv file in the input folder
    region_map = pd.read_csv('input/region_map.csv', index_col='subregion').to_dict()['region']

    # map the subregion to the region
    df['region'] = df['subregion'].map(region_map).fillna('Other')

    return df

# Main function to process the surf data DataFrame
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
          .rename(columns={'region': 'subregion'}))
    
    # Calculate Average Wave Height
    df = calc_avg_wave_height(df)

    # check that row counts are the same (before filtering step below)
    check_row_counts(df_0, df)

    # Remove incomplete years. i.e.;
    #  - 2017 because it starts with Feb
    #  - the current year because only partly through
    if rm_incomplete_yrs:
        df = df.query("year != 2017 and year != @current_year")

    # Add regions (a level up from the region in the sheet)
    # e.g. Spot = 'Seaside', Subregion = 'San Diego', Region = 'Southern California'
    df = add_regions(df)

    # add a column which is the region + spot name
    df['subregion_spot'] = df['subregion'] + ' - ' + df['spot']

    # add new parameter which is the "session value" which is the sum of wave quality, surf quality and barrel count
    df['session_value'] = (df[['wave_quality', 'surfing_quality', 'barrels_made']].sum(axis=1, skipna=True))

    # add in the seasons
    df['season'] = df['month'].apply(assign_season)

    # add in a session_id which is a 3-digit number, restarting per year
    df['session_id'] = df.groupby('year').cumcount() + 1
    df['session_id'] = df['session_id'].astype(str).str.zfill(3)

    return df

