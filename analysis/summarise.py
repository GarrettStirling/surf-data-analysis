# Basic, single values per year
def create_simple_summary(df, group_cols):
    """
    Create an simple summary of surf data, grouped over any time variables.
    Arguments:
        df: DataFrame to summarise
        group_cols: List of columns to group by (e.g., ['year'], ['year', 'month'])
    """
    annual_summary = (df
        .groupby(group_cols, as_index=False)
        .agg(total_hours=('hrs', 'sum'),
             total_sessions=('year', 'count'),
             total_unique_spots=('spot', 'nunique'),
             total_unique_subregions=('subregion', 'nunique'),
             total_unique_regions=('region', 'nunique'),
             total_barrels_made=('barrels_made', 'sum'),
             most_freq_spot=('spot', lambda x: x.value_counts().index[0] if not x.isna().all() else None),
             most_freq_subregion=('subregion', lambda x: x.value_counts().index[0] if not x.isna().all() else None),
             most_freq_region=('region', lambda x: x.value_counts().index[0] if not x.isna().all() else None),
             most_freq_board=('board', lambda x: x.value_counts().index[0] if not x.isna().all() else None),
             most_freq_wetsuit=('wetty', lambda x: x.value_counts().index[0] if not x.isna().all() else None))
        .reset_index())

    return annual_summary

# Function to summarise the data - top n by variable and aggregation type
# e.g. Top 5 Spots by Time
def top_n_by_agg_type(df,
                      grp_cols,
                      top_n,
                      agg_type,
                      agg_col,
                      by_year = True):
    """ 
    Create a summary DataFrame with the top n by aggregation type
    Arguments:
        df: DataFrame to summarise
        grp_cols: List of columns to group by
        top_n: Number of top entries to return
        agg_type: Aggregation type (e.g., 'count', 'sum', 'mean')
        agg_col: Column to aggregate on
        by_year: Whether to group by year or not
    """
    if by_year:
        # Add year to group columns if not already present
        if 'year' not in grp_cols:
            grp_cols = ['year'] + grp_cols

    # develop aggregation per group
    summary_df = (df
                  .groupby(grp_cols, as_index = False)
                  .agg(agg = (agg_col, agg_type)))

    if by_year:
        # add rank column   
        summary_df['rank'] = (summary_df
            .groupby('year')['agg']
            .rank(method='first', ascending=False))
        # filter to only top n
        top_n_per_group = (summary_df[summary_df['rank'] <= top_n]
                        .sort_values(['year', 'rank'])
                        .drop(columns=['rank']))
    else:
        # add rank column   
        summary_df['rank'] = summary_df['agg'].rank(method='first', ascending=False)
        # filter to only top n
        top_n_per_group = (summary_df[summary_df['rank'] <= top_n]
                           .sort_values(['rank'])
                           .drop(columns=['rank']))

    return top_n_per_group

def create_ranked_summary(surf_data_df, top_n=5, by_year=True):

    """
    Create a dictionary of ranked spots, boards, and sessions by different parameters.
    Arguments:
        surf_data_df: DataFrame to summarise
        top_n: Number of top entries to return
        by_year: Whether to group by year or not

    """
    
    # Create a dictionary to hold the ranked summaries
    ranked_summary_dict = {}

    # Top Spots by Count
    ranked_summary_dict['top_spots_by_count'] = top_n_by_agg_type(
        surf_data_df,
        grp_cols=['subregion', 'spot'],
        top_n=top_n,
        agg_type='count',
        agg_col='spot',
        by_year=by_year).rename(columns = {'agg': 'session_count'})
    # Top Spots by Time
    ranked_summary_dict['top_spots_by_time'] = top_n_by_agg_type(
        surf_data_df,
        grp_cols=['subregion', 'spot'],
        top_n=top_n,
        agg_type='sum',
        agg_col='hrs',
        by_year=by_year).rename(columns = {'agg': 'total_hours'})
    # Top Spots by Barrels Made
    ranked_summary_dict['top_spots_by_barrels'] = top_n_by_agg_type(
        surf_data_df,
        grp_cols=['subregion', 'spot'],
        top_n=top_n,
        agg_type='sum',
        agg_col='barrels_made',
        by_year=by_year).rename(columns = {'agg': 'total_barrel_count'})
    # Top Boards by Count
    ranked_summary_dict['top_boards_by_count'] = top_n_by_agg_type(
        surf_data_df,
        grp_cols=['board'],
        top_n=top_n,
        agg_type='count',
        agg_col='board',
        by_year=by_year).rename(columns = {'agg': 'session_count'})
    # Top Boards by Time
    ranked_summary_dict['top_boards_by_time'] = top_n_by_agg_type(
        surf_data_df,
        grp_cols=['board'],
        top_n=top_n,
        agg_type='sum',
        agg_col='hrs',
        by_year=by_year).rename(columns = {'agg': 'total_hours'})
    # Top Boards by Barrels Made
    ranked_summary_dict['top_boards_by_barrels'] = top_n_by_agg_type(
        surf_data_df,
        grp_cols=['board'],
        top_n=top_n,
        agg_type='sum',
        agg_col='barrels_made',
        by_year=by_year).rename(columns = {'agg': 'total_barrel_count'})
    # Top 5 Sessions by session_value
    ranked_summary_dict['top_sessions_by_rank'] = top_n_by_agg_type(
        surf_data_df,
        grp_cols=['date', 'subregion', 'spot'],
        top_n=top_n,
        agg_type='mean',
        agg_col='session_value',
        by_year=by_year).rename(columns = {'agg': 'session_value'})

    return ranked_summary_dict