#def layers(iyear=2006, fyear=2021, imonth=1, fmonth=12, ilat=2.5, ilon=-74., dlat=-1.5, dlon=3.0):
iyear=2006
fyear=2019
imonth=1
fmonth=12
ilat=2.5
ilon=-74.
dlat=-1.5
dlon=3.0

"""
Function LAYERS

Creates a CSV spreadsheet with parameters for each cirrus layer, from CALIOP 5 km Layer datafiles (CAL_LID_L2_05kmCLay-Standard-V4-20...Subset.hdf). The files must be in a directory organized by date in the type ../year/month/files. The layers ARE NOT filtered by temperature or altitude.

Arguments
---------
    iyear (int): initial year
    fyear (int): final year
    imonth (int): initial month
    fmonth (int): final month
    ilat (flt): starting latitude for grid
    ilon (flt): starting longitude for grid
    dlat (flt): lat spacing for grid
    dlon (flt): lon spacing for grid

Outputs
---------
    Prints number of (unfiltered) cirrus layers
    Prints number of profiles (unfiltered) with cirrus
    CSV file with the following parameters:
        year
        month
        month identification number
        day
        day-night flag
        profile identification number
        number of cirrus layers in the profile where the layer is
        layer identification number
        latitude
        longitude
        i,j coordinates of a grid (beginning in ilat-ilon and with spacings dlat-dlon)
        CAD score of the cirrus layer
        base altitude (km)
        top altitude (km)
        tropopause altitude (km)
        base temperature (°C)
        top temperature (°C)
        cloud optical depth
        cloud optical depth uncertainty
        minimum laser energy of CALIOP
        single-shot layers energy
    
History:
    2022-07-21: Script created by Ben-hur M. P.

"""

import numpy as np
from pyhdf import SD
import importlib
import os
import vfm_type
import pandas as pd
importlib.reload(vfm_type)

# variables for cirrus clouds
lyr_yrs = []         # years
lyr_mnths = []       # months
lyr_mnth_n = []      # month number
lyr_days = []        # days
lyr_dn = []          # day/night flag
lyr_prof_n = []      # profile's identification number
lyr_cad = []         # CAD score
lyr_mle = []         # laser energy
lyr_extqc = []       # extinction QC value
lyr_ftype = []       # feature type
lyr_ftype_qa = []    # feature type QA
lyr_ctype = []       # cloud (sub)type
lyr_ctype_qa = []    # cloud (sub)type QA
lyr_phase = []       # ice/water phase
lyr_phase_qa = []    # ice/water phase QA
lyr_i = []           # grid latitude index
lyr_j = []           # grid longitude index
lyr_bases = []       # base altitudes
lyr_tops = []        # top altitudes
lyr_tropps = []      # tropopause altitudes
lyr_tempbase = []    # base temperatures
lyr_temptop = []     # top temperatures
lyr_nlyrs = []       # number of layers for a specific profile
lyr_n = []           # layer number in the netcdf file
lyr_lats = []        # latitudes
lyr_lons = []        # longitudes
lyr_hres = []        # horizontal resolutions
lyr_od = []          # optical depth
lyr_od_unc = []      # optical depth uncertainty

month_number = 0 # month identification number in the whole dataset, ranging from 0 to N-1, where N is the total number of months
profile_id = 0 # profile identification number in the whole dataset, ranging from 0 to P-1, where P is the total number of profiles
total_profiles = 0 # variable to know the total number of profiles (really necessary?)


# looping over all years
for year in range(iyear, fyear+1):

    year = str(year)
    print('Year: '+year)
    
    start_month = 6 if year=='2006' else imonth # if the year is 2006, begin with month 6
    final_month = 3 if year=='2021' else fmonth # if the year is 2006, ends with month 3
    
    # looping over all months in that year
    for month in range(start_month, final_month+1):
    
        month = str(month)
        print('Month: '+month)
        
        # access the directory where the data is stored
        dirs = list(os.walk('data/'+year+'/'+month+'/'))[0]
        # dirs[0] = 'data/2011/1/' (exemplo)
        # dirs[1] = []
        # dirs[2] = lista com nome dos arquivos
        files = dirs[2] # picks up the file names
        
        for filen in files:
            
            # navigates through the directory and get the data
            filedata = 'data/'+year+'/'+month+'/'+filen
            h4sd = SD.SD(filedata)
            
            # gets the data
            sds = h4sd.select('Feature_Classification_Flags').get()
            
            # gets Feature Type flag data
            ftype = vfm_type.vfm_type(sds, 'type')['Data']
            # gets Feature Type QA flag data
            ftypeqa = vfm_type.vfm_type(sds, 'typeqa')['Data']
            # gets Cloud flag data
            ctype = vfm_type.vfm_type(sds, 'cloud')['Data']
            # gets Cloud Subtype QA flag data
            ctype_qa = vfm_type.vfm_type(sds, 'subtypeqa')['Data']
            # gets Ice/Water phase flag data
            clyphase = vfm_type.vfm_type(sds, 'phase')['Data']
            # gets Ice/Water phase QA flag data
            phase_qa = vfm_type.vfm_type(sds, 'phaseqa')['Data']
            
            # layer mask
            #cirrusmask = (cad_score>=70) & (cad_score<=100) & ((extqc==0) | (extqc==1) | (extqc==2) | (extqc==16) | (extqc==18)) & (ftype==2) & (ctype==6) & ((clyphase==1) | (clyphase==3)) & (phase_qa==3) & (ftypeqa==4)
            cirrusmask = (ftype>=0)
            # ftype == 2: only clouds
            # ctype == 6: only cirrus
            # clyavg >= 3: horizontal averaging of 5 km, 20 km and 80 km, used for identification of layers
            # extqc <= 1: extinction factor secure for use in the layer detection
            
            if (cirrusmask==False).all(): # if there is no cirrus in the whole file, pass
            
                pass
                
            else:
                
                # gets values of other variables
                latitude = h4sd.select('Latitude').get()[:,1]
                longitude = h4sd.select('Longitude').get()[:,1]
                tropopause = h4sd.select('Tropopause_Height').get().flatten()
                cad_score = h4sd.select('CAD_Score').get()*1
                cbase = h4sd.select('Layer_Base_Altitude').get()*1
                ctop = h4sd.select('Layer_Top_Altitude').get()*1
                cod = h4sd.select('Feature_Optical_Depth_532').get()*1
                cod_unc = h4sd.select('Feature_Optical_Depth_Uncertainty_532').get()*1
                ctempbase = h4sd.select('Layer_Base_Temperature').get()*1
                ctemptop = h4sd.select('Layer_Top_Temperature').get()*1
                time = h4sd.select('Profile_UTC_Time').get()*1
                mle = (h4sd.select('Minimum_Laser_Energy_532').get()*1)[:,0]
                extqc = (h4sd.select('ExtinctionQC_532').get()*1)
                h_res = h4sd.select('Horizontal_Averaging').get()*1
                
                # gets only the decimal part of the time array
                time = time - np.fix(time)
                
                # picks up indexes where the new cirrusmask is set to True
                profiles = np.where(cirrusmask==True)[0]      # identify profiles with cirrus
                profiles = list(set(profiles))                # remove repeated profile numbers
                
                for j in profiles:   # loop over profiles
                
                    layer = 0
                
                    layers = np.where(cirrusmask[j,:]==True)[0]  # identify layers with cirrus in each profile
                
                    for k in layers:   # loop over layers of each profile
                    
                        # save the properties in its respective lists
                        lyr_yrs.append( int(year) )
                        lyr_mnths.append( int(month) )
                        lyr_mnth_n.append( month_number )
                        lyr_days.append( int(filen[43:45]) )
                        lyr_dn.append( filen[55] )
                        lyr_lats.append( latitude[j] )
                        lyr_lons.append( longitude[j] )
                        lyr_i.append( np.floor((latitude[j] - ilat)/dlat) )
                        lyr_j.append( np.floor((longitude[j] - ilon)/dlon) )
                        lyr_mle.append( mle[j] )
                        lyr_prof_n.append( profile_id )
                        lyr_nlyrs.append( len(layers) )
                        lyr_n.append( layer )
                        lyr_cad.append( cad_score[j,k] )
                        lyr_extqc.append( extqc[j,k] )
                        lyr_ftype.append( ftype[j,k] )
                        lyr_ftype_qa.append( ftypeqa[j,k] )
                        lyr_ctype.append( ctype[j,k] )
                        lyr_ctype_qa.append( ctype_qa[j,k] )
                        lyr_phase.append( clyphase[j,k] )
                        lyr_phase_qa.append( phase_qa[j,k] )
                        lyr_hres.append( h_res[j,k] )
                        lyr_bases.append( cbase[j,k] )
                        lyr_tops.append( ctop[j,k] )
                        lyr_tropps.append( tropopause[j] )
                        lyr_tempbase.append( ctempbase[j,k] )
                        lyr_temptop.append( ctemptop[j,k] )
                        lyr_od.append( cod[j,k] )
                        lyr_od_unc.append( cod_unc[j,k] )
                        
                        layer += 1
                    
                    profile_id += 1 # increments 1 in the profile ID
            
            total_profiles += len(sds[:,0]) # increments the number of profiles in the total_profiles variable
        
        month_number += 1 # increments 1 in the month number

# creates the dataframe for the properties
df = pd.DataFrame(list(zip(*[lyr_yrs, lyr_mnths, lyr_mnth_n, lyr_days, lyr_dn, lyr_lats, lyr_lons, lyr_i, lyr_j, lyr_mle, lyr_prof_n, lyr_nlyrs, lyr_n, lyr_cad, lyr_extqc, lyr_ftype, lyr_ftype_qa, lyr_ctype, lyr_ctype_qa, lyr_phase, lyr_phase_qa, lyr_hres, lyr_bases, lyr_tops, lyr_tropps, lyr_tempbase, lyr_temptop, lyr_od, lyr_od_unc])))

# creates list with the correct titles for dataframe's header
header = ['year', 'month', 'month_number', 'day', 'day_night', 'latitude', 'longitude', 'i' , 'j', 'min_laser_energy', 'profile', 'layers_in_profile', 'layer_number', 'cad', 'extinction_qc', 'feature_type', 'feature_type_qa', 'cloud_type', 'cloud_type_qa', 'phase', 'phase_qa', 'hor_resolution', 'base_altitude', 'top_altitude', 'tropopause_altitude', 'base_temperature', 'top_temperature', 'optical_depth', 'opt_depth_unc']

# applies dataframe's header list
df.columns = header

# save datafrave as a csv sheet
df.to_csv('layers_all.csv', index=False)


