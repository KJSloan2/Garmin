from pyproj import Transformer
from tools import csv_to_dict
import csv
import pandas as pd
import re

headers = [
    "WKT", "Division_Type", "STLength", "Updated_By", "Add_Time_Stamp", "Update_Time_Stamp", 
    "Division_Designator", "PLATTED", "Accuracy_Source", "Input_Method", "STArea", "Legal_Key",
      "Source_Document", "Parson_Methodology", "Spatial_Correction_Date"]

data_path = "%s%s" % (r"01_data\GIS\\",'arlington-tx-lots.csv')
data = pd.read_csv(data_path,encoding="utf-8")

data_geometry = data["WKT"]

#data_dict = csv_to_dict(data_path, headers)
#print(data_dict.keys())

def chunks(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]

# Define the transformer from EPSG:2276 to EPSG:4326
transformer = Transformer.from_crs("EPSG:2276", "EPSG:4326")

write_dataOut = open("%s%s" % (r"02_output\\",'GIS_epsg2276_to_epsg4326.csv'), 'w',newline='', encoding='utf-8')
writer_dataOut = csv.writer(write_dataOut)
writer_dataOut.writerow(["GEOMETRY_ID", "LAT", "LON"])

for i, coordString in enumerate(data_geometry):
    split_coordString = re.split(r'[(), ]', coordString)
    coords = []
    if split_coordString[0] == "POLYGON":
        for string in split_coordString:
            if string not in ["POLYGON", "Z", '']:
                coords.append(string)
    #elif split_coordString[0] == "MULTIPOLYGON":

    coords_chunks = chunks(coords, 3)
    coords_2276 = []
    for chunk in coords_chunks:
        coords_2276.append((float(chunk[0]), float(chunk[1])))
        coord = transformer.transform(float(chunk[0]), float(chunk[1]))
        print(coord[0], coord[1])
        writer_dataOut.writerow([i, coord[0], coord[1]])

    '''coords_4326 = [transformer.transform(x, y) for x, y in coords_2276]'''