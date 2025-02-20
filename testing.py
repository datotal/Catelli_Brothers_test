import pandas as pd
import numpy as np
import streamlit as st
import folium
import plotly.express as px
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')
from streamlit_folium import folium_static
import plotly.graph_objects as go
from plotly.subplots import make_subplots


data=pd.read_excel(r"TMS Data for Catelli Brothers 1 1.xlsx")
df=data
df_zip=pd.read_excel(r"ZIp_lat_long_Pooja.xlsb")

shipper_country='sCountry'
consignee_country='cCountry'
shipper_zip=str('sZip')
consignee_zip='cZip'
shipper_state='sState'
consignee_state='cState'
shipper_city='sCity'
consignee_city='cCity'
weight='Weight'
charge='Charge'
shipper_name='sName'
consignee_name='cName'
shipdate='ShipDate'
count='# Shipments'
carriername='CarrierName'

df = df.merge(df_zip, left_on=shipper_zip, right_on='ZipCode', how='left')
df=df.rename(columns={'Latitude':'lat1','Longitude':'long1'})

# Perform a VLOOKUP-like operation using merge for consignee ZIP
df = df.merge(df_zip, left_on=consignee_zip, right_on='ZipCode', how='left')
df=df.rename(columns={'Latitude':'lat','Longitude':'long'})
df['Distance'] = df.apply(lambda row: geodesic((row['lat1'], row['long1']), (row['lat'], row['long'])).miles, axis=1)       


df[shipdate] = pd.to_datetime(df[shipdate], errors='coerce').dt.date

df['WeekNumber'] = pd.to_datetime(df[shipdate], errors='coerce').dt.isocalendar().week

df['Shipper_3digit_zip']=df[shipper_zip].astype(str).str[:3]
df['Consignee_3digit_zip']=df[consignee_zip].astype(str).str[:3]

# df1['Distance'] = df.apply(lambda row: geodesic((row['lat1'], row['long1']), (row['lat'], row['long'])).miles, axis=1)       

shipper_zips_of_interest=[8103,53186,1590]#warehouse location
#Limit
parcel_limit=7.38
LTL_limit=106
truckload_limit=200

# transfer_shipments=df[(df[shipper_zip].isin(shipper_zips_of_interest))& (df[consignee_zip].isin(shipper_zips_of_interest))& (df['Mode']=='TRUCKLOAD') & (df[weight]>10000)]
# transfer_shipments=df[(df[shipper_zip].isin(shipper_zips_of_interest))& (df[consignee_zip].isin(shipper_zips_of_interest))]
# transfer_shipments['CPP']=transfer_shipments[charge]/transfer_shipments[weight]

def find_outliers_zscore(data, threshold=3):
    mean = np.mean(data)
    std_dev = np.std(data)
    z_scores = (data - mean) / std_dev
    outliers = np.abs(z_scores) > threshold
    return outliers

# outliers_zscore = find_outliers_zscore(transfer_shipments['CPP'])
# outliers=( transfer_shipments[outliers_zscore]['# Shipments'])
# transfer_shipments=transfer_shipments[~transfer_shipments['# Shipments'].isin(outliers)]

# charge1=transfer_shipments[charge].sum()
# count1=transfer_shipments[count].count()
# weight1=transfer_shipments[weight].sum()

# optimal_truck=weight1/40000
# cost_of_single_tl=charge1/count1
# print('cost_of_single_tl',cost_of_single_tl)
# derived_cost=(cost_of_single_tl*round(optimal_truck))

# savings=(charge1-derived_cost)

st.header("Warehouse Analysis Based On Distance")

df=df[(df[shipper_country]=='US') & (df[consignee_country]=='US')]# taking US to US

considering_outbound = df[df[shipper_zip].isin(shipper_zips_of_interest)]
considering_outbound=considering_outbound[considering_outbound[weight]<10000]

print("Warehouse list",set(considering_outbound[shipper_zip]))
p=considering_outbound[[shipper_zip,shipper_state,'lat1','long1']]
p1=p.drop_duplicates(keep="first")
p1['shipper_lat_long'] = p1.apply(lambda row: f'({row["lat1"]}, {row["long1"]})', axis=1)
szip=[]
slat=[]
slong=[]
sstate=[]
for i in range(0,len(p1)):
    szip.append(p1[shipper_zip].iloc[i])
    slat.append(p1['lat1'].iloc[i])
    slong.append(p1['long1'].iloc[i])
    sstate.append(p1[shipper_state].iloc[i])
warehouse_lat_long=list(zip(szip,slat,slong,sstate))
print("warehouse list with lat long",warehouse_lat_long)

preferred_zip=[]
preferred_state=[]
preferred_lat_long=[]
difference_distance=[]
for i in range(0,len(considering_outbound)):
    miles=99999999
    pzip=0
    pstate='ab'
    plat=0
    plong=0
    for j in range(0,len(warehouse_lat_long)):
         outbound_coords = (considering_outbound['lat'].iloc[i], considering_outbound['long'].iloc[i])
         warehouse_coords = (warehouse_lat_long[j][1],warehouse_lat_long[j][2])

         sample_miles = geodesic(outbound_coords,
                               warehouse_coords).miles
         if sample_miles < miles:
             miles=sample_miles
             pzip=warehouse_lat_long[j][0]
             pstate=warehouse_lat_long[j][3]
             plat=warehouse_lat_long[j][1]
             plong=warehouse_lat_long[j][2]
    pdistance=geodesic((considering_outbound['lat'].iloc[i], considering_outbound['long'].iloc[i]),(plat,plong)).miles  
    difference_distance.append((considering_outbound['Distance'].iloc[i]) - pdistance )       
    preferred_zip.append(pzip)
    preferred_state.append(pstate)
    preferred_lat_long.append(((plat,plong)))
considering_outbound['preferred_loc']=preferred_zip
considering_outbound['differnece_distance']=difference_distance  
considering_outbound['preferred_state']=preferred_state
considering_outbound['preferredloc_lat_long']=preferred_lat_long


#Getting preffered location which is not same as actual location and difference distance is greater than 100 miles
preferred_loc=considering_outbound[considering_outbound[shipper_zip] != considering_outbound['preferred_loc'] ]
preferred_loc=preferred_loc[preferred_loc['differnece_distance']>100]


#distance between preffered loc and czip
distance=[]
for idx in range(len(preferred_loc)):
    preferedlat_long=(preferred_loc['preferredloc_lat_long'])
    
    cziplat_long=(preferred_loc['lat'].iloc[idx],preferred_loc['long'].iloc[idx])
    
    disc=geodesic(preferred_loc['preferredloc_lat_long'].iloc[idx],cziplat_long).miles
    distance.append(disc)
preferred_loc['Preferred_Distance']=distance

#Map 
def map_is_created(zips,loc):
    map_centers=[]
    colors=['#e7b108','#ff6969','#96B6C5','#916DB3','#B0578D','#EDB7ED','#A8DF8E','#C8AE7D','#A79277','#A4BC92',
            '#e7b108','#ff6969','#96B6C5','#916DB3','#B0578D','#EDB7ED','#A8DF8E','#C8AE7D','#A79277','#A4BC92',
            '#e7b108','#ff6969','#96B6C5','#916DB3','#B0578D','#EDB7ED','#A8DF8E','#C8AE7D','#A79277','#A4BC92']
    incrementer=0
    for i in range(0,len(warehouse_lat_long)):
        
        outbound_locations=considering_outbound[considering_outbound[zips]==warehouse_lat_long[i][0]]
        outbound_locations[loc] = outbound_locations.apply(lambda row: [row['lat'], row['long']], axis=1)
        data = {'center': (warehouse_lat_long[i][1],warehouse_lat_long[i][2]), 'locations': outbound_locations[loc].tolist(), 'line_color': colors[incrementer]}
        incrementer += 1
        map_centers.append(data)
    # Create a map
    mymap = folium.Map(location=[35.192, -89.8692], zoom_start=3, weight=1)
    for center_data in map_centers:
        center = center_data['center']
        locations = center_data['locations']
        line_color = center_data['line_color']

        # Add lines connecting center to locations
        folium.Marker(center, icon=folium.Icon(color='red')).add_to(mymap)
        for loc in locations:
            folium.PolyLine([center, loc], color=line_color).add_to(mymap)
    
    return mymap
    
originalmap=(map_is_created(shipper_zip,'location'))      
st.write("Current fulfillment map by warehouse")  
folium_static(originalmap)

originalmap=(map_is_created('preferred_loc','locations_prefered'))      
st.write("Map if orders filled by preferred (closest) warehouse")  
folium_static(originalmap)   

# col1, col2 = st.columns(2)

# # Display the first DataFrame in the first column
# with col1:
#     originalmap=(map_is_created(shipper_zip,'location'))      
#     st.write("Current fulfillment map by warehouse")  
#     folium_static(originalmap)

# # Display the second DataFrame in the second column
# with col2:
#     originalmap=(map_is_created('preferred_loc','locations_prefered'))      
#     st.write("Map if orders filled by preferred (closest) warehouse")  
#     folium_static(originalmap)

unique_warehouse=[]
for i in range(0,len(warehouse_lat_long)):
    unique_warehouse.append(warehouse_lat_long[i][0])

#removing transfer shipments    
preferred_loc=preferred_loc[~preferred_loc[consignee_zip].isin(unique_warehouse)]
#consignee name not equal to shipper name
filter=preferred_loc[shipper_name]==preferred_loc[consignee_name]
filter1= preferred_loc[consignee_state]==preferred_loc['preferred_state']
cstate_pstate=preferred_loc[(filter1)]
print(cstate_pstate)
preferred_loc=preferred_loc[~(filter)]

grouped_df = cstate_pstate.groupby(['sState', 'sZip','cState','cZip','preferred_loc', 'preferred_state']).size().reset_index(name=count)

pivot=(grouped_df.sort_values(count,ascending=False)).reset_index(drop=True).head(5)


preferred_loc=preferred_loc[~(filter1)]


cpm=[]
for i in range(0,len(preferred_loc)):              
        
        if not df[(df[shipper_zip]==preferred_loc['preferred_loc'].iloc[i]) & 
                  (df[consignee_zip]==preferred_loc[consignee_zip].iloc[i]) & 
                  (df['Mode']==preferred_loc['Mode'].iloc[i]) & (df['Distance'] !=0) ].empty:
                
                cpm.append(df[(df[shipper_zip]==preferred_loc['preferred_loc'].iloc[i]) & 
                  (df[consignee_zip]==preferred_loc[consignee_zip].iloc[i]) & 
                  (df['Mode']==preferred_loc['Mode'].iloc[i])& (df['Distance'] !=0)][charge].sum()/
                           
                           df[(df[shipper_zip]==preferred_loc['preferred_loc'].iloc[i]) & 
                  (df[consignee_zip]==preferred_loc[consignee_zip].iloc[i]) & 
                  (df['Mode']==preferred_loc['Mode'].iloc[i])& (df['Distance'] !=0)]['Distance'].sum()
                          )
                
        elif not df[(df[shipper_zip]==preferred_loc['preferred_loc'].iloc[i])&
                     (df['Consignee_3digit_zip']==preferred_loc['Consignee_3digit_zip'].iloc[i]) & 
                      (df['Mode']==preferred_loc['Mode'].iloc[i])& (df['Distance'] !=0)].empty:
                      
                      cpm.append((df[(df[shipper_zip]==preferred_loc['preferred_loc'].iloc[i])
                                   & (df['Consignee_3digit_zip']==preferred_loc['Consignee_3digit_zip'].iloc[i]) 
                                    & (df['Mode']==preferred_loc['Mode'].iloc[i])& (df['Distance'] !=0)][charge].sum())/
                                 
                                 ((df[(df[shipper_zip]==preferred_loc['preferred_loc'].iloc[i])
                                   & (df['Consignee_3digit_zip']==preferred_loc['Consignee_3digit_zip'].iloc[i]) 
                                    & (df['Mode']==preferred_loc['Mode'].iloc[i])& (df['Distance'] !=0)]['Distance'].sum()))
                                )     
                      
        elif not  df[(df[shipper_state]==preferred_loc['preferred_state'].iloc[i])&
                     (df[consignee_state]==preferred_loc[consignee_state].iloc[i]) & 
                      (df['Mode']==preferred_loc['Mode'].iloc[i])& (df['Distance'] !=0)].empty: 
                      
                      cpm.append(df[(df[shipper_state]==preferred_loc['preferred_state'].iloc[i])&
                     (df[consignee_state]==preferred_loc[consignee_state].iloc[i]) & 
                      (df['Mode']==preferred_loc['Mode'].iloc[i])& (df['Distance'] !=0)][charge].sum()/
                                df[(df[shipper_state]==preferred_loc['preferred_state'].iloc[i])&
                     (df[consignee_state]==preferred_loc[consignee_state].iloc[i]) & 
                      (df['Mode']==preferred_loc['Mode'].iloc[i])& (df['Distance'] !=0)]['Distance'].sum())
                      
                      
        else:
            cpm.append(0)

preferred_loc['CPM']=cpm 
preferred_loc['CPM']=preferred_loc['CPM']
preferred_loc=preferred_loc[preferred_loc['CPM']!=0]    
preferred_loc['Estimated $'] = preferred_loc['CPM'] * preferred_loc['Preferred_Distance']

#setting limit
preferred_loc.loc[(preferred_loc['Mode'] == 'PARCEL') & (preferred_loc['Estimated $'] < parcel_limit), 'Estimated $'] = parcel_limit
preferred_loc.loc[(preferred_loc['Mode'] == 'LTL') & (preferred_loc['Estimated $'] < LTL_limit), 'Estimated $'] = LTL_limit
preferred_loc['Savings']=preferred_loc[charge]-(preferred_loc['Estimated $']) 
print(preferred_loc)

weight_non_optimal_warehouse=preferred_loc[weight].sum()/40000
print('Non optimal warehouse count',int(weight_non_optimal_warehouse))
# print('Cost',weight_non_optimal_warehouse*cost_of_single_tl)


preferred_loc=preferred_loc[preferred_loc['Savings']>0]

#changing datatype
preferred_loc=preferred_loc.astype({'Savings':int,'differnece_distance':int})
print(preferred_loc)
warehouseSavings=int(preferred_loc['Savings'].sum())
warehousecharge=int(preferred_loc[charge].sum())
print(warehouseSavings)

# print('savings',warehouseSavings-(weight_non_optimal_warehouse*cost_of_single_tl))

preferred_loc=preferred_loc.sort_values(by='Savings',ascending=False)# sort_by_savings
#formatting
st.write("Out of total "+ str(considering_outbound.shape[0])+" Lanes ,"+ str(preferred_loc.shape[0])+
         " lanes can be shipped from a warehouse that is closer (with a 100 mile tolerance). ")

preferred_loc['Estimated $']=preferred_loc[charge]-preferred_loc['Savings']
preferred_loc['Estimated $'] = preferred_loc['Estimated $'].round(2)
preferred_loc[charge] = '$ ' + preferred_loc[charge].astype(str)
preferred_loc['Estimated $'] = '$ ' + preferred_loc['Estimated $'].astype(str)
preferred_loc['Savings'] = '$ ' + preferred_loc['Savings'].astype(str)

grouped_df1 = preferred_loc.groupby(['sState', 'sZip','cState','cZip','preferred_loc', 'preferred_state']).size().reset_index(name=count)

pivot1=(grouped_df1.sort_values(count,ascending=False)).reset_index(drop=True).head(5)

st.dataframe(preferred_loc[[count,shipper_zip,shipper_city,shipper_state,consignee_zip,consignee_city,consignee_state,weight,charge,'preferred_loc','preferred_state','differnece_distance','Estimated $','Savings']].reset_index(drop=True))
st.subheader("Total Spend $"+str(f'{warehousecharge:,}'))
# st.subheader("Total Savings $"+str(f'{round(warehouseSavings-(weight_non_optimal_warehouse*cost_of_single_tl)):,}'))
st.subheader("Efficient Warehouse Utilization: Localized Shipping Solutions")
# st.dataframe(pivot)
# st.dataframe(pivot1)
# Create a streamlit columns layout
col1, col2 = st.columns(2)

# Display the first DataFrame in the first column
with col1:
    
    st.write(pivot)

# Display the second DataFrame in the second column
with col2:
    
    st.write(pivot1)

print("successfully executed")