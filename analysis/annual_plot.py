import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from src.plot_setup import bg_color, main_palette, season_color_dict
from src.utils import save_plt_dated

def plot_annual_stats(summary_df,
                      plot_folder=None):
    
    if 'year_month' in summary_df.columns:
        # Convert year_month to datetime for proper sorting and display
        summary_df['year_month'] = pd.to_datetime(summary_df['year_month'], format='%Y-%m')
        summary_df = summary_df.sort_values('year_month')
        
        # Generate title and filename
        plot_title = 'Surf Stats by Year and Month'
        filename = 'surf_stats_bar_charts_by_month_year.png'
    else:
        # Ensure year is in a suitable format for plotting
        summary_df['year'] = pd.to_numeric(summary_df['year'], errors='coerce')
        summary_df = summary_df.dropna(subset=['year'])
        summary_df = summary_df.sort_values('year')
        
        # Generate title and filename
        plot_title = 'Surf Stats by Year'
        filename = 'surf_stats_bar_charts_by_year.png'

    # Create the figure with 4 subplots stacked vertically
    fig, axes = plt.subplots(4, 1, figsize=(16, 14), sharex=True)
    fig.patch.set_facecolor(bg_color)
    
    # Define metrics for each subplot
    metrics = [
        ('total_hours', 'Total Hours', 'Hours'),
        ('total_sessions', 'Total Sessions', 'Sessions'),
        ('total_unique_spots', 'Total Unique Spots Surfed', 'Spots'),
        ('total_barrels_made', 'Amount of Barrels Made', 'Barrels')
    ]
    
    # Create bars for each subplot
    for i, (metric, title, ylabel) in enumerate(metrics):
        ax = axes[i]
        
        # Add faint colored grid lines FIRST (behind bars)
        ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='white')
        ax.set_axisbelow(True)  # Ensure grid is behind bars
        
        # Create bars with specified width and no stroke
        if 'year_month' in summary_df.columns:
            bars = ax.bar(summary_df['year_month'],
                          summary_df[metric],
                          color=main_palette[i],
                          width=20)
        else:
            bars = ax.bar(summary_df['year'],
                          summary_df[metric],
                          color=main_palette[i],
                          width=0.8)
        
        # Customize each subplot with left-aligned title
        ax.set_title(title, fontsize=16, fontweight='bold', color='white', pad=15, loc='left')
        ax.set_ylabel(ylabel, fontsize=16, color='white')
        ax.set_facecolor(bg_color)
        
        # Remove spines (bounding box) except bottom (white line for all subplots)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        # Make bottom spine white for all subplots
        ax.spines['bottom'].set_color('white')
        ax.spines['bottom'].set_linewidth(1)
        
        # Customize tick colors and remove tick marks
        ax.tick_params(colors='white', labelsize=10, length=0)
    
    # Remove tick marks and adjust x-axis labels for better readability
    axes[-1].tick_params(length=0)
    
    # Format x-axis based on data type with bold labels, size 14, and padding
    if 'year_month' in summary_df.columns:
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        axes[-1].xaxis.set_major_locator(mdates.YearLocator())
        labels = axes[-1].get_xticklabels()
        [label.set_fontweight('bold') for label in labels]
        
    else:
        axes[-1].set_xticks(summary_df['year'])
        axes[-1].set_xticklabels(summary_df['year'].astype(int), fontweight='bold')
    
    axes[-1].tick_params(axis='x', labelsize=14, pad=10)

    # Adjust layout to prevent overlap
    plt.tight_layout()
    
    # Add a main title with more space above top subplot
    fig.suptitle(plot_title, fontsize=18, fontweight='bold', color='white', y=0.975)
    
    # Adjust the top margin to accommodate the main title with more space
    plt.subplots_adjust(top=0.92, bottom=0.12, hspace=0.3)
    
    # Save
    if plot_folder:
        save_plt_dated(plot_folder, filename)
        print(f"Plot saved as {filename} in {plot_folder}")



def plot_seasonal_stats(summary_df, plot_folder=None, season_palette=season_color_dict):
    """
    Plots annual surf summaries, coloring bars by season.

    Args:
        summary_df (pd.DataFrame): Must contain columns 'year_month', 'season', and all relevant metrics.
        plot_folder (str): Folder path for saving the plot.
        season_palette (dict): Mapping from season name to color, e.g. {'Winter': '#1f77b4', ...}
    """
    # Ensure required columns are present
    required_cols = ['year_month', 'season',
                     'total_hours', 'total_sessions', 'total_unique_spots', 'total_barrels_made']
    missing = [col for col in required_cols if col not in summary_df.columns]
    if missing:
        raise ValueError(f"Missing required columns in DataFrame: {missing}")

    # Convert year_month to datetime for proper sorting and plotting
    summary_df['year_month'] = pd.to_datetime(summary_df['year_month'], format='%Y-%m')
    summary_df = summary_df.sort_values('year_month')

    # Generate title and filename
    plot_title = 'Surf Stats by Month and Season'
    filename = 'surf_stats_bar_charts_by_month_season.png'

    # Map color for each row
    bar_colors = summary_df['season'].map(season_palette).fillna('#CCCCCC')

    # Create the figure with 4 subplots stacked vertically
    fig, axes = plt.subplots(4, 1, figsize=(16, 14), sharex=True)
    fig.patch.set_facecolor(bg_color)

    # Define metrics for each subplot
    metrics = [
        ('total_hours', 'Total Hours', 'Hours'),
        ('total_sessions', 'Total Sessions', 'Sessions'),
        ('total_unique_spots', 'Total Unique Spots Surfed', 'Spots'),
        ('total_barrels_made', 'Amount of Barrels Made', 'Barrels')
    ]

    # Create bars for each subplot
    for i, (metric, title, ylabel) in enumerate(metrics):
        ax = axes[i]

        # Add faint colored grid lines FIRST (behind bars)
        ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='white')
        ax.set_axisbelow(True)

        # Create bars colored by season
        bars = ax.bar(summary_df['year_month'],
                      summary_df[metric],
                      color=bar_colors,
                      width=20)

        # Customize subplot
        ax.set_title(title, fontsize=16, fontweight='bold', color='white', pad=15, loc='left')
        ax.set_ylabel(ylabel, fontsize=16, color='white')
        ax.set_facecolor(bg_color)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('white')
        ax.spines['bottom'].set_linewidth(1)
        ax.tick_params(colors='white', labelsize=10, length=0)

    # Remove tick marks and adjust x-axis labels for better readability
    axes[-1].tick_params(length=0)

    # Format x-axis as years
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    axes[-1].xaxis.set_major_locator(mdates.YearLocator())
    labels = axes[-1].get_xticklabels()
    [label.set_fontweight('bold') for label in labels]
    axes[-1].tick_params(axis='x', labelsize=14, pad=10)

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Add a main title with more space above top subplot
    fig.suptitle(plot_title, fontsize=18, fontweight='bold', color='white', y=0.975)
    plt.subplots_adjust(top=0.92, bottom=0.12, hspace=0.3)

    # Save
    if plot_folder:
        save_plt_dated(plot_folder, filename)
        print(f"Plot saved as {filename} in {plot_folder}")
