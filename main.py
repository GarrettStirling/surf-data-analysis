# import pandas as pd
import numpy as np
import os

from src.setup import load_gsheet, concatenate_entries
from src.process import process_surf_data
from src.utils import check_n_distinct

def main(check_data=False,
         save_plots=False):
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
    # New columns added: date, region, subregion_spot session_value
    surf_data_df = process_surf_data(surf_data_df_raw, rm_incomplete_yrs = False)
    
    # CHECK -----------------------------------------------------------

    if check_data:
        # Toggles
        check_missing_values      = False
        check_unique_vals_per_col = False
        check_spots_and_regions   = False

        # check for missing values across all columns, per year
        if check_missing_values:
            missing_values = surf_data_df.groupby('year').apply(lambda x: x.isna().sum())
            print("\nMissing Values:", missing_values)

        # Check unique values per column
        if check_unique_vals_per_col:
            for col in surf_data_df:
                if not col in ['people', 'notes', 'visuals', 'date', 'day']:
                    unique_col = surf_data_df[col].unique()
                    unique_col_str = unique_col.astype(str)
                    unique_col_sort = np.sort(unique_col_str, axis=0)
                    print(unique_col_sort)

        # Check surf spots and regions
        if check_spots_and_regions:
            print("\nUnique Surf Spots:")
            check_n_distinct(surf_data_df, 'subregion_spot')
            print("\nUnique SubRegions:")
            check_n_distinct(surf_data_df, 'subregion')


    # ANALYSES -------------------------------------------------
    
    # INITIALIZE THINGS ----
   
    if save_plots:
        # Specify the plot folder
        plot_folder = os.path.join(os.path.dirname(__file__), 'output', 'visuals')
    else:
        save_plots = None

    # SUMMARISE DATA ----
    from analysis.summarise import (create_simple_summary, 
                                    create_ranked_summary)
    
    # Basic, single values per year and per year+month
    summary_by_year = create_simple_summary(surf_data_df, group_cols=['year'])
    summary_by_year_month = create_simple_summary(surf_data_df, group_cols=['year', 'month'])

    # Ranked Summaries (dictionary objects)
    ranked_summary = create_ranked_summary(surf_data_df, by_year=False)
    ranked_summary_by_year = create_ranked_summary(surf_data_df)
    
    # view the dictionary of ranked summaries
    print_summaries = False
    if print_summaries:
        print("\nRanked Summary:")
        for key, value in ranked_summary.items():
            print(f"{key}:\n{value}\n")
        print("\nRanked Summary by Year:")
        for key, value in ranked_summary_by_year.items():
            print(f"{key}:\n{value}\n")

    # ALL DATA ANALYSIS ----
    from analysis.annual_plot import plot_annual_summaries
    plot_annual_summaries(summary_by_year_month, plot_folder=plot_folder)
    plot_annual_summaries(summary_by_year, plot_folder=plot_folder)

    # SURF DATA WRAPPED ----
    # create and save (as JSON) the data needed for the surfing-wrapped animation project
    surf_wrapped = False
    if surf_wrapped:
        from analysis.surfing_wrapped import create_surf_wrapped_json
        # Create the JSON output folder
        json_output_folder = os.path.join(os.path.dirname(__file__), 'output', 'surfing_wrapped')
        create_surf_wrapped_json(surf_data_df, summary_by_year, ranked_summary_by_year, json_output_folder)

    # SURFBOARD ANALYSIS ----
    surfboard_analysis = False
    if surfboard_analysis:
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
    from analysis.regions import (process_region_hours, 
                                  plot_regions_across_time,
                                  process_time_of_day,
                                  plot_time_of_day)

    # plot the hours per region across time, binned by month
    region_hours_df = process_region_hours(surf_data_df)
    plot_regions_across_time(region_hours_df,
                             plot_folder=plot_folder)
    # plot the time of day surfed, separated by region
    time_of_day_df = process_time_of_day(surf_data_df)
    plot_time_of_day(time_of_day_df,
                     plot_folder=plot_folder)


    # WETSUIT ANALYSIS ----
    # TODO: ADD
    

    # SPOT ANALYSIS ----
    # Link historic NOAA data to surf-data and determine the conditions that lead to a spot being 'good' (i.e. wave quality of 8 or higher)
    # TODO: ADD

    #TEMP
    print("BREAKPOINT")

if __name__ == "__main__":
    main(check_data=False,
         save_plots=True)