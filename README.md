# CALIOP Cloud Layer processing
In this repository, two data processing scripts are provided to extract data from CALIOP 5 km Layer products. Both scripts are considered for the product `CAL_LID_L2_05kmCLay-Standard-V4-20...Subset.hdf`.

## Layer processing script
The first script, [layers_all.py](https://github.com/witsblue/calipso_cloud_process/blob/main/layers_all.py), is dedicated to create a dataset containing information about all the the layers identified as cirrus cloud. In the CALIOP product, all layers have data on coordinates, altitude, CAD (cloud/aerosol classification) score, cloud optical depth (COD), QA classification and others parameters. The details about classification of the layers can be found [here](https://hal.science/hal-05505617v1/file/cal_lid_l2_vfm_v5-00_desc_qs.pdf) The script filters the layers for cirrus clouds and gather informations associated with it, corresponding to the time period determined by the user, and also incoporates a pair of indices i-j to the layer related to a arbitrary spatial grid beginning in a specific location (ilat, ilon). The resulting CSV file (`layers_all.csv`) will have the following information:
- Year
- Month
- Day
- Day/Night flag
- Latitude
- Longitude
- i coordinate, refering to the arbitrary spatial grid
- j coordinate, refering to the arbitrary spatial grid
- Minimum laser energy
- Profile number
- Number of layers in the respective profile
- Layer number
- CAD score
- Extinction QC
- Feature type
- Feature type QA
- Cloud type
- Cloud type QA
- Phase of the layer
- Phase's QA
- Horizontal resolution
- Altitude of the layer's base
- Altitude of the layer's top
- Altitude of the tropopause
- Base's temperature
- Top's temperature
- Optical depth
- Optical depth's uncertainty

## Profile processing script
The second script, [profiles.py](https://github.com/witsblue/calipso_cloud_process/blob/main/profiles.py), is destinated to process profile data gathered from CALIOP's product. As in the layers_all.py script, this one will consider the time period defined by the user, selecting all profiles found in the product and process the data countained in them, and also incorporating a pair of i-j indices associated to an arbitrary grid. The resulting CSV file (`profiles.csv`) will countain all profiles and data about the cirrus layers found in the profiles (if any), considering a set of classification parameters (CAD score, extinction QC, feature and cloud types, phase type). In this processing, cirrus layers with base altitude above 8 km and top temperature below -37 °C were considered. The information present in the CSV is listed below:
- Year
- Month
- Month number
- Day
- Day/Night flag
- Latitude
- Longitude
- i coordinate, refering to the arbitrary spatial grid
- j coordinate, refering to the arbitrary spatial grid
- Tropopause height
- Number of cirrus layers in the profile
- Base's altitude of the lowest cirrus layer (if any)
- Top's altitude of the highest cirrus layer (if any)
- Sum of the COD from all cirrus layers in the profile
- Sum of the geometrical thickness from all cirrus in the profile
- Mininum laser energy

Refference: [https://doi.org/10.1016/j.atmosres.2023.107167](https://doi.org/10.1016/j.atmosres.2023.107167)

Contact: benhurmarpor@gmail.com
