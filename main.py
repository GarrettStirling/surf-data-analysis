# import pandas as pd
import numpy as np

from src.setup import load_gsheet, concatonate_entries
from src.process import process_surf_data

def main(check_data = True):
    """
    Main function to read, process, and visualize my surf data.
    """

    # SETUP -------------------------------------------------------------------
  
    # Path to your JSON file (allows access to google sheet)
    sheet_access_key = 'keys/surf-data-analysis-b31fc887181f.json'
    # Spreadsheet ID (from the URL of the Google Sheet)
    sheet_url = '1DvfcN09E9cHPDe83N89AJtZhk-4DhxkxGLi8UsaR0Mw'

    # Load the Google Sheet data into a dictionary of dfs and then concatonate the surf data
    surf_data_dict = load_gsheet(sheet_url, sheet_access_key)
    surf_data_df_raw = concatonate_entries(surf_data_dict)

    # PROCESS ---------------------------------------------------------
    
    # process the surf data
    # i.e. remove columns, clean up headers, create date col, calculate wave height, etc.
    surf_data_df = process_surf_data(surf_data_df_raw,
                                     rm_incomplete_yrs = False)
    
    # CHECK -----------------------------------------------------------

    if check_data:
        # TODO: turn each of the sections below into functions

        check_missing_values = False
        if check_missing_values:
            # check for missing values across all columns, per year
            missing_values = surf_data_df.groupby('year').apply(lambda x: x.isna().sum())
            print("\nMissing Values:", missing_values)

        check_spots_and_regions = False
        if check_spots_and_regions:
            # Check surf spots
            surf_data_df['region_spot'] = surf_data_df['sub_region'] + ' - ' + surf_data_df['spot']
            unique_spot_regions = surf_data_df['region_spot'].value_counts().reset_index()
            print("\nUnique Surf Spots:")
            for item in unique_spot_regions.sort_values(by='region_spot').itertuples():
                print(f"{item.region_spot}: {item.count}")
            # Check regions
            unique_regions = surf_data_df['sub_region'].value_counts().reset_index()
            print("\nUnique Regions:")
            for item in unique_regions.sort_values(by='sub_region').itertuples():
                print(f"{item.sub_region}: {item.count}")

        check_session_counts = False
        if check_session_counts:
            # Check amount of sessions
            print("\nTotal Sessions by Year:")
            print(surf_data_df.groupby(['year']).agg(session_count = ('year', 'count')).reset_index())
            # Print the total count of sessions
            print("\nTotal Sessions:", surf_data_df['year'].count())

        check_unique_vals_per_col = False
        if check_unique_vals_per_col:
            for col in surf_data_df:
                if not col in ['people', 'notes', 'visuals', 'date', 'day']:
                    unique_col = surf_data_df[col].unique()
                    unique_col_str = unique_col.astype(str)
                    unique_col_sort = np.sort(unique_col_str, axis=0)
                    print(unique_col_sort)

    # add break point
    print("STOP HERE")

    # SPOT ANALYSIS -------------------------------------------------
    # Link historic NOAA data to surf-data and determine the conditions that lead to a spot being 'good' (i.e. wave quality of 8 or higher)

    # TODO: Add spot analysis here

    # ANNUAL DATA EXPORT -------------------------------------
    # to be used in after effect "surfing wrapped" video

    # Counts of things 
    #  - number of sessions, 
    #  - number of unique spots, 
    #  - number of unique regions, 
    #  - number of barrels, 
    #  - etc.
    # TODO: ADD IN

    # Top 5 of things 
    #  - top spots by time and session count, 
    #  - top 5 boards by time and session count, barrel count
    #  - top 5 session by rank (parameter which includes wave quality, surf quality and barrel count)
    # TODO: ADD IN

    # PLOTS ----------------------------------------------------------

    # (a) Surfboard Analysis
    # TODO: ADD IN

    # (b) Region Analysis
    # TODO: ADD IN

if __name__ == "__main__":
    main()