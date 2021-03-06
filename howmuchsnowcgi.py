#!/usr/bin/env python2.7
import sys
from flup.server.fcgi import WSGIServer
from cgi import parse_qs
sys.path.append('/home/mmachenry/HowMuchSnow')
import howmuchsnow
import pages
import sqlalchemy as sa
import json

engine = sa.create_engine(howmuchsnow.DB)
conn = engine.connect()

def get_info(lat, lon):
    return json.dumps({
        'inches': howmuchsnow.how_much_snow_gps((lat, lon), conn),
        'coords': howmuchsnow.make_coordinates(lat, lon)
        })

def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    parameters = parse_qs(environ.get('QUERY_STRING', ''))
    if 'faq' in parameters:
        yield pages.faq
    elif 'geo' in parameters:
        lat = float(parameters['lat'][0])
        lon = float(parameters['lon'][0])
        # inches = howmuchsnow.how_much_snow_gps((lat, lon), conn)
        # yield inches
        yield get_info(lat, lon)
    elif 'ip' in parameters:
        ip_addr = environ['REMOTE_ADDR']
        lat, lon = ipv4_to_gps(ip_addr)
        # inches = howmuchsnow.how_much_snow_ipv4(ip_addr, conn)
        # yield inches
        yield get_info(lat, lon)
    else:
        yield pages.homepage


if __name__ == '__main__':
    WSGIServer(application).run()

