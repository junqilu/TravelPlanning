# TravelPlanning
This contains several tools to help on travel planning 

# General protocol
1. Get all geo-coordinates data from Google map
   * Follow this tutorial: https://www.knowyourmobile.
     com/user-guides/how-to-download-and-export-your-starred-google-maps-locations/ 
2. Use the name of the location to filter out all the sites in the city 
   that you'll visit
3. Clustering of all non-restaurant sites and overlap with restaurants
    * All restaurants don't participate in the clustering
4. Draw out the sites and the clusters on a folium map (like a combination 
   of plt scatter plot for clustering and plotly plot for pop out labels)
    * Only a cluster with 3 or more sites will have the cluster drawn on 
      the map

## Notices
Plotly maps don't have any speciality now since Folium maps are better for 
this purpose. 

# Travel places planned 
* NC
  * Chapel Hill 
    * The data read in for this one is a bit special since this was the 
      first place to plan. Later places all used the data from Google Map 
      export rather than manual inputs for higher efficiency. 
  * Wilmington
    * Major locations shot in the film Blue Velvet: https://wilmtv.com/production/blue-velvet-1986