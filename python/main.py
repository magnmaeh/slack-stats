# Plotting tools
from os import stat
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Time tools
import datetime as dt

import json
import argparse

# Own functions
from getter import *

# Plotter options
start_date = dt.datetime(2021, 1, 2)
end_date = dt.datetime(2021, 6, 6)
emojis_disqualified = [ "+1" ]
nwinners = 10
npoints = 15

# Constants
cumulative_folder = "./data/sum-data/cumulative/"

def __main__():
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
        sumfiles = get_files_below("./data/sum-data/daily", ".json")

        mirror_filestructure("proc-data", files)
        process_raw_to_proc(files)
        process_proc_to_sum(files)
        process_proc_to_sum(procfiles)
        process_sum_daily_to_cumulative(sumfiles)

    elif graph:
        winners = get_winners(start_date, end_date, nwinners, emojis_disqualified)
        
        winnernames = [ '' for x in range(len(winners)) ]
        print(winners)

        for i in range(len(winners)):
            winnernames[i] = winners[i][0]

        plot_cumulative(start_date, end_date, npoints, winnernames)

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
                f.close()

def process_proc_to_sum(files):
    emojistats = dict()
    for file in files:
        [_, _, channel, filename] = get_pathinfo_from_file(file)
        
        # Format: yyyy-mm-dd.json -> yyyy-mm-dd
        date = filename.split('.')[0]

        procfile = "./data/proc-data/" + channel + "/" + filename
        with open(procfile, 'r') as f:
            emojis = json.load(f)
            f.close()
        
        if not emojistats.get(date):
            emojistats[date] = emojis
        else:
            emojistats[date] = dictionary_op(emojistats[date], emojis, add)
    
    for date in emojistats:
        filename = "./data/sum-data/daily/" + date + ".json"
        with open(filename, 'w') as f:
            jsondata = json.dumps(emojistats[date])
            f.write(jsondata)
            f.close()

def process_sum_daily_to_cumulative(sumfiles):
    sumdates = ['' for x in range(len(sumfiles))]
    for sumfile, i in zip(sumfiles, range(len(sumfiles))):
        # String: ./data/sum-data/daily/yyyy-mm-dd.json -> yyyy-mm-dd
        sumdates[i] = sumfile.split('/')[4].split('.')[0]
    
    sumfiles.sort(key=lambda sumfile: dt.datetime.strptime(sumfile.split('/')[4].split('.')[0], "%Y-%m-%d"))    
    cumulative_emojistats = [ dict() for x in range(len(sumfiles))]

    filenr = 0
    for file in sumfiles:

        # 1. Extract json from file
        with open(file, 'r') as f:
            emojistats = dict()
            emojistats = json.load(f)
            f.close()

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

def mirror_filestructure(new_subroot, files):
    if not os.path.exists("./data/" + new_subroot):
        os.mkdir("./data/" + new_subroot)
    
    for file in files:
        [_, _, channel, _] = get_pathinfo_from_file(file)
        folder_to_mirror = "./data/" + new_subroot + "/" + channel
        if not os.path.exists(folder_to_mirror):
            os.mkdir(folder_to_mirror)

def add(op1, op2):
    return op1 + op2

def sub(op1, op2):
    return op1 - op2

def dictionary_op(d1, d2, opfunc):
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

def get_json_from_path(path, discqualified_list):
    with open(path, 'r') as f:
        jsondata = json.load(f)
        for disc in discqualified_list:
            if jsondata.get(disc):
                del jsondata[disc]
        f.close()
    return jsondata

def get_winners(start_date, end_date, nwinners, disqualified):    
    end_date_string = get_datestr_from_datetime(end_date)
    start_date_string = get_datestr_from_datetime(start_date)
    end_date_datapath = cumulative_folder + end_date_string + ".json"
    start_date_datapath = cumulative_folder + start_date_string + ".json"

    # Compensate for having a start date that does not have a corresponding .json
    start_date = get_nearest_date(start_date, cumulative_folder)

    jsondata_end = get_json_from_path(end_date_datapath, disqualified)
    jsondata_start = get_json_from_path(start_date_datapath, disqualified)

    jsondata_diff = dictionary_op(jsondata_start, jsondata_end, sub)

    # Sort and return last nwinners elements
    jsondata_sorted = dict(sorted(jsondata_diff.items(), key=lambda item: item[1], reverse=True))
    items = jsondata_sorted.items()
    return list(items)[:nwinners]

###############################################################################
# Plotter functions
###############################################################################

def plot_get_steplength(start_date, end_date, npoints):
    return (end_date - start_date) / npoints

def plot_calculate_datelist(start_date, end_date, npoints):
    steplength = plot_get_steplength(start_date, end_date, npoints)
    datelist = [ dt.datetime for x in range(npoints) ]
    
    for i in range(1, npoints + 1):
        date = start_date + i * steplength
        date = dt.datetime(*date.timetuple()[:3])
        datelist[i - 1] = date

    return datelist

def get_nearest_date(date, path_prefix):
    path = path_prefix + date.strftime("%Y-%m-%d") + ".json"
    
    while not os.path.exists(path):
        date = date - dt.timedelta(1)
        path = path_prefix + date.strftime("%Y-%m-%d") + ".json"
    return [date, path]

def get_jsondata(path):
    with open(path, 'r') as f:
        jsondict = json.load(f)
        f.close()
    return jsondict


def plot_cumulative(start_date, end_date, npoints, winners):
    
    # Describes which dates we are interested in for plotting
    datelist = plot_calculate_datelist(start_date, end_date, npoints)
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
        stats_diff = dictionary_op(stat_basline, stats, sub)
        for j in range(len(winners)):
            dictstats[str(j)] = (winners[j], stats_diff.get(winners[j]))

        winner_dict[i][date] = dictstats

    imgs = get_images(winners)
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