from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom
import geopy
from config import ureg
from models import FlightDataPoint, Flight
from .common import create_dir_and_file


def prettify_xml(elem):
    """
    Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    rebuilt = minidom.parseString(rough_string)
    return rebuilt.toprettyxml(indent="  ")


# TODO: Сделать палитру автоматическую
def flight_data_point(flight_data: list[FlightDataPoint], metadata: Flight | None = None):
    """ Запишем в формате kml информацию о приёмниках и траектории самолёта. """
    def get_location_name(position: geopy.Point) -> tuple[str, str]:
        geolocator = geopy.geocoders.Nominatim(user_agent='mlat-export')
        location = geolocator.reverse(position, language='en')
        loc_dict: dict[str, str] = location.raw['address']
        for key in ['city', 'state', 'country', 'ISO3166-2-lvl4']:
            if key in loc_dict:
                return loc_dict[key], loc_dict[key]
        return 'unknown', 'unk'

    def coord_to_str(position: geopy.Point, altitude: ureg.Quantity) -> str:
        return f'{position.longitude},{position.latitude},{int(altitude.to('m').magnitude)}'

    def get_line_color(altitude: int):
        colors = {
            0: 'ffffffff',
            1000: 'ffffea00',
            2000: 'ff00ff72',
            3000: 'ff00ff9c',
            4000: 'ff00ffd2',
            5000: 'ff00ffe4',
            6000: 'ff00eaff',
            7000: 'ff00c0ff',
            8000: 'ff0096ff',
            9000: 'ff0078ff',
            10000: 'ff7800ff'
        }

        altitudes = sorted(list(colors.keys()))

        for j in range(len(altitudes)-1):
            if altitudes[j] <= altitude < altitudes[j + 1]:
                return colors[altitudes[j]]
        return colors[max(altitudes)]

    if metadata:
        start_city, start_short = metadata.airport_from.city, metadata.airport_from.iata
        end_city, end_short = metadata.airport_to.city, metadata.airport_to.iata
    else:
        start_city, start_short = get_location_name(flight_data[0].position)
        end_city, end_short = get_location_name(flight_data[-1].position)

    __filename__ = f'flight_({start_short}-{end_short}).kml'
    __extra_dir__ = 'kml'

    route_description = ("<div><div><span><b>Altitude:</b></span> <span>{altitude} ft</span></div>"
                         "<div><span><b>Heading:</b></span> <span>{heading}</span></div>"
                         "<div><span><b>Timestamp:</b></span> <span>{timestamp}</span></div>")
    trail_description = ("<div><div><span><b>Altitude:</b></span> <span>{altitude} ft</span></div>"
                         "<div><span><b>Timestamp:</b></span> <span>{timestamp}</span></div>")

    def create_icon_element(heading: int) -> Element:
        _style = tree.createElement('Style')
        _icon_style = tree.createElement('IconStyle')

        _heading = tree.createElement('heading')
        _heading.appendChild(tree.createTextNode(str(heading)))
        _icon_style.appendChild(_heading)

        _href = tree.createElement('href')
        _href.appendChild(tree.createTextNode('http://maps.google.com/mapfiles/kml/shapes/airports.png'))
        _icon = tree.createElement('Icon')
        _icon.appendChild(_href)
        _icon_style.appendChild(_icon)
        _style.appendChild(_icon_style)
        return _style

    tree = minidom.Document()

    kml = tree.createElement('kml')
    kml.setAttribute('xmlns', 'http://www.opengis.net/kml/2.2')
    tree.appendChild(kml)

    document = tree.createElement('Document')
    kml.appendChild(document)

    name = tree.createElement('name')
    name.appendChild(tree.createTextNode(f'Flight {start_city} - {end_city}'))
    document.appendChild(name)

    description = tree.createElement('description')
    description.appendChild(tree.createTextNode(f'Flight from {start_city} to {end_city}'))
    document.appendChild(description)

    route = tree.createElement('Folder')
    name = tree.createElement('name')
    name.appendChild(tree.createTextNode('Route'))
    route.appendChild(name)

    for row in flight_data:
        placemark = tree.createElement('Placemark')

        name = tree.createElement('name')
        name.appendChild(tree.createTextNode(str(row.timestamp.to('s').magnitude)))
        placemark.appendChild(name)

        description = tree.createElement('description')
        description.appendChild(tree.createCDATASection(route_description.format(**row.to_dict())))
        placemark.appendChild(description)

        # timestamp = SubElement(placemark, 'Timestamp')

        style = create_icon_element(int(row.heading))
        placemark.appendChild(style)
        # SubElement(timestamp, 'when').text = str(row.timestamp.to('s').magnitude)

        point = tree.createElement('Point')

        altitude_mode = tree.createElement('altitudeMode')
        altitude_mode.appendChild(tree.createTextNode('absolute'))
        point.appendChild(altitude_mode)

        coordinates = tree.createElement('coordinates')
        coordinates.appendChild(tree.createTextNode(coord_to_str(row.position, row.altitude)))
        point.appendChild(coordinates)

        placemark.appendChild(point)
        route.appendChild(placemark)

    document.appendChild(route)
    trail = tree.createElement('Folder')
    name = tree.createElement('name')
    name.appendChild(tree.createTextNode('Trail'))
    trail.appendChild(name)

    for i in range(len(flight_data) - 1):
        row, next_row = flight_data[i], flight_data[i + 1]
        placemark = tree.createElement('Placemark')

        name = tree.createElement('name')
        name.appendChild(tree.createTextNode(f'P-{i + 1}'))
        placemark.appendChild(name)

        description = tree.createElement('description')
        description.appendChild(tree.createCDATASection(trail_description.format(**row.to_dict())))
        placemark.appendChild(description)

        style = tree.createElement('Style')
        line_style = tree.createElement('LineStyle')

        color = tree.createElement('color')
        color.appendChild(tree.createTextNode(get_line_color((int(row.altitude.to('m').magnitude) +
                                                              int(next_row.altitude.to('m').magnitude)) // 2)))
        line_style.appendChild(color)

        width = tree.createElement('width')
        width.appendChild(tree.createTextNode('2'))
        line_style.appendChild(width)

        style.appendChild(line_style)
        placemark.appendChild(style)

        multi_geometry = tree.createElement('MultiGeometry')
        line_string = tree.createElement('LineString')

        tessellate = tree.createElement('tessellate')
        tessellate.appendChild(tree.createTextNode('1'))
        line_string.appendChild(tessellate)

        altitude_mode = tree.createElement('altitudeMode')
        altitude_mode.appendChild(tree.createTextNode('absolute'))
        line_string.appendChild(altitude_mode)

        coordinates = tree.createElement('coordinates')
        coordinates.appendChild(tree.createTextNode(
            f'{coord_to_str(row.position, row.altitude)} {coord_to_str(next_row.position, next_row.altitude)}'))
        line_string.appendChild(coordinates)

        multi_geometry.appendChild(line_string)
        placemark.appendChild(multi_geometry)
        trail.appendChild(placemark)

    document.appendChild(trail)

    file_path = create_dir_and_file(__filename__, __extra_dir__)
    with file_path.open('w', encoding='utf-8') as file:
        tree.writexml(file, indent="  ", addindent="  ", newl="\n", encoding='utf-8')
