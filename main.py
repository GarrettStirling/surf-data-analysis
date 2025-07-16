# import pandas as pd
import numpy as np
import os
from datetime import datetime

from src.setup import load_gsheet, concatenate_entries
from src.process import process_surf_data
from src.utils import check_n_distinct

def main(check_data = False):
    """
    Main function to read, process, and visualize my surf data.
    """

    # SETUP -------------------------------------------------------------------
  
    # Path to your JSON file (allows access to google sheet)
    sheet_access_key = 'keys/surf-data-analysis-b31fc887181f.json'
    # Spreadsheet ID (from the URL of the Google Sheet)
    sheet_url = '1DvfcN09E9cHPDe83N89AJtZhk-4DhxkxGLi8UsaR0Mw'

    # Load the Google Sheet data into a dictionary of dfs and then concatenate the surf data
    surf_data_dict = load_gsheet(sheet_url, sheet_access_key)
    surf_data_df_raw = concatenate_entries(surf_data_dict)

    # PROCESS ---------------------------------------------------------
    
    # process the surf data
    # i.e. remove columns, clean up headers, create date col, calculate wave height, etc.
    surf_data_df = process_surf_data(surf_data_df_raw,
                                     rm_incomplete_yrs = False)
    
    # CHECK -----------------------------------------------------------

    if check_data:

        # check for missing values across all columns, per year
        check_missing_values = False
        if check_missing_values:
            missing_values = surf_data_df.groupby('year').apply(lambda x: x.isna().sum())
            print("\nMissing Values:", missing_values)

        # Check surf spots and regions
        check_spots_and_regions = False
        if check_spots_and_regions:
            surf_data_df['region_spot'] = surf_data_df['sub_region'] + ' - ' + surf_data_df['spot']
            print("\nUnique Surf Spots:")
            check_n_distinct(surf_data_df, 'region_spot')
            print("\nUnique Regions:")
            check_n_distinct(surf_data_df, 'region_spot')

        # Check session counts
        check_session_counts = False
        if check_session_counts:
            print("\nTotal Sessions by Year:")
            print(surf_data_df.groupby(['year']).agg(session_count = ('year', 'count')).reset_index())
            print("\nTotal Sessions:", surf_data_df['year'].count())

        # Check unique values per column
        check_unique_vals_per_col = False
        if check_unique_vals_per_col:
            for col in surf_data_df:
                if not col in ['people', 'notes', 'visuals', 'date', 'day']:
                    unique_col = surf_data_df[col].unique()
                    unique_col_str = unique_col.astype(str)
                    unique_col_sort = np.sort(unique_col_str, axis=0)
                    print(unique_col_sort)


    # ANALYSES -------------------------------------------------
    # Specify the plot folder
    plot_folder = os.path.join(os.path.dirname(__file__), 'visuals')
    
    # SPOT ANALYSIS ----
    # Link historic NOAA data to surf-data and determine the conditions that lead to a spot being 'good' (i.e. wave quality of 8 or higher)
    # TODO: Add spot analysis here

    # ANNUAL SUMMARIES ----
    # to be used in after effect "surfing wrapped" video
    # Counts of things 
    #  - number of sessions, 
    #  - number of unique spots, 
    #  - number of unique regions, 
    #  - number of barrels, 
    #  - etc.
    # Top 5 of things 
    #  - top spots by time and session count, 
    #  - top 5 boards by time and session count, barrel count
    #  - top 5 session by rank (parameter which includes wave quality, surf quality and barrel count)

    # SURFBOARD ANALYSIS ----
    from analysis.surfboards import (process_surfboard_hrs, 
                                     plot_surfboard_hrs,
                                     process_surfboard_lifetime,
                                     plot_surfboard_lifetime)

    # Process and plot the amount of hours with each surfboard by region
    surfboard_hrs_df = process_surfboard_hrs(surf_data_df, surf_data_dict)
    plot_surfboard_hrs(surfboard_hrs_df,
                       plot_folder=plot_folder)

    # process and plot a gantt-timeline with each surfboard
    surfboard_min_max_df = process_surfboard_lifetime(surf_data_df, surf_data_dict)
    plot_surfboard_lifetime(surfboard_min_max_df,
                            plot_folder=plot_folder)
    # new analysis; surfboard length over time
    # TODO: maybe average length per month - weighted by hours used?

    # REGION ANALYSIS ----
    # TODO: ADD IN


if __name__ == "__main__":
    main(check_data=False)