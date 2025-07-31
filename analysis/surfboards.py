import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
import numpy as np

from src.plot_setup import bg_color, region_color_dict, board_state_color_dict
from src.utils import to_snake_case, save_plt_dated

def process_surfboard_hrs(surf_data_df, surf_data_dict):
    # filter to surfboards that exist in the board column of surf_data_dict['Surfboards']
    surfboard_analysis = surf_data_df[surf_data_df['board'].isin(surf_data_dict['Surfboards']['board'])]
    # now summarise so that for each board and region, we know the total hours
    surf_data_board_hrs_region = surfboard_analysis.groupby(['board', 'region'])['hrs'].sum().reset_index().sort_values('hrs', ascending=False)
    # convert from data long to data wide
    surf_data_board_hrs_region_wide = surf_data_board_hrs_region.pivot_table(index='board', columns='region', values='hrs', fill_value=0).reset_index()
    # Calculate total hours per board and sort
    surf_data_board_hrs_region_wide['total_hrs'] = surf_data_board_hrs_region_wide.drop(columns=['board']).sum(axis=1)
    surf_data_board_hrs_region_wide = surf_data_board_hrs_region_wide.sort_values(by='total_hrs', ascending=True)

    return surf_data_board_hrs_region_wide



def plot_surfboard_hrs(surfboard_hrs_df,
                       plot_folder=None):
    """ Plot the amount of hours spent on each surfboard by region."""

    # Create the figure and axis
    fig, ax = plt.subplots(1, figsize=(16,16), facecolor=bg_color)
    ax.set_facecolor(bg_color)

    # Plot stacked horizontal bars
    bottom = None
    for region in region_color_dict.keys():
        values = surfboard_hrs_df[region]
        ax.barh(surfboard_hrs_df['board'], values, left=bottom, color=region_color_dict[region], label=region)
        if bottom is None:
            bottom = values
        else:
            bottom = bottom + values

    # Grid lines
    ax.set_axisbelow(True)
    ax.xaxis.grid(color = 'k',
                linestyle = 'dashed',
                alpha = 0.4,
                which = 'both')

    # Customize the plot
    ax.set_xlabel('Hours Spent on Surfboard', color='w', fontweight='bold', fontsize=16, labelpad=25)
    ax.set_ylabel('Surfboards', color='w', fontweight='bold', fontsize=16)
    plt.suptitle('Amount of Hours Spent on Each Surfboard by Region', color='w', fontweight='bold', fontsize=18)

    # Legend
    legend_elements = [Patch(facecolor = region_color_dict[i], label = i)  for i in region_color_dict]
    legend = ax.legend(handles = legend_elements,
                    loc = 'lower center',
                    ncol = len(region_color_dict),
                    frameon = False,
                    bbox_to_anchor=(0.45, 0.975))
    plt.setp(legend.get_texts(), color='w')

    # ax.tick_params(axis='x', labelsize=14, colors='w', length=0)  # Adjust labelsize as needed
    plt.tick_params(colors='w', length=0, labelsize=12)

    # remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_color('w')

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Show the plot
    # plt.show()
    if plot_folder:
        filename = 'surfboard_hours_by_region.png'
        save_plt_dated(plot_folder, filename)



def process_surfboard_lifetime(surf_data_df, surf_data_dict):
    # Step 1: Find the min and max date for each board
    #         also remove boards that were only surfed once (i.e. start to end date are the same)
    board_timeline_df_all = (surf_data_df
                    .groupby(['board'])
                    .agg(min_date = ('date', 'min'),
                        max_date = ('date', 'max'))
                    .sort_values('min_date', ascending=False)
                    .query("min_date != max_date"))

    # Step 2; inner join the boards in the surfboard sheet to the board/min/max df
    surf_data_dict['Surfboards'].columns = [to_snake_case(col) for col in surf_data_dict['Surfboards'].columns]

    # only grab the boards that are defined in the surfboards list
    board_timeline_df = pd.merge(board_timeline_df_all, surf_data_dict['Surfboards'][['board', 'gone']], on='board', how='inner')

    # Grab the first date
    first_date = board_timeline_df.min_date.min()
    # number of days from project start to task start
    board_timeline_df['start_num'] = (board_timeline_df.min_date-first_date).dt.days
    # number of days from project start to end of tasks
    board_timeline_df['end_num'] = (board_timeline_df.max_date-first_date).dt.days
    # days between start and end of each task
    board_timeline_df['days_start_to_end'] = board_timeline_df.end_num - board_timeline_df.start_num

    # map the colors to the df
    board_timeline_df['color'] = board_timeline_df['gone'].map(board_state_color_dict)

    return board_timeline_df

def plot_surfboard_lifetime(board_timeline_df, 
                            plot_folder=None):
    """ Plot a gantt chart with the first and last time using each surfboard."""
    # From two sources:
    # https://medium.com/towards-data-science/gantt-charts-with-pythons-matplotlib-395b7af72d72
    # https://gist.github.com/Thiagobc23/fc12c3c69fbb90ac64b594f2c3641fcf

    # Setup
    fig, ax = plt.subplots(1, figsize=(16, 10), facecolor=bg_color)
    ax.set_facecolor(bg_color)

    # Bars
    ax.barh(y = board_timeline_df.board,
            width = board_timeline_df.days_start_to_end,
            left = board_timeline_df.start_num,
            color = board_timeline_df.color)

    # Adding the board as text next to each bar
    for idx, row in board_timeline_df.iterrows():
        ax.text(x = row.start_num - 10,
                y = idx,
                s = row.board,
                va = 'center',
                ha = 'right',
                alpha = 1,
                color = 'w')

    # Grid lines
    ax.set_axisbelow(True)
    ax.xaxis.grid(color = 'k',
                linestyle = 'dashed',
                alpha = 0.4,
                which = 'both')

    # Legend
    legend_elements = [Patch(facecolor = board_state_color_dict[i], label = i)  for i in board_state_color_dict]
    legend = ax.legend(handles = legend_elements,
                    #  loc = 'lower left',
                    loc = 'lower center',
                    ncol = len(board_state_color_dict),
                    bbox_to_anchor=(0.5, 1),
                    frameon = False)
    plt.setp(legend.get_texts(), color='w')

    # Ticks (confusing)
    # for each day in our range, assing it to a year and save it as an array, then convert to integer
    year_per_day_range = pd.date_range(board_timeline_df.min_date.min(), end=board_timeline_df.max_date.max()).strftime("%Y")
    year_per_day_range = np.array(year_per_day_range, dtype=int)
    # now, find the indexes for the change of each year
    years_start_index = np.where(np.diff(year_per_day_range) != 0)[0] + 1
    years_start_index = np.insert(years_start_index, 0, 0)
    # now apply the ticks as the indexes that indicate the start of each year
    ax.set_xticks(years_start_index)
    ax.set_xticklabels(np.unique(year_per_day_range), color='w', fontsize =14)
    ax.set_yticks([]) # no y-ticks
    plt.setp([ax.get_xticklines()], color='w')
    plt.tick_params(axis='x', length=0)

    # align x axis
    ax.set_xlim(0, board_timeline_df.end_num.max())

    # remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_color('w')

    # Title
    plt.suptitle('Surfboard Lifetime', color='w', fontweight='bold', fontsize=18)
    fig.text(0.5, 0.95, 'Each bar represents the first and last time using each surfboard', transform=fig.transFigure, ha='center', va='top', fontsize=10, fontweight='light', color='w')

    if plot_folder:
        filename = 'surfboard_timeline_df.png'
        save_plt_dated(plot_folder, filename)