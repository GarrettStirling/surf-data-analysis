# Plot Setup
bg_color = '#2C2C2C'
main_palette = ['#89D99D', '#3B8C6E', '#10ABB4', '#1E5959']


# dict used to add in a color column, based on region
region_color_dict = {'Southern CA': '#89D99D',
                     'Central CA': '#3B8C6E',
                     'Northern CA': '#1E5959',
                     'Hawaii': '#10ABB4',
                     'Other': '#D9D9D9'}

# build dictionary to assign colors based on the the board state.
# note, this order matters for the order of the legend!!
board_state_color_dict = {'have':'#5db054', # green
                          'gave away':'#e5ed87', # yellow
                          'sold':'#f59e42', # 
                          'broken':'#b05454'}

# apply color for `when`
time_of_day_color_dict = {'morning': '#89D99D',
                    'midday':  '#3B8C6E',
                    'evening': '#10ABB4',
                    'night':   '#1E5959'}
