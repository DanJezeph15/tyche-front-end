import copy
import math

import reverse_geocoder as rg
from global_land_mask import globe

__all__ = ['generate_search_coordinates_for_layered_search']


def generate_search_coordinates_for_layered_search(
    starting_coordinates: str, radius: int, layers: int, state: str = None
) -> list[str]:
    """
    Generates search coordinates based off the starting coordinates, radius and the amount of layers to search for.

    Conversions for lat and lng from:
    https://stackoverflow.com/questions/1253499/simple-calculations-for-working-with-lat-lon-and-km-distance
    """
    starting_coordinates = list(map(float, starting_coordinates.replace(' ', '').split(',')))
    lat_coords = [starting_coordinates[0]]  # X axis
    lng_coords = [starting_coordinates[1]]  # Y axis

    for i in range(1, layers):
        lat_increment = radius * 1.3 * i / 110_574

        lat_pos_val = starting_coordinates[0] + lat_increment
        lat_neg_val = starting_coordinates[0] - lat_increment

        lat_coords.append(lat_pos_val)
        lat_coords.append(lat_neg_val)

        # Need to convert the lat value to radians for the cos calculation
        lat_in_radians = math.radians(starting_coordinates[0])
        lng_increment = radius * 1.5 * i / (math.cos(lat_in_radians) * 111_320)

        lng_pos_val = starting_coordinates[1] + lng_increment
        lng_neg_val = starting_coordinates[1] - lng_increment

        lng_coords.append(lng_pos_val)
        lng_coords.append(lng_neg_val)

    all_coords = []

    for lng in lng_coords:
        for lat in lat_coords:
            all_coords.append([lat, lng])

    all_coords_copy = copy.deepcopy(all_coords)
    for coords in all_coords_copy:
        circumference_points = _get_circumference_coordinates(coords, radius)
        if not _check_coordinates_contain_land(circumference_points):
            all_coords.remove(coords)
            continue

        if state and not _check_coordinates_within_state([coords], state):
            all_coords.remove(coords)

    return_coords = []
    for coords in all_coords:
        lat = coords[0]
        lng = coords[1]
        circle_size = _calculate_circle_size_on_map(radius, lat)
        return_coords.append(f'{lat},{lng},{circle_size}')
    return return_coords


def _calculate_circle_size_on_map(meters: int, latitude: float) -> float:
    """
    Calculate the size of the circle on the map based off the radius
    """
    val = meters / 0.075 / math.cos(latitude * math.pi / 180)
    return val


def _get_circumference_coordinates(coordinates: list[float], radius: int) -> list[list[float]]:
    """
    Takes a starting coordinate and calculates 8 different coordiantes around the circumference of the circle. We
    calculate the N NE E SE S SW W NW points around the circumference of our circle.
    """
    lat, lng = coordinates[0], coordinates[1]
    lat_in_radians = math.radians(lat)
    coordinates_to_check_land = [[lat, lng]]
    lat_increment = radius / 110_574
    lat_pos = lat + lat_increment
    lat_neg = lat - lat_increment
    lng_increment = radius / (math.cos(lat_in_radians) * 111_320)
    lng_pos = lng + lng_increment
    lng_neg = lng - lng_increment

    coordinates_to_check_land.extend([[lat_pos, lng], [lat_neg, lng], [lat, lng_pos], [lat, lng_neg]])

    # We multiply the radius by this value to get the diagonal points (NE NW SE SW). We can calculate this value
    # by using a unit circle. We know that a diagonal line from the center to the edge will have angles of 45
    # degrees each side meaning that the x and y values will be equal. So we can use the Pythagorean theorem to
    # calculate the value. x^2 + y^2 = radius^2 where x = y. So x^2 + x^2 = radius^2 which we can rewrite to
    # 2x^2 = radius^2. For a unit circle of diameter 1 we can do 2 * 0.5^2 = 0.5^2 which is 0.70711 to 5dp.
    diag_multiplier = 0.70711
    diag_lat_increment = radius * diag_multiplier / 110_574
    diag_lat_pos = lat + diag_lat_increment
    diag_lat_neg = lat - diag_lat_increment
    diag_lon_increment = radius * diag_multiplier / (math.cos(lat_in_radians) * 111_320)
    diag_lon_pos = lng + diag_lon_increment
    diag_lon_neg = lng - diag_lon_increment
    coordinates_to_check_land.extend(
        [
            [diag_lat_pos, diag_lon_pos],
            [diag_lat_pos, diag_lon_neg],
            [diag_lat_neg, diag_lon_pos],
            [diag_lat_neg, diag_lon_neg],
        ]
    )
    return coordinates_to_check_land


def _check_coordinates_contain_land(coordinates_to_check_land: list[list[float]]) -> bool:
    """
    Checks that at least on of the coordinates along the circumference contains some land, if it does, we return
    True, if it doesn't, we return False. Then we can handle the coordinates accordingly.
    """
    for lat, lon in coordinates_to_check_land:
        if globe.is_land(lat, lon):
            return True
    return False


def _check_coordinates_within_state(coordinates: list[list[float]], state: str) -> bool:
    """
    Checks if the coordinates are within the given state. If one point lies within the state, then we return True.
    """
    for coordinates in coordinates:
        result = rg.search(coordinates)
        if result and (n_state := result[0].get('admin1')) and n_state.lower() == state.lower():
            return True
    return False
