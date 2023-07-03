import json
import pandas as pd
import math


def read_json_file(file_path, encoding='utf-8'):
    # Read the Google map json.
    # Use utf-8 encoding because the file can contain special characters
    with open(file_path, 'r', encoding=encoding) as file:
        json_data = json.load(file)
        return json_data


def json_to_df(file_path):
    # Convert the Google map json into a df
    json_data = read_json_file(file_path)

    location_list = json_data['features']

    location_df = pd.json_normalize(location_list)

    return location_df


def drop_same_columns(input_df):
    # Remove columns that have the same data across all the rows in the
    # input_df. For exmaple, if a column has "Point" for all the rows,
    # this column will be removed
    output_df = input_df.copy()

    # Find columns with the same data across all rows
    columns_to_drop = []
    for column in output_df.columns:
        if output_df[column].apply(lambda x: tuple(x) if isinstance(x,
                                                                    list) else x).nunique() == 1:
            columns_to_drop.append(column)

    # Drop the identified columns
    output_df = output_df.drop(columns=columns_to_drop)

    print('> Columns that contain the same data across all the rows are {} '
          'and they are dropped.'.format(columns_to_drop))
    return output_df


def drop_custom_columns(input_df):
    # Remove the columns picked by user given by columns_to_drop_list_of_str
    # to specify the headers of those columns
    output_df = input_df.copy()

    columns_to_drop_list_of_str = [
        'geometry.coordinates',
        'properties.Published',
        'properties.Updated',
        'properties.Location.Country Code'
    ]  # This list contains the columns that I don't think are important

    # Drop the picked columns
    output_df = output_df.drop(columns=columns_to_drop_list_of_str)
    print('> Columns picked by the user are {} and they are dropped.'.format(
        columns_to_drop_list_of_str))
    return output_df


def organize_title_to_address(input_df):
    # Google map json has a very annoying feature: if a location has no
    # title, it'll put its address into the column Title and leave NaN in
    # the column Address. This function corrects that
    output_df = input_df.copy()

    mask = output_df['properties.Location.Address'].apply(
        lambda x: isinstance(x, float) and math.isnan(x)) & \
           output_df['properties.Title'].notnull()
    output_df.loc[mask, 'properties.Location.Address'] = \
        output_df.loc[mask, 'properties.Title']
    output_df.loc[mask, 'properties.Title'] = float('nan')

    print('> The issue with column properties.Title and '
          'properties.Location.Address has been corrected.')

    output_df = output_df.drop(
        columns=['properties.Title'])
    # Col properties.Title and col properties.Location.Business Name can
    # contain very similar data (they're the same for most rows). Since
    # properties.Location.Business Name col contains names used in Google
    # map for locations when the user click a location on the map, the col
    # properties.Title can be removed
    print('> Column properties.Title has been dropped since Column '
          'properties.Location.Business Name contains the same information')

    return output_df


def rename_columns(input_df):
    # The df created by using the info from Google map json will have some
    # very long column headers and this function will rename those columns with
    # shorter headers

    output_df = input_df.copy()
    column_mapping = {
        'properties.Google Maps URL': 'Google Maps URL',
        'properties.Location.Geo Coordinates.Latitude': 'Latitude',
        'properties.Location.Geo Coordinates.Longitude': 'Longitude',
        'properties.Location.Address': 'Address',
        'properties.Location.Business Name': 'Business Name'
    }

    output_df.rename(columns=column_mapping, inplace=True)
    print('> All column headers have been renamed to be shorter.')
    return output_df


def latitude_longitude_to_num(input_df):
    # Convert the str of num inside the columns Latitude and Longitude into
    # float. Without this step, all the locations later mapped out will be
    # in a straight line
    output_df = input_df.copy()

    output_df['Latitude'] = output_df['Latitude'].astype(float)
    output_df['Longitude'] = output_df['Longitude'].astype(float)

    print('> Numerical data (Latitude and Longitude) have been converted '
          'into numbers from strings.')
    return output_df


def location_df_clean(input_df):
    # Caller function that cleans the location df.

    output_df = input_df.copy()
    output_df = drop_same_columns(output_df)
    output_df = drop_custom_columns(output_df)
    output_df = organize_title_to_address(output_df)
    output_df = rename_columns(output_df)
    output_df = latitude_longitude_to_num(output_df)
    return output_df


def location_df_filter_by_allowed_cities(input_df, city_names_list):
    # Filter out the data for the locations in cities that you'll visit. I
    # used city_names_list rather than a single city name because how you
    # see as a "city" on the map is different from how Google defines as a
    # "city," which is strict. For example, the Holiday Inn Resort Lumina is
    # "in" Wilmington, but it's actually in Wrightsville Beach; if you only
    # use "Wilmington" for filtering, this hotel would be filtered out

    copy_df = input_df.copy()

    # Filter the rows based on the conditions
    filtered_df = copy_df[
        copy_df['Address'].str.split(',').str[1].str.strip().isin(
            city_names_list) |
        copy_df['Address'].str.split(',').str[0].str.strip().isin(
            city_names_list)]
    # The allowed city name should be either the 2nd substring in the Address
    # string (mostly in cases for restaurants or museums) or the 1st
    # substring (mostly in cases for nature preserves)

    filtered_df.reset_index(drop=True, inplace=True)
    return filtered_df


def label_based_on_scraped_category(input_df):
    # Because the scraped category from Google map is very detailed,
    # this function further categorized a category into 1 of the
    # user-defined categories below. The matching can be done partially so
    # as long as the original category string contains any substring in the
    # tuples used as keys in label_dict, it'll be matched to that category.
    # All the other categories that are unmatched with any category will
    # "Site".

    label_dict = {
        ('restaurant', 'grill', 'bar'): 'Restaurant',
        ('garden', 'nature preserve', 'park', 'arboretum'): 'Garden',
        ('museum'): 'Museum',
        ('store', 'market', 'shopping mall', 'shop'): 'Store',
        ('no category', 'building'): 'Site',
        # All the other categories that I'm
        # not interested in will also be under this category
        ('closed'): 'Closed'  # This is for the locations that are "Permanently
        # closed" or "Temporarily Closed" and you shouldn't map these
        # locations out on your maps
    }  # I have to use tuples as keys since they're immutable

    output_df = input_df.copy()

    category_labels = []
    for extracted_category in output_df['Extracted Category']:
        lowercase_extracted_category = extracted_category.lower()

        check_list = lowercase_extracted_category.split()
        check_list.append(lowercase_extracted_category)
        # lowercase_extracted_category itself also need to be checked

        category = 'Site'
        for term in check_list:
            for tuple_key, category_str in label_dict.items():
                if term in tuple_key:
                    category = category_str
                    break

        category_labels.append(category)

    output_df['Category'] = category_labels
    return output_df
