# slack-stats
This project plots the number of occurances of each emoji used within a slack workspace. Naturally, it inputs slack workspace data; it is shown how this can be downloaded below. The script does two things separately: (1) processes the workspace data and stores the results to files and (2) plots the data using the emojis themselves as data points.

## Requirements
`pip install -r requirements.txt`

## How to use
1. `./setup-folders.sh`
2. First, you will need to fetch some data.
   * To fetch all messages sent within your Slack workspace, see https://slack.com/intl/en-no/help/articles/201658943-Export-your-workspace-data. This data needs to be put into `data/raw-data/`. Given the zip file from Slack, unzip it there and remove any non-relevant folders. There should now be one folder for each channel you have extracted.
   * To fetch the emojis you want to plot effeciently, see https://gist.github.com/lmarkus/8722f56baf8c47045621. These emoji files should be put into `emojis/`
3. Configure the `plot-config.yaml` to your liking.

Running the script: `python3 python/main.py --help` shows usage.

## Configuration
See config.yaml for user configuration.

