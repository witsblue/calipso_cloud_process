def profiles(iyear=2006, fyear=2021, imonth=1, fmonth=12, ilat=2.5, ilon=-74., dlat=-1.5, dlon=3.0):
    """
    Function PROFILES
    
    Creates a CSV spreadsheet with parameters for each profile, from CALIOP 5 km Layer datafiles (CAL_LID_L2_05kmCLay-Standard-V4-20...Subset.hdf). The files must be in a directory organized by date in the type ../year/month/files. The cirrus layers ARE filtered by temperature (T_top<-37 °C) and altitude (H_base>8 km).
    
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
        Prints number of profiles with (unfiltered) cirrus over the total of profiles
        TXT file listing datafiles with cirrus
        TXT file listing datafiles without cirrus
        CSV file with the following parameters:
            year
            month
            month identification number
            day
            day-night flag
            latitude
            longitude
            i,j coordinates of a grid (beginning in ilat-ilon and with spacings dlat-dlon)
            CAD s
            tropopause altitude (km)
            number of cirrus layers
            lowest base altitude (of cirrus, if exists)
            highest top altitude (of cirrus, if exists)
            sum of the cloud optical depth
            cloud of the geometric thickness
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
    yrs = []        # years
    mnths = []      # months
    mnth_n = []     # month number
    days = []       # days
    dn = []         # day/night flag
    lats = []       # latitudes
    lons = []       # longitudes
    lat_i = []      # grid latitude index
    lon_j = []      # grid longitude index
    tropps = []     # tropopause height
    ci_nlyrs = []   # number of cirrus layers
    lwst_base = []  # lowest cloud base
    hgst_top = []   # highest cloud top
    sum_cod = []    # sum of cirrus optical depths
    sum_tcknss = [] # sum of cirrus geometric thicknesses
    mle = []        # minimum laser energy

    # lists of files
    files_w_cirrus = []     # list of files containing cirrus clouds
    files_wo_cirrus = []    # list of files without cirrus clouds

    month_number = 0 # month identification number in the whole dataset, ranging from 0 to N-1, where N is the total number of months

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
            # dirs[0] = 'data/2011/1/' (example)
            # dirs[1] = []
            # dirs[2] = list with filenames
            files = dirs[2] # picks up the file names
                
            for filen in files:
            
                # navigates through the directory and get the data
                filedata = dirs[0]+filen
                h4sd = SD.SD(filedata)
                
                # gets data
                sds = h4sd.select('Feature_Classification_Flags').get()
                cbase = h4sd.select('Layer_Base_Altitude').get()*1
                ctemptop = h4sd.select('Layer_Top_Temperature').get()*1
                cad_score = h4sd.select('CAD_Score').get()*1
                extqc = h4sd.select('ExtinctionQC_532').get()
                min_le = (h4sd.select('Minimum_Laser_Energy_532').get()*1)[:,0]
                
                # gets Feature Type flag data
                ftype = vfm_type.vfm_type(sds, 'type')['Data']
                # gets Feature Type QA flag data
                ftypeqa = vfm_type.vfm_type(sds, 'typeqa')['Data']
                # gets Cloud flag data
                ctype = vfm_type.vfm_type(sds, 'cloud')['Data']
                # gets Cloud Subtype QA flag data
                ctype_qa = vfm_type.vfm_type(sds, 'subtypeqa')['Data']
                # gets Ice/Water phase flag data
                phase = vfm_type.vfm_type(sds, 'phase')['Data']
                # gets Ice/Water phase QA flag data
                phase_qa = vfm_type.vfm_type(sds, 'phaseqa')['Data']
                
                # gets latitude, longitude and tropopause height
                latitude = h4sd.select('Latitude').get()[:,1]
                longitude = h4sd.select('Longitude').get()[:,1]
                tropopause = h4sd.select('Tropopause_Height').get().flatten()
                
                # cirrus mask
                cirrusmask = (cad_score>=70) & (cad_score<=100) & ((extqc==0) | (extqc==1) | (extqc==2) | (extqc==16) | (extqc==18)) & (ftype==2) & (ctype==6) & ((phase==1) | (phase==3)) & (phase_qa==3) & (ftypeqa==4) & (cbase>=8) & (ctemptop<=-37)
                # ftype == 2: only clouds
                # cad_score >= 70: high confidence in identifying as "cloud" (according to the CAD Score)
                # ctype == 6: only cirrus
                # clyavg >= 3: horizontal averaging of 5 km, 20 km and 80 km, used for identification of layers
                # cbase > 8: base altitude higher than 8 km
                # ctemptop < -37: top temperature less than -37 °C
                # extqc <= 1: extinction factor secure for use in the layer detection
                
                for j in range(len(latitude)): # loop over all profiles
                
                    # save the properties in its respective lists
                    yrs.append( int(year) )
                    mnths.append( int(month) )
                    mnth_n.append( month_number )
                    days.append( int(filen[43:45]) )
                    dn.append( filen[55] )
                    lats.append( latitude[j] )
                    lons.append( longitude[j] )
                    lat_i.append( np.floor((latitude[j] - ilat)/dlat) )
                    lon_j.append( np.floor((longitude[j] - ilon)/dlon) )
                    tropps.append( tropopause[j] )
                    ci_nlyrs.append( np.count_nonzero(cirrusmask[j,:] == True) )
                    mle.append( min_le[j] )
                    
                    if ci_nlyrs[-1] != 0: # if there is any cirrus layer in that profile
                        
                        # get arrays of layer top altitude and cod
                        ctop = h4sd.select('Layer_Top_Altitude').get()*1
                        cod = h4sd.select('Feature_Optical_Depth_532').get()*1

                        bases = cbase[j,:][cirrusmask[j,:]==True]   # array with base altitudes
                        tops = ctop[j,:][cirrusmask[j,:]==True]     # array with top altitudes
                        cods = cod[j,:][cirrusmask[j,:]==True]      # array with cirrus optical depths
                        tcknss = tops - bases                       # array with thicknesses
                                            
                        lwst_base.append( min(bases) )  # gets lowest base altitude in the profile
                        hgst_top.append( max(tops) )    # gets highest top altitude in the profile
                        sum_cod.append( sum(cods) )     # gets the sum of cod over the profile (only cirrus)
                        sum_tcknss.append( sum(tcknss) ) # gets the sum of thickness over the profile (only cirrus)
                        
                    else: # if there are no cirrus layers in the profile
                        
                        lwst_base.append(0)
                        hgst_top.append(0)
                        sum_cod.append(0)
                        sum_tcknss.append(0)
                
                if (cirrusmask==False).all(): # if there is no cirrus in the whole file, add file name to list of files without cirrus
                
                    files_wo_cirrus.append(filen)
                    
                else:
                
                    files_w_cirrus.append(filen) # if there is any cirrus in the file, add file name to list of files with cirrus
            
            month_number += 1 # increments 1 in the month number

    # creates the dataframe for the properties
    df = pd.DataFrame(list(zip(*[yrs, mnths, mnth_n, days, dn, lats, lons, lat_i, lon_j, tropps, ci_nlyrs, lwst_base, hgst_top, sum_cod, sum_tcknss, mle])))

    # creates list with the correct titles for dataframe's header
    header = ['year', 'month', 'month_number', 'day', 'day_night','latitude', 'longitude', 'i', 'j', 'tropopause_height', 'cirrus_layers', 'lowest_base', 'highest_top', 'sum_opt_depth', 'sum_geom_thickness', 'min_laser_energy']

    # applies dataframe's header list
    df.columns = header
    # save datafrave as a csv sheet
    df.to_csv('output/profiles.csv', index=False)

    np.savetxt('output/files_with_cirrus.txt', files_w_cirrus, fmt='%s')
    np.savetxt('output/files_without_cirrus.txt', files_wo_cirrus, fmt='%s')

    print('DONE')
    print('Number of profiles with cirrus: {} / {}'.format(np.count_nonzero(ci_nlyrs), len(yrs)))
