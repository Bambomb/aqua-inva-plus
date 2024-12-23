import numpy as np

def map_range(x, in_min, in_max, out_min, out_max):
    return out_min + (((x - in_min) / (in_max - in_min)) * (out_max - out_min))

def getDistanceFromLatLonInKm(lat1,lon1,lat2,lon2) :
    if(type(lat1)==str or type(lon1)==str or type(lat2)==str or type(lon2)==str): return 0

    R = 6371 # Radius of the earth in km
    dLat = np.deg2rad(lat2-lat1)  # deg2rad below
    dLon = np.deg2rad(lon2-lon1)
    a =    np.sin(dLat/2) * np.sin(dLat/2) +    np.cos(np.deg2rad(lat1)) * np.cos(np.deg2rad(lat2)) *    np.sin(dLon/2) * np.sin(dLon/2)
    c = 2 * np.atan2(np.sqrt(a), np.sqrt(1-a))
    d = R * c # Distance in km
    return d

def deg2rad(deg):
  return deg * (np.pi/180)