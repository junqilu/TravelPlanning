import folium
import folium.plugins as plugins
import numpy as np
from matplotlib import pyplot as plt

from convex_hull_interpolation_toolkit import generate_convex_hull, \
    generate_interpolation
from plt_map_toolkit import create_four_point_diamond_around


def initialize_folium_map(df_no_restaurant, num_cluster):
    latitude_avg = df_no_restaurant['Latitude'].mean()
    longitude_avg = df_no_restaurant['Longitude'].mean()

    my_map = folium.Map(
        location=[latitude_avg, longitude_avg],
        zoom_start=12,
        control_scale=True,
        tiles=None
    )

    # Add in several options for the map You can find a list of free tile
    # providers here: http://leaflet-extras.github.io/leaflet-providers/preview/
    map_style_list = [
        'OpenStreetMap',  # Colorful and has lots of details
        'CartoDB Positron',  # Lightly colored with some details
        # 'Stamen Toner', #Very simplified black-and-white map
    ]
    for map_style in map_style_list:  # Add in all the map styles you like
        folium.TileLayer(map_style).add_to(my_map)

    # You have to create all the feature groups you need later here
    restaurant_group = folium.FeatureGroup(name='Restaurants')  # For all the
    # restaurants
    site_group = folium.FeatureGroup(
        name='Sites')  # For all the non-restaurants
    cluster_group = folium.FeatureGroup(
        name='Clusters: {}'.format(num_cluster)
        # This reminds the user how many
        # clusters in total
    )  # For all the clustering polygons of the non-restaurants

    # Add in all the feature groups that you just created
    restaurant_group.add_to(my_map)
    site_group.add_to(my_map)
    cluster_group.add_to(my_map)

    folium.LayerControl(
        # LayerControl line must be after the FeatureGroup lines
        # . Otherwise, you'll lose the LayerControl as a whole
        collapsed=False
    ).add_to(my_map)  # Give user the option to
    # choose which style to use

    # Add in plugins. This section should be put in the same block as the map
    # initiation since running these twice will add duplicates
    plugins.Geocoder(
        collapsed=True,  # Minimize the search bar unless you click on it
        position='topleft',
        add_marker=True  # If True, adds a marker on the found location.
    ).add_to(my_map)  # Add in a search bar

    plugins.MiniMap(
        position='bottomright',
        toggle_display=True
        # Sets whether the minimap should have a button to minimise it
    ).add_to(my_map)  # Add minimap to map

    plugins.Fullscreen(
        position='bottomright',
        title="Expand map",
        title_cancel="Exit expand mode",
        force_separate_button=True  # Force separate button to detach from zoom
        # buttons
    ).add_to(my_map)  # Add full screen button
    # to map

    plugins.LocateControl().add_to(
        my_map)  # This plugins adds a button to the map, and when it’s
    # clicked shows the current user device location.

    plugins.MeasureControl(
        position='bottomleft'
    ).add_to(my_map)  # Add a measurement widget on the map.

    plugins.Draw(
        export=True,  # Add a small button that exports the drawn shapes as a
        # geojson file
        position='topleft'
    ).add_to(my_map)  # Add draw tools to map

    return my_map, restaurant_group, site_group, cluster_group


def add_in_location_markers(open_df, my_map, restaurant_group, site_group):
    for index, row in open_df.iterrows():
        latitude = row['Latitude']
        longitude = row['Longitude']
        category = row['Category']

        google_category = row['Extracted Category']
        google_url = row['Google Maps URL']

        place_name = row['Business Name']
        if str(place_name) == 'nan':
            place_name = 'No business name'

        # You have to recreate the icon_style since folium doesn't allow
        # reusing icon_style
        if category == 'Restaurant':
            feature_group = restaurant_group

            icon_style = plugins.BeautifyIcon(
                icon='utensils',
                # Name for icons can be found at https://fontawesome.com/search
                icon_shape='circle',
                border_color='orange',
                # Use orange here since yellow is too light
                text_color='orange'  # This controls the icon image color
            )
        else:
            feature_group = site_group

            if category == 'Garden':
                icon_style = plugins.BeautifyIcon(
                    icon='leaf',
                    icon_shape='circle',
                    border_color='green',
                    text_color='green'
                )
            elif category == 'Museum':
                icon_style = plugins.BeautifyIcon(
                    icon='university',
                    icon_shape='circle',
                    border_color='red',
                    text_color='red'
                )
            elif category == 'Site':
                icon_style = plugins.BeautifyIcon(
                    icon='camera',
                    icon_shape='circle',
                    border_color='blue',
                    text_color='blue'
                )
            elif category == 'Store':
                icon_style = plugins.BeautifyIcon(
                    icon='store',
                    icon_shape='circle',
                    border_color='purple',
                    text_color='purple'
                )
            else:
                print('Run into an unknown category {}!'.format(category))

        html_content = """
        <!DOCTYPE html>
        <html>
          <head>
            <style type="text/css" media="screen">
                table, th, td {{
                    border: 1px solid black;
                    border-collapse: collapse;
                    text-align: center;
                }}
            </style>
          </head>
          <body>
            <h4>{}</h4>
            <div>
              <table>
                <tbody>
                  <tr>
                    <th>Sub-category</td>
                    <td>{}</td>
                  </tr>
                  <tr>
                    <th>URL</td>
                    <td><a href="{}">{}</a></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </body>
        </html>
        """.format(place_name, google_category, google_url, google_url)

        popup_iframe = folium.IFrame(
            html_content,
            width='auto',
            height='auto'
        )
        popup_obj = folium.Popup(
            popup_iframe,
            min_width=300,
            max_width=500
        )

        folium.Marker(
            location=[latitude, longitude],
            popup=popup_obj,
            icon=icon_style,
            opacity=1
        ).add_to(feature_group)

    # Create a legend using BeautifyIcon and Icon classes
    legend_html = '''
         <div style="position: fixed;
                     top: 180px; right: 10px; width: auto; height: auto;
                     border: 2px solid grey; z-index:9999;
                     font-size:12px;
                     background-color: white;
                     opacity: 1;
                     border-radius: 5px; /* Rounded corners */
                     padding: 10px; /* Add some padding for spacing */
                     ">
             <p style="margin: 0; text-align:center; border-bottom: 1px solid
             grey; padding-bottom: 5px;"><b>Legend</b></p>
             <p style="margin: 5px; color: orange; text-align:center;
             "><b>Restaurants</b></p>
             <p style="margin: 5px; color: blue; text-align:center;
             "><b>Sites</b></p>
             <p style="margin: 5px; color: green; text-align:center;
             "><b>Gardens</b></p>
             <p style="margin: 5px; color: red; text-align:center;
             "><b>Museums</b></p>
             <p style="margin: 5px; color: purple; text-align:center;
             "><b>Stores</b></p>
         </div>
    '''

    my_map.get_root().html.add_child(folium.Element(legend_html))
    return my_map


def generate_color_list(df_no_restaurant):
    fig, ax = plt.subplots(figsize=(10, 8))

    scatter_non_restaurant = ax.scatter(  # Draw cluster plot for all the
        # non-restaurants
        df_no_restaurant['Longitude'],
        df_no_restaurant['Latitude'],
        c=df_no_restaurant['Cluster'],
        alpha=1,
        s=100,
        edgecolor='black',
    )

    # The 2 lines below output the colors used in the scatter plot so the later
    # convex hull interpolation can use the same color as the points
    labels = df_no_restaurant[
        'Cluster'].unique()  # Get the unique cluster labels
    color_list = scatter_non_restaurant.cmap(
        scatter_non_restaurant.norm(
            labels))  # Get the colors used for each label

    plt.close() #This forbids to really plot out the scatter plot since I
    # don't need that--all I need is the color_list. Without this line,
    # you'll have a plt plot alongside the folium map
    return color_list

def plot_polygon_shades_for_clusters(my_map, df_no_restaurant, cluster_group):
    color_list = generate_color_list(df_no_restaurant)


    for cluster_idx in df_no_restaurant.Cluster.unique():  # Add in the convex
        # hull and interpolate

        # You won't have a cluster that contains 0 location Technically,
        # you can only make convex hull and the later interpolation with at
        # least 3 points. So for clusters that contain only 1 or 2
        # locations, you need to do something to increase the
        # pseudo-location number to make the shade

        cluster_df = df_no_restaurant[df_no_restaurant.Cluster == cluster_idx]
        location_count_in_cluster = cluster_df.shape[0]

        points = cluster_df[['Longitude', 'Latitude']].values  # Obtain the
        # true location's longitude and latitude. Remember, points is a
        # numpy.ndarray not a df
        delta = 0.02  # Amount to add or subtract. I have adjusted this
        # based on the Wilmington travel planning

        if location_count_in_cluster == 1:# When a cluster has only 1
            # location, add 4 pseudo-locations to make a diamond shade
            # around the 1 true location. The side of the diamond will be
            # controlled by the delta variable

            new_rows = create_four_point_diamond_around(points, delta)
            # Create 4 pseudo points around the 1 true location

            points = np.vstack((points, new_rows))  # Add the 4
            # pseudo-locations to be with the 1 true location

        elif location_count_in_cluster == 2:  # When a cluster has only 2
            # locations, you still cannot use the midpoint of the 2
            # locations as the hull will be flat and the algorithum will
            # complain about it. My method is to calculate out the midpoint
            # and add in 4 pseudo-locations to create a diamond shape around
            # that midpoint. Those 4 pseudo-locations will be added into the
            # point ndarray to make the hull. I used a diamond here to avoid
            # have only 2 pseudo-locations that perfectly align with the 2
            # true locations, resulting in a flat hull again.
            mid_point = points.mean(axis=0)
            reshaped_mid_point = np.reshape(mid_point, (1, 2))

            new_rows = create_four_point_diamond_around(reshaped_mid_point,
                                                        delta)

            points = np.vstack(
                (points, new_rows))  # Add the 4 pseudo-locations to be with
            # the 2 true locations

        else:  # location_count_in_cluster >= 3:
            # Then you can simply use the points obtained before without any
            # processing

            pass

        x_hull, y_hull = generate_convex_hull(
            points)  # Generate the convex
        # hull

        interp_x, interp_y = generate_interpolation(x_hull, y_hull)
        # Generate the interpolation

        # plot the polygon shades
        interp_coordinates = []

        for x, y in zip(interp_x, interp_y):
            interp_coordinates.append([y, x])

        polygon = folium.Polygon(
            locations=interp_coordinates,
            color='rgba({})'.format(','.join(str(255 * num) for num in
                                             color_list[cluster_idx])),
            # The
            # color is passed in as the rgba values. The original numbers in
            # color_list[cluster_idx] need to be timed 255 to get the
            # representing rgba values
            # dash_array='10,5', #Make the outline to be dashed if you want
            fill=True,
            # fill_color='blue', #If you don't specify the fill_color, then
            # it'll follow on the color argument. You can use a different
            # color for filling though by the fill_color argument
            fill_opacity=0.3
        )
        polygon.add_to(cluster_group)

    return my_map


def generate_folium_map(open_df, df_no_restaurant, num_cluster):
    my_map, restaurant_group, site_group, cluster_group = \
        initialize_folium_map(df_no_restaurant, num_cluster)

    my_map = add_in_location_markers(open_df, my_map, restaurant_group, site_group)

    my_map = plot_polygon_shades_for_clusters(my_map, df_no_restaurant, cluster_group)

    return my_map
