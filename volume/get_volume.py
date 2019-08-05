import pandas as pd
import ifcb

# first read in data to get all_samples
samples = pd.read_csv("level_1b.csv", usecols=['permalink'])

# separate out roi id from permalink
samples['roi'] = samples['permalink']
samples.roi = samples.roi.str.slice(68, 74)
# gets rid of leading zeros
samples.roi = samples.roi.str.lstrip("0")
# cut permalink to just be permalink of sample
samples.permalink = samples.permalink.str.slice(0, 67)

# get unique urls to each sample
urls = samples.drop_duplicates(subset='permalink').reset_index()
urls['volume_imaged'] = 0.00
# change type to float
urls['volume_imaged'] = urls['volume_imaged'].astype('float64')
urls = urls[['permalink', 'volume_imaged']]
# get volume imaged of each sample
counter = 0
for row in urls.iterrows():
    pid = urls.permalink[counter]
    url = '{}.html'.format(pid)
    # use sample bin to grab ml analyzed
    with ifcb.open_url(url, images=False) as sample_bin:
        urls.volume_imaged[counter] = float(sample_bin.ml_analyzed)
        counter += 1
# output as a csv to be read in later
urls.to_csv('volumes.csv', index=None, header=True)
