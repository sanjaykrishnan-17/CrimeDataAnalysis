import streamlit as st
import pandas as pd
from plotly import express as px
import numpy as np
from plotly import graph_objects as go
from matplotlib import pyplot as plt
import requests
from geopy.geocoders import Nominatim 

def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]

def get_location():
    ip_address = get_ip()
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    city = location_data.get("city").upper()
    state = location_data.get("region").upper()
    return [city,state]

def get_latlong(city):
    loc = Nominatim(user_agent="GetLoc")
    getLoc = loc.geocode(city)
    return [getLoc.latitude, getLoc.longitude]

siteHeader = st.container()
locationInfo = st.container()
plotting = st.container()
safetyReco = st.container()

t = open('text.txt', 'r')

with siteHeader:
    st.markdown('<p style="font-family: Showcard Gothic, monospace; color: red; font-size: 72px;text-align: center"><b>CRIME DATA ANALYSIS AND SAFETY RECOMMENDATION</b></p>', unsafe_allow_html=True)
    st.markdown('<hr style="height:5px;border:none;color:#000000;background-color:#FFFFFF;"/> ', unsafe_allow_html=True)
    st.image(r'crimestory.png')
    st.markdown('<hr style="height:5px;border:none;color:#000000;background-color:#FFFFFF;"/>', unsafe_allow_html=True)

with locationInfo:
    st.markdown('<p style="font-family: Verdana; color: red; font-size: 25px;text-align: center"><b>a 2-minute-read on crimes in India</b></p>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-family: Verdana;text-align: justify;">{t.read()}</p>', unsafe_allow_html=True)
    st.markdown("""<hr style="height:5px;border:none;color:#000000;background-color:#FFFFFF;" /> """, unsafe_allow_html=True)
    by_place = pd.read_csv(r'by_place.csv', index_col=[0])
    dist_wise = pd.read_csv(r'dist_wise.csv', index_col=[0])
    d = pd.read_csv(r'clustered.csv', index_col=[0])

    # try: 
    # city = get_location()[0]
    # state = get_location()[1]
    # except:
    state = st.sidebar.selectbox('STATE', d['STATE'].unique())
    city = st.sidebar.selectbox('CITY', d[(d['STATE'] == state)]['DISTRICT'])
    
    st.markdown(f'<p style = "font-family: Verdana; text-align: center">You are currently in </p><p style="font-family: Verdana; font-size: 24px;text-align: center"><b>{city}, {state}</b></p>', unsafe_allow_html=True)
    latlong = {'lat':[get_latlong(city)[0]], 'lon':[get_latlong(city)[1]]}
    df = pd.DataFrame(latlong)
    st.map(df)
    out = pd.DataFrame(d[(d['STATE'] == state) & (d['DISTRICT'] == city)].cluster).to_csv(sep='\t', index=False)[7:]
    st.markdown(f'<p style="font-family:Courier New; font-size: 56px;background-color:red; color:black; text-align: center"><b>{out.upper()}</b></p>', unsafe_allow_html=True)
    
with locationInfo:
    st.markdown('<hr style="height:5px;border:none;color:#000000;background-color:#FFFFFF"/>', unsafe_allow_html=True)
    st.markdown(f'<p style = "font-family: Verdana; font-size: 50px; text-align: center"><b>A DETAILED CRIME ANALYSIS OF THE PLACE</b></p>',  unsafe_allow_html=True)
    
    state_dist = pd.DataFrame(d[d['STATE'] == state]['cluster'].value_counts())
    st.markdown('<p style="font-family: Showcard Gothic, monospace; color: red; font-size: 35px;text-align: center"><b>TYPES OF CRIMES IN THE PLACE</b></p>', unsafe_allow_html=True)
    df = dist_wise[(dist_wise['STATE/UT'] == state) & (dist_wise['DISTRICT'] == city)]
    d = {'value_options': ['MURDER', 'ATTEMPT TO MURDER',
       'CULPABLE HOMICIDE NOT AMOUNTING TO MURDER', 'RAPE', 'CUSTODIAL RAPE',
       'KIDNAPPING & ABDUCTION', 'KIDNAPPING AND ABDUCTION OF WOMEN AND GIRLS',
       'KIDNAPPING AND ABDUCTION OF OTHERS',
       'PREPARATION AND ASSEMBLY FOR DACOITY', 'ROBBERY', 'BURGLARY', 'THEFT',
       'AUTO THEFT', 'RIOTS', 'CRIMINAL BREACH OF TRUST',
       'CHEATING', 'COUNTERFIETING', 'ARSON', 'HURT/GREVIOUS HURT',
       'ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY',
       'INSULT TO MODESTY OF WOMEN',
       'IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES',
       'CAUSING DEATH BY NEGLIGENCE'], 
        'values': [df['MURDER'].to_list()[0], df['ATTEMPT TO MURDER'].to_list()[0],
                   df['CULPABLE HOMICIDE NOT AMOUNTING TO MURDER'].to_list()[0], df['RAPE'].to_list()[0],
                   df['CUSTODIAL RAPE'].to_list()[0],
                   df['KIDNAPPING & ABDUCTION'].to_list()[0], df['KIDNAPPING AND ABDUCTION OF WOMEN AND GIRLS'].to_list()[0],
                   df['KIDNAPPING AND ABDUCTION OF OTHERS'].to_list()[0], df['PREPARATION AND ASSEMBLY FOR DACOITY'].to_list()[0],
                   df['ROBBERY'].to_list()[0], df['BURGLARY'].to_list()[0],
                   df['THEFT'].to_list()[0], df['AUTO THEFT'].to_list()[0],
                   df['RIOTS'].to_list()[0], df['CRIMINAL BREACH OF TRUST'].to_list()[0], 
                   df['CHEATING'].to_list()[0],
                   df['COUNTERFIETING'].to_list()[0], df['ARSON'].to_list()[0],
                   df['HURT/GREVIOUS HURT'].to_list()[0], df['ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY'].to_list()[0],
                   df['INSULT TO MODESTY OF WOMEN'].to_list()[0], df['IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES'].to_list()[0], 
                   df['CAUSING DEATH BY NEGLIGENCE'].to_list()[0]
                   ]}
    df = pd.DataFrame(data=d)
    fig = px.pie(df,
                values="values",
                names="value_options")
    st.plotly_chart(fig)
    st.markdown('<p style="font-family: Showcard Gothic, monospace; color: red; font-size: 35px;text-align: center"><b>DISTRIBUTION OF CRIME</b></p>', unsafe_allow_html=True)
    fig = px.bar(state_dist, x="cluster", color="cluster")
    st.write(fig)
    df = by_place[by_place['STATE/UT'] == state]
    hi = 'HIGHWAYS'
    ri = 'RIVER and SEA'
    ra = 'RAILWAYS'
    ba = 'BANKS'
    co = 'COMMERCIAL ESTABLISHMENTS'
    ot = 'OTHER PLACES'
    def pie(place, df):
        d = {'value_options': [f'{place} - Dacoity', f'{place} - Robbery',
                                f'{place} - Burglary', f'{place} - Theft'], 
            'values': [df[f'{place} - Dacoity'].to_list()[0], df[f'{place} - Robbery'].to_list()[0], 
                        df[f'{place} - Burglary'].to_list()[0], df[f'{place} - Theft'].to_list()[0]]}
        df = pd.DataFrame(data=d)
        st.markdown(f'<p style="font-family: Showcard Gothic, monospace; color: red; font-size: 35px;text-align: center"><b>{place}</b></p>', unsafe_allow_html=True)
        pie_chart = px.pie(df,
                        values="values",
                        names="value_options")
        st.plotly_chart(pie_chart)
    pie(hi, df)
    pie(ri, df)
    pie(ra, df)
    pie(ba, df)
    pie(co, df)
    pie(ot, df)

with safetyReco:
    st.markdown('<p style="font-family: Showcard Gothic, monospace; color: white; font-size: 35px;text-align: center; background-color:red;"><b>When you\'re on streets:</b></p>', unsafe_allow_html=True)
    st.text("""
    • Stand tall and walk confidently. Watch where you’re going and what’s happening around you.
    • Stick to well-lit and busy streets. Walk with friends. Avoid shortcuts through a dark alley or a deserted street.
    • If harassed by someone in a car, walk quickly or run in the opposite direction to safety. If you are really scared, scream.
    • Never hitchhike. Accept rides only from people you know and trust.
    • Don’t flash your cash.
    • Always have a well-charged cell phone immediately available.
    • Know your neighborhood. What hours are stores and restaurants open? Where are the police and fire stations, libraries, and schools? You might need them in an emergency.
    • If you go out for a late-night snack or a midnight movie, take a friend. Don’t go alone. Most assaults happen to a lone victim.
    • Let someone know where you are going and when you will come back. Call if you’re going to be late.
    • If you are driving, park your car in well-lit places and lock it when you leave. Check for uninvited passengers in the back seat or on the floor before you get in.
    • Have your keys in hand when approaching your car. Don’t wait until you get to the car to look for your keys.
    • Alter your routine. Change daily patterns and, if possible, take different routes to work or to school. Park in different locations.
    """)
    
    st.markdown('<p style="font-family: Showcard Gothic, monospace; color: white; font-size: 35px;text-align: center; background-color:red;"><b>When you’re alone:</b></p>', unsafe_allow_html=True)
    st.text("""
    • Always stop and think about the risk.
    • Always identify a visitor before opening the door.
    • Never allow young children to open the door to visitors.
    • Always ask representatives to provide identification.
    • Avoid walking alone at night.
    • Walk in busy well lit roads, towards traffic.
    """)
    
    st.markdown('<p style="font-family: Showcard Gothic, monospace; color: white; font-size: 35px;text-align: center; background-color:red;"><b>When you travel:</b></p>', unsafe_allow_html=True)
    st.text("""
    • Always be alert while leaving the gate of your house or retuming to the house this applies to entry and exit from the office complex as well. Keep your car doors locked while traveling/when parked in the garage. If no garage is available, leave your car at a Place where it can be seen by everyone.
    • Vary your time of departure and change your route frequently Use altemative routes occasionally though this may involve increase in commuting time. If you have a choice of vehicles, do not make full use of them.
    • Occasionally, sit beside the driver in the front seat.
    • Travel in a group to the extent possible.
    • If you think you are being followed, take a known detour and if you are still suspicious, head for the nearest police station.
    • Avoid narrow lonely dark streets and keep to the well -lit main routes especially those that pass by police posts.
    • Beware of accident scenes or broken down vehicles they may be a decoy.
    • If something unusual appears to be taking place on the road ahead, stop and turn before it is too late.
    • Give details of your intended movements to only those who need to know.
    • Ensure that someone in your family knows your whereabouts.
    • While moving in a car, open the windows only enough for ventilation.
    • Have your driver thoroughly briefed to be security conscious. Let him get training in offensive and defensive driving.
    • See that your car is not very showy.
    • While traveling by train, enter into a compartment, which is already occupied. Do not travel in a empty compartment. 
    """)