"""
This module downloads the grib file from the opendata server and extracts the data
"""

from itertools import product
import json
import os.path
import subprocess
from time import localtime
import requests


def download_grib_file(url: str, dest_folder: str):
    """Downloads the grib file

    Args:
        url (str): url with the file at the ending
        dest_foler (str): dir where file should be saved
    """
    if not os.path.exists(dest_folder):
        raise FileNotFoundError("Directory doesn't exist, script wont make on automatically")

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    #TODO: how does requests work
    req = requests.get(url, stream=True, timeout=30)
    if req.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as grib_file:
            for chunk in req.iter_content(chunk_size=1024 * 8):
                if chunk:
                    grib_file.write(chunk)
                    grib_file.flush()
                    os.fsync(grib_file.fileno())
    else:  # HTTP status code 4XX/5XX
        print(f"Download failed: status code {req.status_code}\n{req.text}")


def download_whole_day(dest_folder: str):
    """Downloads a whole day from the OpenData DWD Server

    Args:
        dest_folder (str): destination of the directory
    """
    url_to_icond2 = "http://opendata.dwd.de/weather/nwp/icon-d2/grib"
    models = ("icosahedral_model-level", "icosahedral_pressure_level",
              "regular-lat-lon_model-level", "regular-lat-lon_pressure-level")
    time_stamps = ("/00", "/03", "/06", "/09", "/12", "/15", "/18", "/21")
    pressure_levels = [200, 250, 300, 400, 500, 600, 700, 850, 950, 975, 1000]  # hPa
    standard_half_heights = [22000.000, 19401.852, 18013.409, 16906.264, 15958.169, 15118.009,
                             14358.139, 13661.439, 13016.363, 12414.654, 11850.143, 11318.068,
                             10814.653, 10336.841, 9882.112, 9448.359, 9033.796, 8636.893,
                             8256.329, 7890.952, 7539.748, 7201.825, 6876.388, 6562.725,
                             6260.200, 5968.239, 5686.321, 5413.976, 5150.773, 4896.323,
                             4650.265, 4412.272, 4182.043, 3959.301, 3743.791, 3535.279,
                             3333.549, 3138.402, 2949.656, 2767.143, 2590.708, 2420.213,
                             2255.527, 2096.537, 1943.136, 1795.234, 1652.748, 1515.610,
                             1383.761, 1257.155, 1135.760, 1019.556, 908.539, 802.721,
                             702.132, 606.827, 516.885, 432.419, 353.586, 280.598,
                             213.746, 153.438, 100.277, 55.212, 20.000, 0.000]
    standard_full_heights = [20700.926, 18707.630, 17459.836, 16432.216, 15538.089, 14738.074,
                             14009.789, 13338.901, 12715.508, 12132.398, 11584.105, 11066.360,
                             10575.747, 10109.477, 9665.235, 9241.077, 8835.344, 8446.611,
                             8073.640, 7715.350, 7370.787, 7039.106, 6719.557, 6411.462,
                             6114.219, 5827.280, 5550.148, 5282.374, 5023.548, 4773.294,
                             4531.269, 4297.157, 4070.672, 3851.546, 3639.535, 3434.414,
                             3235.976, 3044.029, 2858.399, 2678.926, 2505.461, 2337.870,
                             2176.032, 2019.836, 1869.185, 1723.991, 1584.179, 1449.686,
                             1320.458, 1196.457, 1077.658, 964.048, 855.630, 752.427,
                             654.479, 561.856, 474.652, 393.002, 317.092, 247.172,
                             183.592, 126.857, 77.745, 37.606, 10.000]
    fields = ("/u", "/v", "/w")
    number_of_flight_levels = 65

    year, month, day, *useless = localtime()
    # del useless
    today = f"{year}{month}{day}"

    bz2_file_begin = "/icon-d2_germany"
    bz2_file_end = ".grib2.bz2"

    for model, time_stamp, field in product(models, time_stamps, fields):
        # path_to_dest_folder = fr"{dest_folder}{time_stamp}{field}"
        path_to_dest_folder = os.path.join(dest_folder, time_stamp, field)
        #TODO: wrong number, how iterate
        for i in range(5):
            for j in range(65):
                bz2_file = f"{bz2_file_begin}_{model}_{today}{time_stamp[1:]}_00{i}_{j}_{field[1:]}{bz2_file_end}"
                url_to_bz2_file = url_to_icond2.join((time_stamp, field, bz2_file))
                download_grib_file(url_to_bz2_file, path_to_dest_folder)


def extract_grib_data(path_to_grib_file: str):
    """Grib data is downloaded in .bz2 files. Extracting is necessary

    Args:
        grib_file (str): path to grib file
    """
    pass


def dump_grib_data(path_to_file: str):
    """Dump grib data with eccodes functions

    Args:
        path_to_file (str): path to file (with the file name at the end)
    """
    file_name = os.path.basename(os.path.normpath(path_to_file))
    grib_stdout = subprocess.run(["grib_dump", "-j", file_name], capture_output=True, text=True, check=True)
    d = json.loads(grib_stdout)


def optimize_json(path_to_file: str):
    """Optimize json format from DWD server

    Args:
        path (str): path to json file, excluding file name
        file_name (str): file name
    """
    file_name = os.path.basename(os.path.normpath(path_to_file))
    path, file_name = os.path.split(path_to_file)
    with open(path_to_file, "r", encoding="utf8") as json_file:
        json_dict = json.load(json_file)
        amount_of_messages = len(json_dict["messages"][0])
        json_obj = json_dict["messages"][0]
        new_json = {json_obj[i]["key"]: json_obj[i]["value"] for i in range(amount_of_messages)}

    name = file_name[:-5]
    end = file_name[-5:]

    with open(os.path.join(path, fr"{name}_new{end}"), "w", encoding="utf8") as new_json_file:
        json.dump(new_json, new_json_file, indent=4)


def main():
    """For testing and debugging purposes"""
    path_to_model = os.path.join(os.path.expanduser("~"),
                                 "Dokumente", "_TU", "Bachelor", "DWD", "icond-d2")
    path_to_model = os.path.join(path_to_model, "00", "u")
    url = r"http://opendata.dwd.de/weather/nwp/icon-d2/grib/00/u"
    file_name = r"/icon-d2_germany_regular-lat-lon_model-level_2022111400_000_10_u.grib2.bz2"
    download_grib_file(url.join(file_name), path_to_model)
    download_whole_day(path_to_model)


if __name__ == "__main__":
    main()