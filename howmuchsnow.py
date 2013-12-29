import pygeoip
import numpy as np
from scipy.interpolate import griddata
from model import get_triangle_predictions, get_nearest


GEOIP_DATABASE = "/usr/share/GeoIP/GeoLiteCity.dat"

def how_much_snow_ipv4 (ip_address, persistent):
    #return interpolate_triangle(ipv4_to_gps (ip_address), persistent)
    return how_much_snow_gps (ipv4_to_gps (ip_address), persistent)

def ipv4_to_gps (ip_address):
    '''Takes IP address and returns latitude and longitude of the nearest city.'''
    gi = pygeoip.GeoIP(GEOIP_DATABASE)
    record = gi.record_by_addr(ip_address)
    return record['latitude'], record['longitude']

def how_much_snow_gps (user_loc, persistent):
    '''Takes a tuple of a user's estimated latitude and longitude, and a
    database connection. Returns a list of the three shortest distances from
    there to places in the database, and a list of the amounts of snow
    predicted for those three places.'''
    nearest = get_nearest(user_loc, persistent)
    coordinates = [(point['latitude'], point['longitude'], point['inches'])
                   for point in nearest]
    return interpolate_closest(coordinates, user_loc)

def interpolate_closest (coordinates, lat, lon):
    '''Takes a list of 3 points in 3D space and the x and y coordinates of
    another point. Defines a plane over the points. Returns the z coordinate of
    the last point. The 3 coordinates do not have to surround the other point.'''
    assert len(coordinates) == 3, 'Wrong number of coordinates passed in, may not define a plane.'''
    vector1, vector2 = coordinates[0] - coordinates[1], coordinates[2] - coordinates[1]
    normal = np.cross(vector1, vector2)
    # plane equation is ax + by + cz = d
    a, b, c = normal
    d = np.dot(coordinates[0], normal)
    # z = (ax + by - d) / -c
    return np.dot([a, b, -d], [lat, lon, 1]) / -c

def get_triangle(user_lat, user_lon, triangulation):
    #TODO can I do this by point id somehow?
    triangle_index = triangulation.find_simplex([user_lat, user_lon])
    triangle = triangulation.simplices[triangle_index]
    return triangulation.points[triangle]

def interpolate_triangle ((user_lat, user_lon), (conn, predictions, triangulation)):
    '''Takes a tuple of the user's estimated latitude and longitude, and a database connection.
    Finds a triangle of points surrounding the user's coordinates that are in the weather database.
    Interpolates from the triangle to the user's coordinates. Returns predicted amount of snow.'''
    tri_xy = get_triangle(user_lat, user_lon, triangulation)
    tri_z = get_triangle_predictions(tri_xy, conn, predictions)
    return griddata(tri_xy, tri_z, [[user_lat, user_lon]])
