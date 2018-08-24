#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 6 10:30:41 2018

@author: hannah + eion
"""
import requests
import pandas as pd

# constants
CENSUS_API_KEY = "36ff0f593ede962a47e6e53c530380589a969aad"
HOST = "https://api.census.gov/data"

#set year for data and acs5 or sf1
year = "2010"
dataset = "sf1"
base_url = "/".join([HOST, year, dataset])

county_count = 29
state_fips = 2

#p5_vars = ["P005" + str(i + 1).zfill(4) for i in range(17)]
#get_vars = ["NAME"] + p5_vars
get_vars = [#"NAME",
            "P0010001", #total
            "P0030002", #white alone
            "P0050003", #white alone and not Hispanic/Latino
            "P0040003", #Hispanic/Latino
#            "P0070006", #Cambodian, at all
            "P0030004", #Native American or Alaska Native alone
            "P0060004", #Nat. Am. or Alaska Nat. +
            "P0030005", #Asian alone
            "P0030003", #Black/African American alone
#            "H0160002" #owner-occupied housing
            ]

data = []
#loop over Alaska's boroughs + areas (158 after 2015 for Kusilvak, 270 before)
for i in [13,16,20,50,60,68,70,90,
          100,105,110,122,130,150,164,170,180,185,188,195,198,
          220,230,240,261,270,275,282,290]:
#loop over the 14 counties in MA
#for i in range(1,2*county_count,2): 
#for i in range(17,18):
    predicates = {}         
    predicates["get"] = ",".join(get_vars)
    predicates["for"] = "tract:*"
#    predicates["for"] = "block group:*"
#    predicates["for"] = "block:*"
    predicates["in"] = "state:"+str(state_fips)+"+county:"+str(i)#+"+place:"+str(37000)
    predicates["key"] = CENSUS_API_KEY

# Write the result to a response object:
    response = requests.get(base_url, params=predicates)
    try:
        col_names = response.json()[0]
        data = data + response.json()[1:]
    except :
        print(response.url)

census_df = pd.DataFrame(columns=col_names, data=data)
census_df.set_index(["state", "county", "tract"#, "block group"
                     ], drop=False, inplace=True)
census_df['geoid'] = census_df['state'].astype(str) + census_df['county'].astype(str) + census_df['tract'].astype(str) #+ census_df['block group'].astype(str)

census_df['tot_pop'] = pd.to_numeric(census_df['P0010001'])
census_df['pr_white'] = pd.to_numeric(census_df['P0030002']) / pd.to_numeric(census_df['P0010001'])
#census_df['pr_white_not_hisp'] = pd.to_numeric(census_df['P0050003']) / pd.to_numeric(census_df['P0010001'])
census_df['pr_hisp_lat'] = pd.to_numeric(census_df['P0040003']) / pd.to_numeric(census_df['P0010001'])
#census_df['prop_cambodian'] = pd.to_numeric(census_df['P0070006']) / pd.to_numeric(census_df['P0010001'])
census_df['pr_native'] = pd.to_numeric(census_df['P0030004']) / pd.to_numeric(census_df['P0010001'])
census_df['pr_native+'] = pd.to_numeric(census_df['P0060004']) / pd.to_numeric(census_df['P0010001'])
census_df['pr_asian'] = pd.to_numeric(census_df['P0030005']) / pd.to_numeric(census_df['P0010001'])
census_df['pr_black_afr_am'] = pd.to_numeric(census_df['P0030003']) / pd.to_numeric(census_df['P0010001'])
#census_df['prop_owner_occ'] = pd.to_numeric(census_df['H0160002']) / pd.to_numeric(census_df['P0010001'])

census_df.fillna(0, inplace=True)

census_df.to_csv("alaska_data_tract.csv")
