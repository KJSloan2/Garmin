import os
from datetime import datetime
import xml.etree.ElementTree as ET
import csv
import json
import math
from pyproj import Transformer

write_dataOut = open("%s%s" % (r"output/gpx_to_csv/",'gpx_points.csv'), 'w',newline='', encoding='utf-8')
writer_dataOut = csv.writer(write_dataOut)
writer_dataOut.writerow(['FILE_ID', 'FILE_GROUP', 'EXPERIMENT', 'LAT ', 'LON', 'ELV', 'HEART_RATE', 'DATE', 'TIME'])

def parse_gpx(file_path, csvOutput, paricipantInfo, path_obj):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Namespace
    ns = {'default': 'http://www.topografix.com/GPX/1/1'}
    ns3 = {'ns3': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'}
    
    # Parse metadata
    metadata = root.find('default:metadata', ns)
    if metadata is not None:
        name = metadata.find('default:name', ns).text if metadata.find('default:name', ns) is not None else None
        desc = metadata.find('default:desc', ns).text if metadata.find('default:desc', ns) is not None else None
        #print(f"Metadata - Name: {name}, Description: {desc}")
    
    # Parse waypoints
    waypoints = []
    for wpt in root.findall('default:wpt', ns):
        lat = float(wpt.get('lat'))
        lon = float(wpt.get('lon'))
        ele = float(wpt.find('default:ele', ns).text) if wpt.find('default:ele', ns) is not None else None
        time = wpt.find('default:time', ns).text if wpt.find('default:time', ns) is not None else None
        waypoints.append({'lat': lat, 'lon': lon, 'ele': ele, 'time': time})
    
    # Print waypoints
    #for wp in waypoints:
        #print(f"Waypoint - Lat: {wp['lat']}, Lon: {wp['lon']}, Ele: {wp['ele']}, Time: {wp['time']}")
    
    # Parse tracks
    tracks = []
    for trk in root.findall('default:trk', ns):
        track = {'name': trk.find('default:name', ns).text if trk.find('default:name', ns) is not None else None, 'segments': []}
        for trkseg in trk.findall('default:trkseg', ns):
            segment = []
            for trkpt in trkseg.findall('default:trkpt', ns):
                lat = float(trkpt.get('lat'))
                lon = float(trkpt.get('lon'))
                ele = float(trkpt.find('default:ele', ns).text) if trkpt.find('default:ele', ns) is not None else None
                time = trkpt.find('default:time', ns).text if trkpt.find('default:time', ns) is not None else None
                hr = trkpt.find('.//ns3:hr', namespaces=ns3).text if trkpt.find('.//ns3:hr', namespaces=ns3) is not None else None
                segment.append({'lat': lat, 'lon': lon, 'ele': ele, 'time': time, 'hr': hr})
            track['segments'].append(segment)
        tracks.append(track)
    
    # Print tracks
    for track in tracks:
        print(f"Track - Name: {track['name']}")
        for segment in track['segments']:
            for point in segment:
                #print(f"  Point - Lat: {point['lat']}, Lon: {point['lon']}, Ele: {point['ele']}, Time: {point['time']}")

                dt = datetime.strptime(point['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                new_hour = (dt.hour - 5) % 24
                updated_dt = dt.replace(hour=new_hour)
                formatted_time = updated_dt.strftime("%H:%M:%S")
                date = dt.date()

                hr = point['hr']
                print(hr)
                #ns3:hr

                #xyz = geo_to_xyz(point['lat'], point['lon'], point['ele'])
                xyz = [point['lat'], point['lon'], point['ele']]
                csvOutput.writerow([
                    paricipantInfo[0], paricipantInfo[1], paricipantInfo[2], 
                    xyz[0], xyz[1], xyz[2], hr, date, formatted_time])
                
                path_obj['geometry']['coordinates'].append([point['lat'], point['lon']])
                path_obj['properties']['hr'].append(hr)
                path_obj['properties']['time'].append(formatted_time)
        paths_output['features'].append(path_obj)
    
    return waypoints, tracks

def geo_to_xyz(lat, lon, elv, radius_km=6371):
    # Convert latitude and longitude from degrees to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    # Convert elevation from feet to kilometers
    elevation_km = elv * 0.0003048
    
    # Calculate x, y, z
    x = radius_km * math.cos(lat_rad) * math.cos(lon_rad)
    y = radius_km * math.cos(lat_rad) * math.sin(lon_rad)
    z = radius_km * math.sin(lat_rad) + elevation_km
    return [x, y, z]

def parse_gpx_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.gpx'):
            filenameBase = strip_extension(filename)

            path_obj = {
                "type": "Feature", "properties": {
                    "id": filenameBase,
                    "hr":[], 
                    "time":[]
                    },
                "geometry":{"type": "LineString", "coordinates": []}
                }

            parse_fileName = filenameBase.split("_")
            participantId = parse_fileName[0]
            conditionGroupId = parse_fileName[1]
            experiment = parse_fileName[2]
            file_path = os.path.join(folder_path, filename)
            print(f"\nParsing file: {file_path}")
            waypoints, tracks = parse_gpx(file_path, writer_dataOut, [participantId, conditionGroupId, experiment], path_obj)

def strip_extension(file_name):
    base_name, _ = os.path.splitext(file_name)
    return base_name
paths_output = {"type": "FeatureCollection", "features":[]}
# Example usage
folder_path = r'data/gpx/'
parse_gpx_files_in_folder(folder_path)

geojson_file = "%s%s" % (r"output/",'garmin_gpx_paths.geojson')
with open(geojson_file, "w") as f:
    json.dump(paths_output, f)
