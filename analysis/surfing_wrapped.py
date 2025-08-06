import json
import os

from src.utils import NpEncoder

def create_surf_wrapped_json(surf_data_df, 
                             summary_by_year, 
                             ranked_summary_by_year,
                             json_output_folder):

    """
    This function creates a JSON file, per year, for the surfing-wrapped animation project.
    It includes the following data:
      - year
      - total number of sessions
      - total number of hours
      - total number of barrels
      - total number of unique spots surfed 
      - Single day with most hours in the water
      - Top 5 surf spots, by most amount of hours. With this data; spot name, region, total hours, number of sessions
      - Top 5 Surf sessions, by rank (parameter which includes wave quality, surf quality and barrel count). With this data; date, region, spot, wave quality, surf quality, barrel count

    Arguments:
        surf_data_df -- DataFrame containing the surf data
        summary_by_year -- DataFrame containing the summary by year
        ranked_summary_by_year -- DataFrame containing the ranked summary by year
        json_output_folder -- Folder where the JSON files will be saved
    """

    years = surf_data_df['year'].unique()

    top_spots_by_time_by_year = ranked_summary_by_year['top_spots_by_time']
    top_sessions_by_year = ranked_summary_by_year['top_sessions_by_rank']

    for year in years:
        surf_data_single_year = surf_data_df[surf_data_df['year'] == year]
        summary = summary_by_year[summary_by_year['year'] == year]
        top_spots_by_time = top_spots_by_time_by_year[top_spots_by_time_by_year['year'] == year]
        top_sessions = top_sessions_by_year[top_sessions_by_year['year'] == year]

        # For the top 5 spots, add in the total number of sessions
        # 1. inner join surf_data_single_year and top_spots_by_time on spot
        top_spots_n_sessions = top_spots_by_time.merge(surf_data_single_year, on=['subregion', 'spot'], how='inner')
        # 2. group by subregion, spot and count the number of sessions
        top_spots_n_sessions = (top_spots_n_sessions
                                .groupby(['subregion', 'spot'], as_index = False)
                                .agg(total_sessions=('spot', 'count')))
        # 3. merge the total_sessions into the top_spots_by_time
        top_spots_by_time = (top_spots_by_time.merge(top_spots_n_sessions, 
                                                    on=['subregion', 'spot'], 
                                                    how='left'))

        # For the top 5 sessions, add in the region, wave quality, surf quality and barrel count
        top_sessions_merge = top_sessions.merge(surf_data_single_year[['date', 'spot', 'region', 'wave_quality', 'surfing_quality', 'barrels_made']], 
                                                on=['date', 'spot'], 
                                                how='left')

        # "biggest_day" add in the single day with most hours in the water
        hours_per_day = surf_data_single_year.groupby('date')['hrs'].sum().reset_index()
        hours_per_day.columns = ['date', 'total_hours']
        biggest_day = hours_per_day.loc[hours_per_day['total_hours'].idxmax()]
        
        # Create a dictionary to hold the wrapped data
        wrapped_data = {
            'year': year,
            'total_sessions': summary['total_sessions'].values[0],
            'total_hours': summary['total_hours'].values[0],
            'total_barrels': summary['total_barrels_made'].values[0],
            'total_unique_spots': summary['total_unique_spots'].values[0],
            'biggest_day': biggest_day.to_dict(),
            'top_spots': top_spots_by_time.to_dict(orient='records'), 
            'top_sessions': top_sessions_merge.to_dict(orient='records')
        }

        # Save the wrapped data as a JSON file
        file_name = f'wrapped_data_{year}.json'
        output_file_path = os.path.join(json_output_folder, file_name)
        # create the output folder if it doesn't exist
        if not os.path.exists(json_output_folder):
            print(f"Creating output folder: {json_output_folder}")
            os.makedirs(json_output_folder, exist_ok=True)

        with open(output_file_path, 'w') as f:
            json.dump(wrapped_data, f, indent=4, cls=NpEncoder)
            print(f"Created JSON file: {output_file_path}")