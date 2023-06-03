import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from kneed import KneeLocator
from tqdm.notebook import tqdm  # Show loop progress

def determine_max_num_try_cluster(coordinate_array):
    # Ask the user to give a number to be the max of times of clustering to
    # try

    num_row_in_coordinate_array = coordinate_array.shape[
        0]  # This is the max you can use for the clustering

    while True:
        user_input = input("Please enter an int for the max number of cluster "
                           "you want to try that is <= {}: "
                           .format(num_row_in_coordinate_array))
        try:
            user_input = int(user_input)
            if user_input < 0 or user_input > num_row_in_coordinate_array:
                print("Input must be between 0 and {}.".format
                      (num_row_in_coordinate_array))
            else:
                break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    max_num_try_cluster = user_input
    return max_num_try_cluster


def calculate_inertia(coordinate_array, max_num_try_cluster):
    # Calculate inertia for each k value
    # max_num_try_cluster is the max number to try to do the clustering
    # wcss is a list of inertia

    wcss = []
    for k in tqdm(range(1, max_num_try_cluster + 1)):
        kmeans = KMeans(
            n_clusters=k,
            init='k-means++',
            max_iter=300,
            n_init=30,
            # By defualt, this is 10, the larger the more likely to get
            # the global minimum of WCSS, but the computation time is also longer
            random_state=0
        )
        kmeans.fit(coordinate_array)
        wcss.append(kmeans.inertia_)

    return wcss


def generate_x_axis(max_num_try_cluster):
    x_axis = range(1, max_num_try_cluster + 1)  # Update x-axis to match length
    # of wcss
    return x_axis


def calculate_optimal_cluster_num(x_axis, wcss):
    kn = KneeLocator(  # Calculate out the optimal number of clusters
        x_axis,
        wcss,
        curve='convex',
        direction='decreasing',
        interp_method='interp1d',
    )

    optimal_cluster_num = kn.knee
    return optimal_cluster_num


def make_elbow_plot(coordinate_array, max_num_try_cluster):
    # Generate the elbow plot

    x_axis = generate_x_axis(max_num_try_cluster)
    wcss = calculate_inertia(coordinate_array, max_num_try_cluster)
    optimal_cluster_num = calculate_optimal_cluster_num(x_axis, wcss)

    # Plot the elbow curve
    plt.plot(x_axis, wcss, 'o-')
    plt.xticks(x_axis)  # Force to show all the ticks on x-axis

    plt.vlines(  # Plot out the optimal number of cluster
        optimal_cluster_num,
        ymin=plt.ylim()[0],
        ymax=plt.ylim()[1],
        linestyles='dashed',
        colors='g'
    )

    plt.title('Elbow Method to determine optimal number of clusters')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Inertia')
    plt.figtext(
        0,
        0,
        'The optimal number of clusters is {}'.format(optimal_cluster_num),
        ha='left',
        fontsize=10,
        color='green'
    )

    plt.show()
    return optimal_cluster_num
