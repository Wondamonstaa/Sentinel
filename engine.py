!unzip data/flood_data.zip -d flood_data

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
from mpl_toolkits.basemap import Basemap

# set environment variables
%set_env LOCAL_DATA_DIR=/dli/task/flood_data

# set paths for images and masks
image_dir=os.path.join(os.getenv('LOCAL_DATA_DIR'), 'images')
mask_dir=os.path.join(os.getenv('LOCAL_DATA_DIR'), 'masks')

def count_num_images(file_dir): 
    """
    This function returns a dictionary representing the count of images for each region as the key. 
    """
    # list all files in the directory
    file_list=os.listdir(file_dir)
    region_count={}
    # iterate through the file_list and count by region
    for file_name in file_list: 
        region=file_name.split('_')[0]
        if (len(file_name.split('.'))==2) and (region in region_count): 
            region_count[region]+=1
        elif len(file_name.split('.'))==2: 
            region_count[region]=1
    return region_count

images_count=count_num_images(os.path.join(image_dir, 'all_images'))
masks_count=count_num_images(os.path.join(mask_dir, 'all_masks'))

# display counts
print(f'-----number of images: {sum(images_count.values())}-----')
display(sorted(images_count.items(), key=lambda x: x[1]))

print(f'-----number of masks: {sum(masks_count.values())}-----')
display(sorted(masks_count.items(), key=lambda x: x[1]))

def get_coordinates(catalog_dir): 
    """
    This function returns a list of boundaries for every image as [[lon, lat], [lon, lat], [lon, lat], etc.] in the catalog. 
    """
    catalog_list=os.listdir(catalog_dir)
    all_coordinates=[]
    for catalog in catalog_list: 
        # check if it's a directory based on if file_name has an extension
        if len(catalog.split('.'))==1:
            catalog_path=f'{catalog_dir}/{catalog}/{catalog}.json'
            # read catalog
            with open(catalog_path) as f: 
                catalog_json=json.load(f)
            # parse out coordinates
            coordinates_list=catalog_json['geometry']['coordinates'][0]
            lon=[coordinates[0] for coordinates in coordinates_list]
            all_coordinates.append(lon)
            lat=[coordinates[1] for coordinates in coordinates_list]
            all_coordinates.append(lat)
    return all_coordinates

image_catalog_dir=os.path.join(os.getenv('LOCAL_DATA_DIR'), 'catalog', 'sen1floods11_hand_labeled_source')
image_coordinates_list=get_coordinates(image_catalog_dir)

# create figure
plt.figure(figsize=(15, 10))

# create a Basemap
m=Basemap(projection='merc', llcrnrlat=-80, urcrnrlat=80, llcrnrlon=-180, urcrnrlon=180)

# display blue marble image
m.bluemarble(scale=0.2) # 0.2 downsamples to 1350x675 image
m.drawcoastlines(color='white', linewidth=0.2) # add coastlines
m.drawparallels(range(-90, 90, 10), labels=[0, 1, 0, 0], color='white', textcolor='black')
m.drawmeridians(range(-180, 180, 10), labels=[0, 0, 0, 1], color='white', textcolor='black', rotation=90)

# flatten lat and lon coordinate lists
image_lon=[image_coordinates_list[x] for x in range(len(image_coordinates_list)) if x%2==0]
image_lon=np.concatenate(image_lon).ravel()
image_lat=[image_coordinates_list[x] for x in range(len(image_coordinates_list)) if x%2==1]
image_lat=np.concatenate(image_lat).ravel()

# convert lon/lat to x/y map projection coordinates
x, y=m(image_lon, image_lat)
plt.scatter(x, y, s=10, marker='o', color='Red') 

plt.title('Data Distribution')
plt.show()

def get_extent(file_path): 
    """
    This function returns the extent as [left, right, bottom, top] for a given image. 
    """
    # read catalog for image
    with open(file_path) as f: 
        catalog_json=json.load(f)
    coordinates=catalog_json['geometry']['coordinates'][0]
    coordinates=np.array(coordinates)
    # get boundaries
    left=np.min(coordinates[:, 0])
    right=np.max(coordinates[:, 0])
    bottom=np.min(coordinates[:, 1])
    top=np.max(coordinates[:, 1])
    return left, right, bottom, top

def tiles_by_region(region_name, plot_type='images'): 
    # set catalog and images/masks path
    catalog_dir=os.path.join(os.getenv('LOCAL_DATA_DIR'), 'catalog', 'sen1floods11_hand_labeled_source')
    if plot_type=='images': 
        dir=os.path.join(image_dir, 'all_images')
        cmap='viridis'
    elif plot_type=='masks': 
        dir=os.path.join(mask_dir, 'all_masks')
        cmap='gray'
    else: 
        raise Exception('Bad Plot Type')

    # initiate figure boundaries, which will be modified based on the extent of the tiles
    x_min, x_max, y_min, y_max=181, -181, 91, -91
    fig=plt.figure(figsize=(15, 15))
    ax=plt.subplot(111)
    
    # iterate through each image/mask and plot
    file_list=os.listdir(dir)
    for each_file in file_list:
        # check if image/mask is related to region and a .png file
        if (each_file.split('.')[-1]=='png') & (each_file.split('_')[0]==region_name): 
            # get boundaries of the image
            extent=get_extent(f"{catalog_dir}/{each_file.split('.')[0]}/{each_file.split('.')[0]}.json")
            x_min, x_max=min(extent[0], x_min), max(extent[1], x_max)
            y_min, y_max=min(extent[2], y_min), max(extent[3], y_max)
            image=mpimg.imread(f'{dir}/{each_file}')
            plt.imshow(image, extent=extent, cmap=cmap)

    # set boundaries of the axis
    ax.set_xlim([x_min, x_max])
    ax.set_ylim([y_min, y_max])
    plt.show()
    
tiles_by_region(region_name='Spain', plot_type='images')

def tiles_by_boundaries(left_top, right_bottom, plot_type='images'): 
    # set catalog and images/masks path
    catalog_dir=os.path.join(os.getenv('LOCAL_DATA_DIR'), 'catalog', 'sen1floods11_hand_labeled_source')
    if plot_type=='images': 
        dir=os.path.join(image_dir, 'all_images')
        cmap='viridis'
    elif plot_type=='masks': 
        dir=os.path.join(mask_dir, 'all_masks')
        cmap='gray'
    else: 
        raise Exception('Bad Plot Type')

    # initiate figure boundaries, which will be modified based on the extent of the tiles
    x_min, x_max, y_min, y_max=left_top[0], right_bottom[0], right_bottom[1], left_top[1]
    ax_x_min, ax_x_max, ax_y_min, ax_y_max=181, -181, 91, -91

    fig=plt.figure(figsize=(15, 15))
    ax=plt.subplot(111)

    # iterate through each image/mask and plot
    file_list=os.listdir(dir)
    for each_file in file_list: 
        # check if image/mask is a .png file
        if each_file.split('.')[-1]=='png': 
            # get boundaries of the image/mask
            extent=get_extent(f"{catalog_dir}/{each_file.split('.')[0]}/{each_file.split('.')[0]}.json")
            (left, right, bottom, top)=extent
            if (left>x_min) & (right<x_max) & (bottom>y_min) & (top<y_max):
                ax_x_min, ax_x_max=min(left, ax_x_min), max(right, ax_x_max)
                ax_y_min, ax_y_max=min(bottom, ax_y_min), max(top, ax_y_max)
                image=mpimg.imread(f'{dir}/{each_file}')
                plt.imshow(image, extent=extent, cmap=cmap)

    # set boundaries of the axis
    ax.set_xlim([ax_x_min, ax_x_max])
    ax.set_ylim([ax_y_min, ax_y_max])
    plt.show()

tiles_by_boundaries(left_top=(-0.966, 38.4), right_bottom=(-0.597, 38.0), plot_type='images')
