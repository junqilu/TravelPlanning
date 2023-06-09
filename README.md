# TravelPlanning
This contains several tools to help on travel planning 

# General protocol
1. Get all geo-coordinates data from Google map json
    * Follow this tutorial: https://www.knowyourmobile.
      com/user-guides/how-to-download-and-export-your-starred-google-maps-locations/
        * Following the tutorial, you'll have a .json. Put that file in the
          inputs folder
        * That .json file is privacy-sensitive, so don't share that with
          others. The whole inputs folder is not tracked for an extra
          protection
        * The data structure of that .json:
          file:///C:
          /Users/louie/Desktop/download/takeout-20230524T051600Z-001/Takeout/archive_browser.html
1. Convert the json into a pandas dataframe
1. Use the Address of the location to filter out all the locations in the
   cities that you'll visit
    * I used a list of allowed cities here rather than 1 single city
      because how you see as a "city" on the map is different from how
      Google defines as a "city," which is strict.
    * For example, the Holiday Inn Resort Lumina is in" Wilmington, but it's
      actually in Wrightsville Beach; if you only use "Wilmington" for
      filtering, this hotel would be filtered out
1. Use the Google map url to scrape the categories of locations
    * I have to scrape because the Google map json doesn't contain this info
1. Label the location's category using the category info from
   Google map
    * This is because the Google map category is very detailed. For example,
      I like to regard a "Grill" place as a "Restaurant".
    * This is done by matching the category from Google map to a 
      pre-defined dictionary, which is more reliable than a NLP 
      text-classification. 
1. Clustering of all non-restaurant sites and overlap with restaurants
    * All restaurants don't participate in the clustering
    * Although using the real distance (considering roads) rather than the 
      straight distance will be more accurate for clustering, doing so 
      is very complicated. Considering I'm not using a map API, this is 
      temporally out of the scope of the project. 
1. Draw out the locations and the clusters on a folium map (like a
   combination of plt scatter plot for clustering and plotly plot for pop out
   labels)
    * Only a cluster with 3 or more sites will have the cluster drawn on
      the map

## Notices
Plotly maps don't have any speciality now since Folium maps are better for 
this purpose, but I still use the plt map for showing the clusterings as a 
secondary visualization. 

# Travel places planned 
* NC
  * Chapel Hill 
    * The data read in for this one is a bit special since this was the 
      first place to plan. Later places all used the data from Google Map 
      export rather than manual inputs for higher efficiency. 
  * Wilmington
    * Major locations shot in the film Blue Velvet: https://wilmtv.com/production/blue-velvet-1986
    * This is the __1st place__ that all the codes are set to use and can be 
      used as a template for the later travel planning for other places. 