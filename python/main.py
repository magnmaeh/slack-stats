# Utility libraries
import datetime as dt
import yaml
import json
import argparse

# Plotting tools
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Own functions
from getter import *


configfile = 'plot-config.yaml'
cumulative_folder = "./data/sum-data/cumulative/"
datetime_format = '%Y-%m-%d'

###############################################################################
# Yaml configuration import
###############################################################################
with open (configfile, 'r') as f:
    config = yaml.full_load(f)
    
    def yamldate_to_datetime(yamldate):
        return dt.datetime(
            yamldate['year'],
            yamldate['month'],
            yamldate['day']
        )

    startdate = yamldate_to_datetime(config['startdate'])
    enddate = yamldate_to_datetime(config['enddate'])
    
    emojis_disqualified = config['disqualified']
    nwinners = config['nwinners']
    npoints = config['npoints']

###############################################################################
# Main
###############################################################################
def __main__():
    if not helper_validate_period(startdate, enddate):
        exit(1)
    
    parser = argparse.ArgumentParser(description="Process and plot data based on Slack data.")
    parser.add_argument("-p", "--preprocess", action="store_true", help="Preprocess data and store to files.")
    parser.add_argument("-g", "--graph", action="store_true", help="Graph data based on preprocessing.")
    args = vars(parser.parse_args())

    preprocess = args["preprocess"]
    graph = args["graph"]

    if not preprocess and not graph:
        parser.print_help()
        exit(1)

    elif preprocess:
        files = get_files_below("./data/raw-data", ".json")
        procfiles = get_files_below("./data/proc-data/", ".json")
        daily_sumfiles = get_files_below("./data/sum-data/daily", ".json")

        helper_mirror_filestructure("./data/proc-data", "./data/raw-data")
        process_raw_to_proc(files)
        process_proc_to_sum(files)
        process_proc_to_sum(procfiles)
        process_sum_daily_to_cumulative(daily_sumfiles)

    elif graph:
        winners = helper_get_winners(startdate, enddate, nwinners, emojis_disqualified)
        helper_print_winnners(winners)
        
        winnernames = [ '' for x in range(len(winners)) ]

        for i in range(len(winners)):
            winnernames[i] = winners[i][0]

        plot_cumulative(startdate, enddate, npoints, winnernames)

    else:
        parser.print_help()
        exit(1)

###############################################################################
# Processor functions
###############################################################################

def process_raw_to_proc(files):
    for file in files:
        emojis = get_emojis_from_file(file)
        [_, _, channel, filename] = get_pathinfo_from_file(file)
        filepath = "./data/proc-data/" + channel + "/" + filename

        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                jsondata = json.dumps(emojis)
                f.write(jsondata)

def process_proc_to_sum(files):
    emojistats = dict()
    for file in files:
        [_, _, channel, filename] = get_pathinfo_from_file(file)
        
        # Format: yyyy-mm-dd.json -> yyyy-mm-dd
        date = filename.split('.')[0]

        procfile = "./data/proc-data/" + channel + "/" + filename
        with open(procfile, 'r') as f:
            emojis = json.load(f)
        
        if not emojistats.get(date):
            emojistats[date] = emojis
        else:
            emojistats[date] = helper_dictionary_op(emojistats[date], emojis, add)
    
    for date in emojistats:
        filename = "./data/sum-data/daily/" + date + ".json"
        with open(filename, 'w') as f:
            jsondata = json.dumps(emojistats[date])
            f.write(jsondata)

def process_sum_daily_to_cumulative(sumfiles):
    sumdates = ['' for x in range(len(sumfiles))]
    for sumfile, i in zip(sumfiles, range(len(sumfiles))):
        # String: ./data/sum-data/daily/yyyy-mm-dd.json -> yyyy-mm-dd
        sumdates[i] = sumfile.split('/')[4].split('.')[0]
    
    sumfiles.sort(key=lambda sumfile: dt.datetime.strptime(sumfile.split('/')[4].split('.')[0], datetime_format))    
    cumulative_emojistats = [ dict() for x in range(len(sumfiles))]

    filenr = 0
    for file in sumfiles:

        # 1. Extract json from file
        with open(file, 'r') as f:
            emojistats = dict()
            emojistats = json.load(f)

        # 2. Deepcopy it into a new dictionary
        cumulative_emojistats[filenr] = emojistats
        
        # 3. Add the previous dictionary values to the new dictionary
        for emoji in cumulative_emojistats[filenr - 1]:
            if cumulative_emojistats[filenr].get(emoji):
                cumulative_emojistats[filenr][emoji] += cumulative_emojistats[filenr - 1][emoji]
            else:
                cumulative_emojistats[filenr][emoji]  = cumulative_emojistats[filenr - 1][emoji]

        # 4. Write the dictionary to file
        [_, _, _, date] = get_pathinfo_from_file(file)
        filepath = cumulative_folder + date
        with open(filepath, 'w') as f:
            jsondata = json.dumps(cumulative_emojistats[filenr])
            f.write(jsondata)

        # 5. Repeat
        if emojistats:
            filenr += 1

    return cumulative_emojistats

###############################################################################
# Helper functions
###############################################################################

def helper_mirror_filestructure(new_structure, old_structure):
    """"
    This is a specific helper function that when after run guarantees some
    the necessary file structure is present under the first argument. It only
    mirrors the folders and not the files.

    It only copies at one depth level because that is what this program needs.
    In thats sense it is not very general.
    """
    
    subfolders = [x[0] for x in os.walk(old_structure)]
    for entry in subfolders:
        if get_depth_from_path(entry) == 2:
            entry = new_structure
        else:
            entry_split = entry.split('/')
            new_structure_split = new_structure.split('/')
            entry_split[2] = new_structure_split[2]
            entry = "/".join(entry_split)
        if not os.path.exists(entry):
            os.mkdir(entry)

def helper_find_minimum_date(folder, enddate):
    mindate = enddate
    subfolders = [x[0] for x in os.walk(folder)]
    for subfolder in subfolders:
        files = os.listdir(subfolder)
        for file in files:
            if os.path.isfile(subfolder + '/' + file):
                date = get_datetime_from_filename(file, datetime_format)
                if date < mindate:
                    mindate = date
    return mindate

def helper_validate_period(startdate, enddate):
    if startdate > enddate:
        print(configfile + ": The start date cannot be greater than the end date.")
        return False
    else:
        mindate = helper_find_minimum_date('./data/raw-data', enddate)
        if startdate < mindate:
            print(configfile + ": The start date is less than the minimum date "
                "found in raw files." 
                "\nStart date:         " + startdate.strftime(datetime_format) + 
                "\nMinimum date found: " + mindate.strftime(datetime_format))
            return False
        else:
            return True

def add(op1, op2):
    return op1 + op2

def sub(op1, op2):
    return op1 - op2

def helper_dictionary_op(d1, d2, opfunc):
    sum = dict()

    for e1 in d1:
        if not sum.get(e1):
            sum[e1] = d1[e1]
        else:
            sum[e1] = opfunc(d1[e1], sum[e1])
    
    for e2 in d2:
        if not sum.get(e2):
            sum[e2] = d2[e2]
        else:
            sum[e2] = opfunc(d2[e2], sum[e2])
    return sum

def helper_get_json_from_path(path, discqualified_list):
    with open(path, 'r') as f:
        jsondata = json.load(f)
        for disc in discqualified_list:
            if jsondata.get(disc):
                del jsondata[disc]
    return jsondata

def helper_get_winners(startdate, enddate, nwinners, disqualified):    
    enddate_string = get_datestr_from_datetime(enddate)
    startdate_string = get_datestr_from_datetime(startdate)
    enddate_datapath = cumulative_folder + enddate_string + ".json"
    startdate_datapath = cumulative_folder + startdate_string + ".json"

    # Compensate for having a start date that does not have a corresponding .json
    startdate = get_nearest_date(startdate, cumulative_folder)

    jsondata_end = helper_get_json_from_path(enddate_datapath, disqualified)
    jsondata_start = helper_get_json_from_path(startdate_datapath, disqualified)

    jsondata_diff = helper_dictionary_op(jsondata_start, jsondata_end, sub)

    # Sort and return last nwinners elements
    jsondata_sorted = dict(sorted(jsondata_diff.items(), key=lambda item: item[1], reverse=True))
    items = jsondata_sorted.items()
    return list(items)[:nwinners]

def helper_print_winnners(winners):
        longestwinnerstr = 0
        for winner in winners:
            winnerstr = winner[0]
            if len(winnerstr) > longestwinnerstr:
                longestwinnerstr = len(winnerstr)
        print("Winners are:")
        for winner in winners:
            print(winner[0].ljust(longestwinnerstr) + " :", str(winner[1]))

###############################################################################
# Plotter functions
###############################################################################

def plot_get_steplength(startdate, enddate, npoints):
    return (enddate - startdate) / npoints

def plot_calculate_datelist(startdate, enddate, npoints):
    steplength = plot_get_steplength(startdate, enddate, npoints)
    datelist = [ dt.datetime for x in range(npoints) ]
    
    for i in range(1, npoints + 1):
        date = startdate + i * steplength
        date = dt.datetime(*date.timetuple()[:3])
        datelist[i - 1] = date

    return datelist

def get_nearest_date(date, path_prefix):
    path = path_prefix + date.strftime(datetime_format) + ".json"
    
    while not os.path.exists(path):
        date = date - dt.timedelta(1)
        path = path_prefix + date.strftime(datetime_format) + ".json"
    return [date, path]

def get_jsondata(path):
    with open(path, 'r') as f:
        jsondict = json.load(f)
    return jsondict


def plot_cumulative(startdate, enddate, npoints, winners):
    
    # Describes which dates we are interested in for plotting
    datelist = plot_calculate_datelist(startdate, enddate, npoints)
    datelist_paths = [ '' for x in range(npoints) ]
    
    for i in range(npoints):        
        [ datelist[i], datelist_paths[i] ] = get_nearest_date(datelist[i], cumulative_folder)

    # Fetch the necessary data for each of the winners
    winner_dict = [ dict() for x in range(len(datelist)) ]
    
    for date, i in zip(datelist, range(len(datelist))):
        dictstats = dict()
        if i == 0:
            stat_basline = get_jsondata(datelist_paths[i])
            stats = stat_basline
        else:
            stats = get_jsondata(datelist_paths[i])
        stats_diff = helper_dictionary_op(stat_basline, stats, sub)
        for j in range(len(winners)):
            dictstats[str(j)] = (winners[j], stats_diff.get(winners[j]))

        winner_dict[i][date] = dictstats

    imgs = get_images(winners)
    if not imgs:
        exit(1)

    _, ax = plt.subplots()
    for datestat, i in zip(winner_dict, range(len(winner_dict))):
        winstats = datestat[datelist[i]]
        for winner, img in zip(winstats, imgs):
            winner_occurance = winstats[winner][1]
            
            if not winner_occurance:
                continue
            
            datestr = get_datestr_from_datetime(datelist[i])
            ax.plot(datestr, winner_occurance)
            plot_images(datestr, winner_occurance, img, ax, 3500)
        
    plt.grid(True)
    plt.show()

def plot_images(x, y, image, ax, size):
    area = image.shape[0] * image.shape[1]
    sz = area ** (1/2)
    im = OffsetImage(image, zoom=size/sz/ax.figure.dpi)
    im.image.axes = ax

    ab = AnnotationBbox(im, (x, y), frameon=False, pad=0.0)

    ax.add_artist(ab)

if __name__ == "__main__":
    __main__()