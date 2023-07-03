import matplotlib.pyplot as plt
import numpy as np

from convex_hull_interpolation_toolkit import generate_convex_hull, \
    generate_interpolation

# Define the marker style and color for each category. These 2 dict will
# only be used for making the plt scatter map
marker_dict = {
    'Restaurant': '*',
    'Site': 'o',
    'Garden': 'o',
    'Museum': 'o',
    'Store': 'o'
}

color_dict = {
    'Restaurant': 'yellow',
    'Site': 'blue',
    'Garden': 'green',
    'Museum': 'red',
    'Store': 'purple'
}


def plt_scatter_map(travel_city_name, open_df):
    # Simply plot a scatter plot of locations of different categories

    fig, ax = plt.subplots(figsize=(10, 8))  # Create the scatter plot

    # Plot each category separately with a different marker style and color
    for category in open_df['Category'].unique():
        mask = open_df['Category'] == category
        if category == 'Restaurant':
            ax.scatter(
                open_df['Longitude'][mask],
                open_df['Latitude'][mask],
                marker=marker_dict[category],
                color=color_dict[category],
                s=200,
                label=category,
                edgecolor='black',
                alpha=0.5
            )
        else:
            ax.scatter(
                open_df['Longitude'][mask],
                open_df['Latitude'][mask],
                marker=marker_dict[category],
                color=color_dict[category],
                s=100,
                label=category,
                edgecolor='black',
                alpha=0.5
            )

    # Set the chart title and axis labels
    ax.set_title('{} places to visit'.format(travel_city_name))
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # Add a legend to the plot
    legend_dict = {}
    handles, labels = ax.get_legend_handles_labels()
    for handle, label in zip(handles, labels):
        legend_dict[label] = handle
    new_labels = ['Restaurant', 'Site', 'Garden', 'Store', 'Museum']  # This is
    # the order of legend I specified
    new_handles = [legend_dict[label] for label in new_labels]
    ax.legend(new_handles, new_labels, loc='center left',
              bbox_to_anchor=(1.0, 0.5))

    # Show the plot
    plt.show()


def create_four_point_diamond_around(points, delta):
    # points is a numpy.ndarray that contains only 1 true location's
    # longitude and latitude. This function will create 4 more
    # pseudo-locations and add them back to the points numpy.ndarray

    new_rows = np.array([
        [points[0, 0] + delta, points[0, 1]],
        # Plus delta to the first number
        [points[0, 0] - delta, points[0, 1]],
        # Minus delta from the first number
        [points[0, 0], points[0, 1] + delta],
        # Plus delta to the second number
        [points[0, 0], points[0, 1] - delta],
        # Minus delta from the second number
    ])  # Create a numpy.ndarray for the 4 pseudo-locations

    return new_rows


def plt_cluster_map(travel_city_name, df_no_restaurant, df_restaurant):
    # Plot the clustered data points with the new marker and color dictionaries

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
        delta = 0.01  # Amount to add or subtract. I have adjusted this
        # based on the Wilmington travel planning

        if location_count_in_cluster == 1:  # When a cluster has only 1
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

        x_hull, y_hull = generate_convex_hull(points)  # Generate the convex
        # hull

        interp_x, interp_y = generate_interpolation(x_hull, y_hull)
        # Generate the interpolation

        # plot the polygon shades
        ax.fill(
            interp_x,
            interp_y,
            '--',
            c=color_list[cluster_idx],
            alpha=0.3
        )

    scatter_restaurant = ax.scatter(
        # Label out all the restaurants. Put it here
        # so the restaurants aren't covered by the interpolation
        df_restaurant['Longitude'],
        df_restaurant['Latitude'],
        marker='*',
        c='yellow',
        alpha=0.8,
        s=150,
        edgecolor='black',
    )

    ax.set_title('{} places to visit (excluding Restaurants)'.format(travel_city_name))
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    plt.figtext(
        0,
        0,
        'Only cluster with 3 points have a convex hull '
        'interpolation\nNon-stars are non-restaurant sites\nYellow '
        'starts are restaurants',
        ha='left',
        fontsize=10,
        color='red'
    )

    plt.show()
