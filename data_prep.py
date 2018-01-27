#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Make sheriffs script a runnable file that will output a pandas df
Can be used to develop visualizations

@author: austinbrian
"""

# Imports
import pandas as pd
import numpy as np

# Load in and shape previously scraped data
def load_political_data(path1, path2):
    ct = pd.read_csv(path1, dtype={'FIPS':object})
    # ct = pd.read_csv('../sheriffs/data/ct.csv',dtype={'FIPS':object})
    pres = pd.read_csv(path2)
    # pres = pd.read_csv('../sheriffs/data/president_counties.csv')
    pres['turnout'] =  pres.total_votes/pres.people
    cols = [i for i in pres.columns]
    cols.append('fips_county')
    pres['fips_countyname_county'] = [str(i.split(',')[0])+' County'
                                  for i in pres.countyname]
    pres['state'] = [str(i.split(',')[1][1:]) for i in pres.countyname]
    if len(pres)>1:
        print("Pres loaded successfully")
    return ct,pres

def load_ilrc_data(path):
    '''
    Data provided by ILRC of their blog: https://www.ilrc.org/local-enforcement-map
    '''
    path = '../sheriffs/data/County_Imm_Map_ILRC.csv'
    ilrc = pd.read_csv(path,dtype={"GEOID - FIPS":object})
    # ilrc = pd.read_csv('../sheriffs/data/County_Imm_Map_ILRC.csv',dtype={"GEOID - FIPS":object})
    return ilrc.head()

def load_imm_data(path1,path2):
    '''
    Combines several datasets across 39 states where there is an estimate of
    the number of unauthorized immigrants in counties
    '''
    # start with county-level immigration data
    imm = pd.read_csv(path1)
    # imm = pd.read_csv('../data/State-county-unauthorized-estimates.csv')
    imm['county_split']=[i.split(',') for i in imm.County]
    imm['county_name']=[i[0] for i in imm.county_split]
    imm = imm.drop('county_split',axis=1)
    imm['countyname_split']=[i.split(' ') for i in imm.county_name]
    imm['County_UA_pop'] = [int(i.replace(',','')) for i in imm['Total Unauthorized Population']]
    imm.drop('Total Unauthorized Population',axis=1, inplace=True)
    # There's sometimes a couple of counties all together
    imm['mult_counties'] = 0
    for i,v in enumerate(imm.countyname_split):
        if v[-1] == 'Counties':
            imm.loc[i,'mult_counties'] = 1
    imm = imm.drop('countyname_split',axis=1)

    # add in the state unauthorized estimates (total amount for the whole state)
    ua_state = pd.read_csv(path2)
    # ua_state = pd.read_csv('../data/State-unauthorized-estimates.csv')
    ua_state['Statewide_UA_pop'] = [int(i.replace(',','')) for i in ua_state['Total Unauthorized Population']]
    ua_state.drop('Total Unauthorized Population',axis=1, inplace=True)

    imm_ua = pd.merge(left=imm,right=ua_state,left_on='State',right_on='State')
    if len(imm_ua)>1:
        print("Imm loaded successfully")
    return imm_ua

def combine_dfs(pres,imm_ua):
    '''
    Takes in political and immigration dfs, reshapes them
    '''
    # First step adds the state initial here
    # df1=pd.merge(left=pres, right=imm_ua[['State','State_init']], left_on='state',right_on='State_init')

    # What, what is this?
    df1 =pd.merge(left=pres,right=imm_ua,left_on=['fips_countyname_county','state'],right_on=['county_name','State_init'])
    if len(df1)>df1.iloc[:,0].nunique():
        df1 = df1.drop_duplicates(str(df1.columns[0])) # drops on FIPS code
    if len(df1)>1:
       print("Dfs combined succesfully")
    return df1

def merge_check(df, imm):
    merged_counties = [i for i in df.fips_countyname_county]
    print("{} merged".format(len(merged_counties)))
    immigration_counties = [i for i in imm.county_name]
    to_be_merged = [i for i in immigration_counties if i not in merged_counties]
    print("{} to be merged".format(len(to_be_merged)))

def add_ice_data(df,icepath):
    ice = pd.read_csv(icepath)
    ice['pct_ice']=ice.Yes/ice.All
    ice.rename(columns={'All':'total_detained','Yes':'ICE_custody','No':'No_ICE_custody'},inplace=True)
    imm = pd.merge(left=df,right=ice,how='left',left_on=['county_name','State'],
                 right_on=['County','State'])
    imm['taxpayer_turnout'] = imm.total_votes/imm.num_returns
    imm['pct_clinton'] = imm.clinton/imm.total_votes
    imm['pct_ua_pop_detained'] = imm.total_detained/imm.County_UA_pop
    imm['log_total_detained'] = np.log(imm.total_detained)
    imm.drop(['State_init','County_y'],axis=1,inplace=True)
    imm.rename(columns={'County_x':'county_state_long','State':'State_long'},inplace=True)

    # add some detention measures
    imm['dem_votes_per_custody']=imm.clinton/imm.ICE_custody

    return imm


def main():
    ct,pres = load_political_data('../sheriffs/data/ct.csv','../sheriffs/data/president_counties.csv')
    imm_ua = load_imm_data('../sheriffs/data/State-county-unauthorized-estimates.csv','../sheriffs/data/State-unauthorized-estimates.csv')
    imm = combine_dfs(pres,imm_ua)
    df = add_ice_data(imm,'../sheriffs/data/county_rollup_ice_detainees.csv')
    return df


if __name__ == "__main__":
    df = main()
    print(df.head())
    print(df.shape)
    print(df.columns)
    print(df.iloc[143, :])
