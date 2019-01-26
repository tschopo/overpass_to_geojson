#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import json
import geopandas as gpd
import geojson


# In[ ]:


def geojson_nodes(overpass_json):
    
    features = []
    geometry = None
    
    for elem in overpass_json['elements']:
        
        elem_type = elem.get("type")
        
        if elem_type and elem_type == "node":
            
            geometry = geojson.Point((elem.get("lon"), elem.get("lat")))
            
            feature = geojson.Feature(id=elem['id'], geometry=geometry, properties=elem.get("tags"))
            features.append(feature)
            
    return geojson.FeatureCollection(features)


def geojson_ways(overpass_json):

    # first construct a node df for lookup of coordinates
    t = geojson_nodes(overpass_json)
    all_nodes = gpd.GeoDataFrame(t['features'])

    features = []
    geometry = None
    
    for elem in overpass_json['elements']:
        
        elem_type = elem.get("type")

        if elem_type and elem_type == "way":
            
            coords = []
            
            for node_id in elem['nodes']:
                
                # get the coordinates of the node from all_nodes df
                coords.append(all_nodes[all_nodes['id'] == node_id]['geometry'].iloc[0]['coordinates'])
                
            geometry = geojson.LineString(coords)
            
            feature = geojson.Feature(id=elem['id'], geometry=geometry, properties=elem.get("tags"))
            features.append(feature)

    return geojson.FeatureCollection(features)


# In[ ]:


overpass_url = "http://overpass-api.de/api/interpreter"

lat_max,lon_min,lat_min,lon_max = 47.617581, 7.606412, 47.586086, 7.668244
overpass_query = '''
[out:json][timeout:25];
(
way[highway=motorway]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway= trunk]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=primary]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=secondary]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=tertiary]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=unclassified]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=residential]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=service]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=motorway_link]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=trunk_link]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=primary_link]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=secondary_link]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=tertiary_link]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=unclassified_link]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=residential_link]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=service_link]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=living_street]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=track]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=escape]({lat_min}, {lon_min}, {lat_max}, {lon_max});
way[highway=road]({lat_min}, {lon_min}, {lat_max}, {lon_max});
);
out body;
>;
out skel qt;
'''.format(lat_min = lat_min, lon_min = lon_min, lat_max = lat_max, lon_max = lon_max)


# In[ ]:


response = requests.get(overpass_url, params={'data': overpass_query})
response = json.loads(response.text)


# In[ ]:


output = geojson_ways(response)


# In[ ]:


with open("ways.geosjon", 'w') as outfile:
     geojson.dump(output, outfile)

