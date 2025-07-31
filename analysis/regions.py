import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.dates import DateFormatter
import seaborn as sns

from src.plot_setup import bg_color, region_color_dict, time_of_day_color_dict, main_palette
from src.utils import save_plt_dated

def process_region_hours(surf_data_df):

    # Group by year, month, and region, then sum the hours
    region_hours = (surf_data_df
                    .groupby(['year', 'month', 'region'])['hrs']
                    .sum()
                    .reset_index()
                    .sort_values(['year', 'month']))

    # for the code to work, we need a df with every combination of year, month, and region
    # that way, for every year/month, we know the hours in each region
    # Step 1.  Create a list of all combinations (years, month, and regions)
    all_combinations = []
    for year in region_hours['year'].unique():
        for month in region_hours['month'].unique():
            for region in region_hours['region'].unique():
                all_combinations.append([year, month, region])
    combinations_df = pd.DataFrame(all_combinations, columns=['year', 'month', 'region'])

    # sort by year and month
    combinations_df = combinations_df.sort_values(['year', 'month'])

    # Merge region_hours and combinations_df
    region_hours_full = pd.merge(combinations_df, region_hours, on=['year', 'month', 'region'], how='left')
    
    assert len(region_hours_full) == len(combinations_df), "Join of region hours to df with all combinations did not work correctly"
    
    # Fill NaN values in 'hrs' column with 0
    region_hours_full['hrs'] = region_hours_full['hrs'].fillna(0)

    # get a version of the month that is in string form
    region_hours_full['month_str'] = region_hours_full['month'].apply(lambda x: f'{int(x):02d}')

    # Add in the 'year-month' value - for x-axis unit
    region_hours_full['year_month'] = (region_hours_full['year'].astype(str) + '-' + region_hours_full['month_str'])

    # Also add in date column
    def create_date_column(df, year_col, month_col, new_col):
        df[new_col] = pd.to_datetime(df[year_col].astype(str) + '-' + df[month_col].astype(str) + '-01')
        return df
    region_hours_full = create_date_column(region_hours_full, 'year', 'month_str', 'date')

    # map the colors to the df
    region_hours_full['color'] = region_hours_full['region'].map(region_color_dict)

    # create and order for the plot
    region_hours_full['region'] = pd.Categorical(region_hours_full['region'], ['Southern CA', 'Central CA', 'Northern CA', 'Hawaii', 'Other'])

    return region_hours_full

def plot_regions_across_time(plot_df,
                            plot_folder=None):
    

    # find the total amount of hours per year/month and divide by 2 (we are going to use this value for both side of the line)
    symm_adjust = (plot_df.groupby('year_month')['hrs'].sum().values / 2)
    #get a list of the regions
    region_list = plot_df['region'].unique().tolist()

    # Plot Setup
    fig, ax = plt.subplots(1, figsize=(16,4), facecolor=bg_color)
    ax.set_facecolor(bg_color)

    # Do the plotting
    stack = 0
    for region in region_list:
        temp = plot_df[plot_df['region'] == region]
        stack = stack + temp['hrs'].values
        plt.fill_between(x = temp.date,
                        y1 = stack - temp['hrs'].values - symm_adjust,
                        y2 = stack - symm_adjust,
                        color = temp.color,
                        linewidth=0)

    # Legend
    legend_elements = [Patch(facecolor = region_color_dict[i], label = i)  for i in region_color_dict]
    legend = ax.legend(handles = legend_elements,
                    loc = 'lower center',
                    ncol = len(region_color_dict),
                    frameon = False,
                    bbox_to_anchor=(0.5, 1.05))
    plt.setp(legend.get_texts(), color='w')

    # Ticks
    date_format = DateFormatter("%Y")
    ax.xaxis.set_major_formatter(date_format)
    plt.tick_params(axis='x', colors='w', length=0)
    plt.yticks([])

    # remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    # grid
    ax.set_axisbelow(True)
    ax.xaxis.grid(color='lightgrey', linestyle='dashed', alpha=.5, lw=0.5)

    # Title
    plt.suptitle('Hours Spent Surfing in Each Region (Relative)', color='w', fontweight='bold', fontsize=18)

    plt.tight_layout()

    if plot_folder:
        filename = 'region_hours_across_time.png'
        save_plt_dated(plot_folder, filename)

def process_time_of_day(surf_data_df):
    time_of_day_df = surf_data_df.copy().dropna(subset=['when'])
    afternoon_index = time_of_day_df.index[time_of_day_df['when'] == 'afternoon'].tolist()
    time_of_day_df.loc[afternoon_index, 'when'] = 'midday'
    # create an order for the plot
    time_of_day_df['when'] = pd.Categorical(time_of_day_df['when'], (['morning','midday','evening','night'])[::-1])
    time_of_day_df['region'] = pd.Categorical(time_of_day_df['region'], (['Northern CA','Southern CA','Central CA','Other', 'Hawaii'])[::1])

    time_of_day_df['time_of_day_color'] = time_of_day_df['when'].map(time_of_day_color_dict)

    return(time_of_day_df)

def plot_time_of_day(time_of_day_df,
                            plot_folder=None):
    fig, ax = plt.subplots(1, figsize=(10,4), facecolor=bg_color)
    ax.set_facecolor(bg_color)

    sns.histplot(time_of_day_df,
                y='region',
                hue='when',
                hue_order=['morning','midday','evening','night'],
                stat='percent',
                multiple='fill',
                discrete=True,
                shrink=0.8,
                edgecolor=None,
                palette=main_palette[::1], # [::-1] for reverse order
                alpha=1,
                ax=ax)
    plt.gca().invert_xaxis()
    sns.despine()
    sns.move_legend(ax, bbox_to_anchor=(1.01, 1.02), loc='upper left')
    for p in ax.patches:
        h, w, x, y = p.get_height(), p.get_width(), p.get_x(), p.get_y()
        if w > 0.01:
            text = f'{w * 100:0.0f}%'
            ax.annotate(text=text, xy=(x + w / 2, y + h / 2),
                        ha='center',
                        va='center',
                        color=bg_color, #'white',
                        size=14)

    # fix ticks and axis labels
    ax.xaxis.label.set_visible(False)
    ax.yaxis.label.set_visible(False)
    plt.xticks([])
    plt.tick_params(axis='both', which='both', colors='w', length=0)

    # Legend (top middle)
    legend_elements = [Patch(facecolor = time_of_day_color_dict[i], label = i)  for i in time_of_day_color_dict]
    legend = ax.legend(handles = legend_elements,
                    loc = 'lower center',
                    #  loc = 'upper left',
                    ncol = len(time_of_day_color_dict),
                    frameon = False,
                    bbox_to_anchor=(0.5, 1))
    plt.setp(legend.get_texts(), color='w')

    # remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    # grid
    ax.set_axisbelow(True)
    ax.xaxis.grid(color='lightgrey', linestyle='dashed', alpha=.5, lw=0.5)

    # Title
    plt.suptitle('Session Time of Day per Region', color='w', fontweight='bold', fontsize=18)

    plt.tight_layout()

    if plot_folder:
        filename = 'time_of_day_by_region.png'
        save_plt_dated(plot_folder, filename)
