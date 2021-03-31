import json
import sys
import threading
import time
import cv2

import colorsys
import requests
import argparse
from hue_api import HueApi
from hue_api.exceptions import UninitializedException, ButtonNotPressedException, FailedToSetState

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")
parser.add_argument("-b", "--bridgeid", dest="bridge_id")
parser.add_argument("-ull", "--upleftlight", dest="up_left_light")
parser.add_argument("-url", "--uprightlight", dest="up_right_light")
parser.add_argument("-dll", "--downleftlight", dest="down_left_light")
parser.add_argument("-drl", "--downrightlight", dest="down_right_light")
cmd_args = parser.parse_args()


def verbose(*args, **kwargs):
    if cmd_args.verbose:
        print()
        print(*args, **kwargs)


####################################
#        Hue bridge setup          #
####################################
def hue_login():
    """
    This function will assure connection to hue bridge,
    and save user info in hue_api cache.
    """
    global api
    # instantiate a HueApi object
    api = HueApi()

    try:
        # load existing user if saved in cache
        verbose("Trying to load user from cache")
        api.load_existing(cache_file="cache")
        verbose("User saved in cache loaded")
        return
    except UninitializedException:
        # auto-find bridges on network & get list
        response = requests.get("https://discovery.meethue.com/")
        bridges = json.loads(response.text)

        # by default we take first bridge found
        current_bridge = bridges[0]
        if cmd_args.bridge_id:
            for bridge in bridges:
                if bridge.get("id") == cmd_args.bridge_id:
                    current_bridge = bridge
        verbose(f"Bridge with id: {current_bridge.get('id')} will be used")

        while True:
            try:
                print("Please push the button on the hue bridge...")
                api.create_new_user(current_bridge.get("internalipaddress"))
                verbose(f"User created on hue bridge ip: {current_bridge.get('internalipaddress')}")
                break
            except ButtonNotPressedException:
                print("Hue bridge button not pushed")
                print("Try again in three seconds...")
                time.sleep(3)

        open('cache', 'w+')
        api.save_api_key(cache_file="cache")
        verbose(f"User saved on cache")


####################################
#           Lights setup           #
####################################
def animation_light_on(light):
    try:
        verbose(f"Turning on light: {light.name}")
        time.sleep(0.2)
        light.set_off()
        time.sleep(0.2)
        light.set_on()
        time.sleep(0.2)
        light.set_brightness(20)
        time.sleep(0.2)
        light.set_brightness(254)
        time.sleep(0.2)
        light.set_brightness(100)
    except FailedToSetState:
        verbose(f"Error on config set light on for light: {light.name}")


def animation_light_off(light):
    try:
        verbose(f"Turning off light: {light.mame}")
        light.set_brightness(254)
        time.sleep(0.2)
        light.set_brightness(100)
        time.sleep(0.2)
        light.set_brightness(20)
        time.sleep(0.2)
        light.set_off()
    except FailedToSetState:
        verbose(f"Error on config set light off for light: {light.name}")


def get_hue_color_from_rgba(rgba):
    """
    HSV: Hue, Saturation, Value
    H: position in the spectrum
    S: color saturation ("purity")
    V: color brightness
    :param rgba: Color in rgba format
    :return: hue color and saturation (hue, saturation)
    """
    r, g, b, a = rgba
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    hue = int((2 ** 16 - 1) * h)
    saturation = int((2 ** 8 - 1) * s)
    return hue, saturation


def change_light_color(light, rgba):
    try:
        r, g, b, a = rgba
        if r == g == b ==0:
            light.set_off()
        else:
            light.set_on()
            light.set_color(*get_hue_color_from_rgba(rgba))
        # api.set_color((rgba[0], rgba[1], rgba[2]), indices=[light_id])
        # api.set_brightness(rgba[3], indices=[light_id])
    except FailedToSetState:
        verbose(f"Error on change light color for light: {light.name}")


def get_light_by_name(name):
    for light in api.fetch_lights():
        if light.name == name:
            animation_light_on(light)
            return light

    print(f"Error: Can't find light id for name: {name}")
    sys.exit(0)


def init_light_locations():
    global light_locations

    light_locations = {
        # light positions [x, y]
        "up_right_light": [0.5, 1.0, 0.0],
        "up_left_light": [-0.5, 1.0, 0.0],
        "down_right_light": [0.5, 1.0, 0.0],
        "down_left_light": [-0.5, 1.0, 0.0]
    }

    if not cmd_args.up_left_light:
        del light_locations["up_left_light"]
    else:
        light = get_light_by_name(cmd_args.up_left_light)
        light_locations[light] = light_locations.get("up_left_light")
        del light_locations["up_left_light"]
        verbose("Up-left light configured successfully")

    if not cmd_args.up_right_light:
        del light_locations["up_right_light"]
    else:
        light = get_light_by_name(cmd_args.up_right_light)
        light_locations[light] = light_locations.get("up_right_light")
        del light_locations["up_right_light"]
        verbose("Up-right light configured successfully")

    if not cmd_args.down_left_light:
        del light_locations["down_left_light"]
    else:
        light = get_light_by_name(cmd_args.down_left_light)
        light_locations[light] = light_locations.get("down_left_light")
        del light_locations["down_left_light"]
        verbose("Down-left light configured successfully")

    if not cmd_args.down_right_light:
        del light_locations["down_right_light"]
    else:
        light = get_light_by_name(cmd_args.down_right_light)
        light_locations[light] = light_locations.get("down_right_light")
        del light_locations["down_right_light"]
        verbose("Down-right light configured successfully")

    if not light_locations:
        print(
            "Error: no lights provided, "
            "you must provide either right-light (-rl) name or left-light (-ll) name or both"
        )
        sys.exit(0)


####################################
#        Video Capture Setup       #
####################################
def configure_rgb_frames():
    global video_width, video_height, rgb_frame
    time.sleep(2)  # wait for animation start complete
    # Init video capture
    capture = cv2.VideoCapture(0)

    # Try to get the first frame
    if capture.isOpened():
        verbose('Capture Device Opened')

    else:
        verbose("Unable to open Capture Device, please check your configuration")
        sys.exit(0)

    video_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))  # gets video width
    video_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))  # gets video height
    verbose(f"Video Shape is: {video_width}, {video_height}")

    # This section loops & pulls re-colored frames and always get the newest frame
    capture.set(cv2.CAP_PROP_BUFFERSIZE, 0)  # No frame buffer to avoid lagging, always grab newest frame
    capture_index = 0

    while not stop_stream:
        capture_index += 1
        frame = capture.grab()  # constantly grabs frames
        if capture_index % 1 == 0:  # Skip frames (1=don't skip,2=skip half,3=skip 2/3rds)
            frame, bgr_frame = capture.retrieve()  # processes most recent frame
            rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)  # corrects BGR to RGB

        # if no new frame: stop loop
        if not frame:
            break


####################################
#          Average image          #
####################################
def average_image():
    # Scales up locations to identify the nearest pixel based on lights locations
    time.sleep(2.2)  # wait for video size to be defined
    for light, light_pos in light_locations.items():
        # Translates x value and resizes to video aspect ratio
        light_pos[0] = ((light_pos[0]) + 1) * video_width // 2

        # Flips y, translates, and resize to vid aspect ratio
        light_pos[2] = (-1 * (light_pos[2]) + 1) * video_height // 2

    scaled_locations = list(light_locations.items())  # Makes it a list of locations by light
    verbose("Lights and locations (in order) on TV array after math are: ", scaled_locations)

    # This section assigns light locations to variable light1,2,3...etc. in JSON order
    avg_size = video_width / 2 + video_height / 2
    verbose('Average size is: ', avg_size)

    breadth = .15  # approx percent of the screen outside the location to capture
    dist = int(breadth * avg_size)  # proportion of the pixels we want to average around in relation to the video size
    verbose('Distance from relative location is: ', dist)

    global coords  # dict of coordinates
    global bounds  # dict of bounds for each coord, each item is formatted as [top, bottom, left, right]

    # initialize the dicts
    coords = {}
    bounds = {}
    for light, coordinates in scaled_locations:
        coords[light] = coordinates
        bound = [coordinates[2] - dist, coordinates[2] + dist, coordinates[0] - dist, coordinates[0] + dist]
        bound = list(map(int, bound))
        bound = list(map(lambda x: 0 if x < 0 else x, bound))
        bounds[light] = bound

    global rgb_colors, rgb_bytes  # array of rgb values, one for each light
    rgb_bytes = {}
    rgb_colors = {}

    # Constantly sets RGB values by location via taking average of nearby pixels
    while not stop_stream:
        for light_id, bound in bounds.items():
            area = rgb_frame[bound[0]:bound[1], bound[2]:bound[3], :]
            rgb_colors[light_id] = cv2.mean(area)


####################################
#     Send colors to Lights        #
####################################
def send_colors_to_lights():
    # Hold on for connection to bridge can be made & video capture is configured
    time.sleep(2.5)

    while not stop_stream:
        for light, rgba in rgb_colors.items():
            change_light_color(light, rgba)


####################################
#             Run script           #
####################################
def run_hue_play():
    global buffer_lock, stop_stream
    buffer_lock = threading.Lock()
    stop_stream = False

    # Section executes video input and establishes the connection stream to bridge
    try:
        try:
            threads = list()
            verbose("Starting Video Capture Setup...")
            t = threading.Thread(target=configure_rgb_frames)
            t.start()
            threads.append(t)
            time.sleep(.75)
            verbose("Starting Average image...")
            t = threading.Thread(target=average_image)
            t.start()
            threads.append(t)
            time.sleep(.25)  # Initialize and find bridge IP before creating connection
            verbose("Starting Send colors to Lights...")
            t = threading.Thread(target=send_colors_to_lights)
            t.start()
            threads.append(t)

            input("Press ENTER to stop")  # Allow us to exit easily
            stop_stream = True
            for t in threads:
                t.join()
        except Exception as e:
            print(e)
            stop_stream = True

    finally:  # Turn off streaming to allow normal function immediately
        for light in light_locations.keys():
            animation_light_off(light)
        verbose("Disabling lights color streaming")


if __name__ == "__main__":
    ####################################
    #        Init global vars          #
    ####################################
    global api, buffer_lock, stop_stream, light_locations, video_width, \
        video_height, rgb_frame, rgb_colors, rgb_bytes, coords, bounds
    # login to hue bridge
    hue_login()
    # init lights location
    init_light_locations()
    # run hue play script
    run_hue_play()
