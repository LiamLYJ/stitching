
import glob
from PIL import Image
import os
from PIL.ExifTags import TAGS, GPSTAGS
from binascii import hexlify
import xmltodict
import utils

def get_exif_data(image):
    """
    Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags
    """
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value

    return exif_data

def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None

def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    """
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data):
    """
    Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)
    """
    lat = None
    lon = None

    '''
    for key, values in exif_data.items():
	print(key, values)
    '''

    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]

        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')
        gps_altitude = _get_if_exist(gps_info, 'GPSAltitude')
        gps_altitude_ref = _get_if_exist(gps_info, 'GPSAltitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref and gps_altitude and gps_altitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon

            alt = gps_altitude[0]/gps_altitude[1]
            if hexlify(gps_altitude_ref) == 0 :
                alt = 0 - alt

    return lat, lon


def xmp(filename):

    with Image.open(filename) as im:
        for segment, content in im.applist:

            marker, body = content.split(b'\x00', 1)

            if segment == 'APP1' and marker == b'http://ns.adobe.com/xap/1.0/':
                # parse the XML string with any method you like
                dji = xmltodict.parse(body)
                '''for key, values in dji['x:xmpmeta']['rdf:RDF']['rdf:Description'].items():
                    print (key + " " + values)
                '''

                alt = dji['x:xmpmeta']['rdf:RDF']['rdf:Description']['@drone-dji:AbsoluteAltitude']
                roll = dji['x:xmpmeta']['rdf:RDF']['rdf:Description']['@drone-dji:FlightRollDegree']
                yaw = dji['x:xmpmeta']['rdf:RDF']['rdf:Description']['@drone-dji:FlightYawDegree']
                pitch = dji['x:xmpmeta']['rdf:RDF']['rdf:Description']['@drone-dji:FlightPitchDegree']

                return alt, roll, yaw, pitch

def prepare(file_name, image_path, workspace_dir):

    with open(file_name, 'w') as fn:
        for image in sorted(glob.glob(os.path.join(image_path, '*'))):
            exif_data = get_exif_data(Image.open(image))
            lat, lon = get_lat_lon(exif_data)

            alt, roll, yaw, pitch = xmp(image)
            #print lon, lat, alt, yaw, pitch, roll
            st = (os.path.basename(image)) + "," + str(float(lon)) + "," + str(float(lat)) + "," + str(float(alt)) + "," + str(float(yaw)) + "," + str(float(pitch)) + "," + str(float(roll)) + "\n"
            fn.write(st)

    
    all_images, data_matrix = utils.importData(file_name, image_path, workspace_dir)
    return all_images, data_matrix