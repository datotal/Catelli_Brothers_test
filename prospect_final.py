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

#setting page icon
st.set_page_config(
    page_title="Prospect Analysis",
    page_icon="🌙",
   
    initial_sidebar_state="auto",
)
data=pd.read_excel(r"TMS Data for Catelli Brothers 1 1.xlsx")
df=data
print(df.columns)
st.title("PROSPECT RECOMMENDATIONS")
df_zip=pd.read_excel(r"ZIp_lat_long_Pooja.xlsb")

# df_datRates=pd.read_excel(r"TL_Rates_Sears.xlsx")
# new_column_names = {
#     'EstimatedLineTotal': 'Average Market Rate',
#     'HighLineTotal': 'Ceiling Rate'
# }
# df_datRates = df_datRates.rename(columns=new_column_names)


shipper_country='sCountry'
consignee_country='cCountry'
shipper_zip='sZip'
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
# Perform a VLOOKUP-like operation using merge for shipper ZIP

def convert_to_int(zip_code):
    try:
        return int(zip_code)
    except ValueError:
        return zip_code

df[consignee_zip] = df[consignee_zip].apply(convert_to_int)
df[shipper_zip] = df[shipper_zip].apply(convert_to_int)
df = df.merge(df_zip, left_on=shipper_zip, right_on='ZipCode', how='left')
df=df.rename(columns={'Latitude':'lat1','Longitude':'long1'})

# Perform a VLOOKUP-like operation using merge for consignee ZIP
df = df.merge(df_zip, left_on=consignee_zip, right_on='ZipCode', how='left')
df=df.rename(columns={'Latitude':'lat','Longitude':'long'})

#droping the rows when there is a null in these cols
df.replace(['', ' ', '  ','NULL','NONE'], pd.NA, inplace=True)
df=df.drop_duplicates(keep='first')
df[count]=df[count].astype(str)
# df = df.dropna(axis=0, subset=[shipper_country,consignee_country,shipper_zip,consignee_zip,shipper_state,consignee_state,
#                                shipper_city,consignee_city,weight,charge,'lat1','long1','lat','long'])

df['MonthYear'] = df[shipdate].dt.strftime('%B %Y')  
month_counts = df['MonthYear'].nunique()

st.header("Time Frame "+str(month_counts)+" Months ")
st.subheader("Shipment Count "+str(f'{data.shape[0]:,}'))

#converting into upper case
# df[[shipper_city,consignee_city,shipper_name,consignee_name,carriername]]=df[[shipper_city,consignee_city,shipper_name,consignee_name,carriername]].apply(lambda x: x.str.upper())

# #removing extra space
# df[[shipper_country,consignee_country,shipper_city,consignee_city,shipper_name,consignee_name,shipper_state,consignee_state,carriername]]=df[[shipper_country,consignee_country,shipper_city,consignee_city,shipper_name,consignee_name,shipper_state,consignee_state,carriername]].apply(lambda a: a.str.strip())

#converting weight to numeric
# df[weight] = pd.to_numeric(df[weight], errors='coerce')
# df.dropna(subset=[weight], inplace=True)
df1=df
#Getting the datas whos weight and charge is greater than 0
df=df[(df[weight]>0) & (df[charge]>0)]

st.subheader("Total Shipments Excluding Outliers "+str(f'{df1.shape[0]:,}'))
print("Total Shipments After Removing Outliers "+str(f'{df1.shape[0]:,}'))
bad_data_count=(data.shape[0] - df1.shape[0])
bad_data_per=((data.shape[0]-df1.shape[0])/data.shape[0])*100
st.subheader("Outliers "+str(f'{bad_data_count:,}')+" ("+str(round(bad_data_per,1))+"%)")
df[shipper_zip]=df[shipper_zip].astype('str')
df[consignee_zip]=df[consignee_zip].astype('str')

df1[shipper_zip]=df1[shipper_zip].astype('str')
df1[consignee_zip]=df1[consignee_zip].astype('str')

df[[shipper_zip,consignee_zip]]=df[[shipper_zip,consignee_zip]].apply(lambda x:x.str[:5])
df['Shipper_3digit_zip']=df[shipper_zip].astype(str).str[:3]
df['Consignee_3digit_zip']=df[consignee_zip].astype(str).str[:3]

df1[[shipper_zip,consignee_zip]]=df1[[shipper_zip,consignee_zip]].apply(lambda x:x.str[:5])
df1['Shipper_3digit_zip']=df1[shipper_zip].astype(str).str[:3]
df1['Consignee_3digit_zip']=df1[consignee_zip].astype(str).str[:3]

# df_datRates[[shipper_zip,consignee_zip]]=df_datRates[[shipper_zip,consignee_zip]].astype(str)
# df_datRates[[shipper_zip,consignee_zip]]=df_datRates[[shipper_zip,consignee_zip]].apply(lambda x:x.str[:5])
# df_datRates['Shipper_3digit_zip']=df_datRates[shipper_zip].str[:3]
# df_datRates['Consignee_3digit_zip']=df_datRates[consignee_zip].str[:3]

df[[charge,weight]] = df[[charge,weight]].apply(lambda x:x.astype(int))
df['Mode']=df['Mode'].apply(lambda x: x.upper())

df1[[charge,weight]] = df1[[charge,weight]].apply(lambda x:x.astype(int))
df1['Mode']=df1['Mode'].apply(lambda x: x.upper())


total_charge=int(df[charge].sum())
st.subheader("Total Spend $"+str(f'{total_charge:,}'))

#savings chart
name= ['LTL to TL Mode Optimization','TL_DAT Rates']
savings_total= [3245,3246]


saving_percentage=int(((sum(savings_total))/(total_charge))*100)
total_saving=int(sum(savings_total))

st.subheader("Total Savings $"+str(f'{total_saving:,}')+" ("+str(saving_percentage)+"%)")

# savings chart
fig = px.pie(names=name,values=savings_total,hole=0.5,color_discrete_sequence=px.colors.sequential.Sunset )
fig.update_layout(title='Savings Chart',title_x=0.5)

st.plotly_chart(fig)

#Top carrier
st.subheader("Number Of Carriers Utilized: "+str(len(df[carriername].unique())))

carriers_list=df.groupby(carriername).aggregate({charge:'sum'}).reset_index().sort_values(by=charge,ascending=False).head(10)
fig=px.bar(carriers_list,x=charge,y=carriername, title='Top Carriers')
fig.update_yaxes(categoryorder='total ascending')
fig.update_xaxes(title_text="Spend")
fig.update_yaxes(title_text="Carrier")
st.plotly_chart(fig)

#predicted warehouses
shipper_zips_of_interest=[8103,53186,1590]#warehouse location
warehouse=df[df[shipper_zip].isin(shipper_zips_of_interest)]
warehouse_list=df.groupby(shipper_state).aggregate({charge:'sum'}).reset_index().sort_values(by=charge,ascending=False)
fig=px.bar(warehouse_list,x=charge,y=shipper_state,title='Warehouse')
# fig=px.bar(warehouse_list,x=charge,y=shipper_city, title='Warehouse')
fig.update_yaxes(categoryorder='total ascending')
fig.update_xaxes(title_text="Spend")
fig.update_yaxes(title_text='Warehouse')
st.plotly_chart(fig)

# #Mode chart
mode=df.groupby('Mode').aggregate({charge:'sum'}).reset_index().sort_values(by=charge,ascending=False)
fig=px.bar(mode,x=charge,y='Mode', title='Spend By Mode')
fig.update_yaxes(categoryorder='total ascending')
fig.update_xaxes(title_text="Spend")
fig.update_yaxes(title_text='Mode')
st.plotly_chart(fig)



# distance between two zips
df['Distance'] = df.apply(lambda row: geodesic((row['lat1'], row['long1']), (row['lat'], row['long'])).miles, axis=1)       


df[shipdate] = pd.to_datetime(df[shipdate], errors='coerce').dt.date

df['WeekNumber'] = pd.to_datetime(df[shipdate], errors='coerce').dt.isocalendar().week

df1['Distance'] = df.apply(lambda row: geodesic((row['lat1'], row['long1']), (row['lat'], row['long'])).miles, axis=1)       


df1[shipdate] = pd.to_datetime(df[shipdate], errors='coerce').dt.date

df1['WeekNumber'] = pd.to_datetime(df[shipdate], errors='coerce').dt.isocalendar().week


#Limit
parcel_limit=7.38
LTL_limit=106
truckload_limit=200
print("Data Cleaning sucessfully done")
  



########################################################## CPP ##################################################################
def costPerPound(df_len,mode):
    cpp=[]
    for i in range(0,len(df_len)):
        if not df[(df[shipper_zip]==df_len[shipper_zip].iloc[i]) & 
                  (df[consignee_zip]==df_len[consignee_zip].iloc[i]) & 
                  (df['Mode']==mode) & 
                  (df[count]!=df_len[count].iloc[i])].empty:
                            
                            cpp.append(df[(df[shipper_zip]==df_len[shipper_zip].iloc[i]) & 
                                          (df[consignee_zip]==df_len[consignee_zip].iloc[i]) 
                                          & (df['Mode']==mode)& (df[count]!=df_len[count].iloc[i])][charge].sum()/
                                       df[(df[shipper_zip]==df_len[shipper_zip].iloc[i]) & 
                                          (df[consignee_zip]==df_len[consignee_zip].iloc[i]) 
                                          & (df['Mode']==mode)& (df[count]!=df_len[count].iloc[i])][weight].sum()
                                      )
                             

        elif not df[(df[shipper_zip]==df_len[shipper_zip].iloc[i])&
                     (df['Consignee_3digit_zip']==df_len['Consignee_3digit_zip'].iloc[i]) & 
                      (df['Mode']==mode)& (df[count]!=df_len[count].iloc[i])].empty:
                      
                      cpp.append((df[(df[shipper_zip]==df_len[shipper_zip].iloc[i])
                                   & (df['Consignee_3digit_zip']==df_len['Consignee_3digit_zip'].iloc[i]) 
                                    & (df['Mode']==mode)& 
                                     (df[count]!=df_len[count].iloc[i])][charge].sum())/
                                 
                                 ((df[(df[shipper_zip]==df_len[shipper_zip].iloc[i])
                                   & (df['Consignee_3digit_zip']==df_len['Consignee_3digit_zip'].iloc[i]) 
                                    & (df['Mode']==mode)& 
                                      (df[count]!=df_len[count].iloc[i])][weight].sum()))
                                )
                    
        elif not  df[(df[shipper_state]==df_len[shipper_state].iloc[i])&
                     (df[consignee_state]==df_len[consignee_state].iloc[i]) & 
                      (df['Mode']==mode)& 
                     (df[count]!=df_len[count].iloc[i])].empty: 
                      
                      cpp.append(df[(df[shipper_state]==df_len[shipper_state].iloc[i])&
                     (df[consignee_state]==df_len[consignee_state].iloc[i]) & 
                      (df['Mode']==mode)&
                                    (df[count]!=df_len[count].iloc[i])][charge].sum()/
                                df[(df[shipper_state]==df_len[shipper_state].iloc[i])&
                     (df[consignee_state]==df_len[consignee_state].iloc[i]) & 
                      (df['Mode']==mode)& (df[count]!=df_len[count].iloc[i])][weight].sum())              

        else:  
        
            cpp.append(0)
                            
        
    return cpp              

################################################################### DAT Rates #######################################################3
# def dat_Rates(df_len,szip,col_name):
#     dat=[]
#     for i in range(0,len(df_len)):
#         if not df_datRates[(df_datRates[shipper_zip]==df_len[szip].iloc[i]) & 
#                   (df_datRates[consignee_zip]==df_len[consignee_zip].iloc[i]) ].empty:
                            
#                             dat.append(df_datRates[(df_datRates[shipper_zip]==df_len[szip].iloc[i]) & 
#                                           (df_datRates[consignee_zip]==df_len[consignee_zip].iloc[i])][col_name].mean())
                                     
#         else:  
        
#             dat.append(0)
                                    
#     return dat              

########################### ZONES #########################################
print("Zones")
# df['Shipper_3digit_zip']=df[shipper_zip].astype(str).str[:3]
# df['Consignee_3digit_zip']=df[consignee_zip].astype(str).str[:3]
# df['Distance'] = df.apply(lambda row: geodesic((row['lat1'], row['long1']), (row['lat'], row['long'])).miles, axis=1)
# df['FEDEX_Zone'] = np.where((df['Distance'] >= 0) & (df['Distance'] <= 150), 'Zone2',
#                                np.where((df['Distance'] >= 151) & (df['Distance'] <= 300), 'Zone3',
#                                         np.where((df['Distance'] >= 301) & (df['Distance'] <= 600), 'Zone4',
#                                                  np.where((df['Distance'] >= 601) & (df['Distance'] <= 1000), 'Zone5',
#                                                           np.where((df['Distance'] >= 1001) & (df['Distance'] <= 1400), 'Zone6',
#                                                                    np.where((df['Distance'] >= 1401) & (df['Distance'] <= 1800), 'Zone7',
#                                                                             np.where(df['Distance'] >= 1801, 'Zone8', ' ')))))))


# upsn_zone=pd.read_excel(r"C:\Users\pvijayakumar\Downloads\UPSN Zones.xlsx")

# upsn_zone[['Shipper_3digit_zip','Consignee_3digit_zip']]=upsn_zone[['Shipper_3digit_zip','Consignee_3digit_zip']].apply(lambda x:x.astype('str'))
# #vlookup
# df_zone=df.merge(upsn_zone,on=['Shipper_3digit_zip','Consignee_3digit_zip'],how='inner')

# df_zone=df_zone[(df_zone['Mode']=='PARCEL') & ((df_zone['Ground']==2)| (df_zone['FEDEX_Zone']=='Zone2')) & 
#            (df_zone['ServiceLevel']!= 'Ground') & (df_zone['ServiceLevel'] != 'FedEx Ground') ]

# ################################################# When zone is given ############################################
# df_zone=df[(df['Mode']=='PARCEL') & (df['Zone']==2)& (df['Zone']==3) & (df['ServiceLevel']!= 'Ground') & (df['ServiceLevel'] != 'FedEx Ground') ]
# cpp=[]
# for i in range(0,len(df_zone)):
#         if not df[(df[shipper_zip]==df_zone[shipper_zip].iloc[i]) & 
#                   (df[consignee_zip]==df_zone[consignee_zip].iloc[i]) & 
#                   (df['Mode']=='PARCEL') & 
#                   ((df['ServiceLevel']=='Ground')| (df['ServiceLevel'] == 'FedEx Ground'))].empty:
                            
#                             cpp.append(df[(df[shipper_zip]==df_zone[shipper_zip].iloc[i]) & 
#                                           (df[consignee_zip]==df_zone[consignee_zip].iloc[i]) 
#                                           & (df['Mode']=='PARCEL')& ((df['ServiceLevel']=='Ground')| (df['ServiceLevel'] == 'FedEx Ground'))][charge].sum()/
#                                        df[(df[shipper_zip]==df_zone[shipper_zip].iloc[i]) & 
#                                           (df[consignee_zip]==df_zone[consignee_zip].iloc[i]) 
#                                           & (df['Mode']=='PARCEL')& ((df['ServiceLevel']=='Ground')| (df['ServiceLevel'] == 'FedEx Ground'))][weight].sum()
#                                       )
                             

#         elif not df[(df[shipper_zip]==df_zone[shipper_zip].iloc[i])&
#                      (df['Consignee_3digit_zip']==df_zone['Consignee_3digit_zip'].iloc[i]) & 
#                       (df['Mode']=='PARCEL')& ((df['ServiceLevel']=='Ground')| (df['ServiceLevel'] == 'FedEx Ground'))].empty:
                      
#                       cpp.append((df[(df[shipper_zip]==df_zone[shipper_zip].iloc[i])
#                                    & (df['Consignee_3digit_zip']==df_zone['Consignee_3digit_zip'].iloc[i]) 
#                                     & (df['Mode']=='PARCEL')& ((df['ServiceLevel']=='Ground')| (df['ServiceLevel'] == 'FedEx Ground'))][charge].sum())/
                                 
#                                  ((df[(df[shipper_zip]==df_zone[shipper_zip].iloc[i])
#                                    & (df['Consignee_3digit_zip']==df_zone['Consignee_3digit_zip'].iloc[i]) 
#                                     & (df['Mode']=='PARCEL')& ((df['ServiceLevel']=='Ground')| (df['ServiceLevel'] == 'FedEx Ground'))][weight].sum()))
#                                 )
                    
#         elif not  df[(df[shipper_state]==df_zone[shipper_state].iloc[i])&
#                      (df[consignee_state]==df_zone[consignee_state].iloc[i]) & 
#                       (df['Mode']=='PARCEL')& ((df['ServiceLevel']=='Ground')| (df['ServiceLevel'] == 'FedEx Ground'))].empty: 
                      
#                       cpp.append(df[(df[shipper_state]==df_zone[shipper_state].iloc[i])&
#                      (df[consignee_state]==df_zone[consignee_state].iloc[i]) & 
#                       (df['Mode']=='PARCEL')& ((df['ServiceLevel']=='Ground')| (df['ServiceLevel'] == 'FedEx Ground'))][charge].sum()/
#                                 df[(df[shipper_state]==df_zone[shipper_state].iloc[i])&
#                      (df[consignee_state]==df_zone[consignee_state].iloc[i]) & 
#                       (df['Mode']=='PARCEL')& ((df['ServiceLevel']=='Ground')| (df['ServiceLevel'] == 'FedEx Ground'))][weight].sum())              

#         else:  
        
#             cpp.append(0)
# df_zone['cpp']=cpp                         
# df_zone['Estimated PARCEL$']=df_zone['cpp']*df_zone[weight]
# df_zone.loc[(df_zone['Estimated PARCEL$'] <parcel_limit),'Estimated PARCEL$' ]=parcel_limit
# df_zone['Savings']=df_zone[charge]-(df_zone['Estimated PARCEL$'])

# zone_Savings=int(df_zone['Savings'].sum())             
# zone_charge=int(df_zone[charge].sum())

# if df_zone.shape[0]>1:
#     #formatting
#     st.subheader('Zones')
#     df_zone[charge] = '$ ' + df_zone[charge].astype(str)
#     df_zone['Estimated PARCEL$'] = '$ ' + df_zone['Estimated PARCEL$'].astype(str)
#     df_zone['Savings'] = '$ ' + df_zone['Savings'].astype(str)
#     st.write(df_zone[['Zone',shipper_zip,consignee_zip,carriername,weight,charge,'Estimated PARCEL$','Savings']].reset_index(drop=True))
#     st.subheader("Total Spend $"+str(f'{zone_charge:,}'))          
#     st.subheader("Total Savings $"+str(f'{zone_Savings:,}'))
# print("Zones part completed")
##############################LTL to PARCEL#########################################     
print("LTL to Parcel")   
df_ltl=df[df['Mode']=='LTL']
LTL_to_PARCEL=df_ltl[df_ltl[weight]<150]
LTL_to_PARCEL['cpp']=costPerPound(LTL_to_PARCEL,'PARCEL')
LTL_to_PARCEL=LTL_to_PARCEL[LTL_to_PARCEL['cpp']!=0]
LTL_to_PARCEL['Estimated PARCEL$']=LTL_to_PARCEL['cpp']*LTL_to_PARCEL[weight]
if LTL_to_PARCEL.shape[0]>1:
    # setting limit
    LTL_to_PARCEL.loc[(LTL_to_PARCEL['Estimated PARCEL$'] <parcel_limit),'Estimated PARCEL$' ]=parcel_limit
    LTL_to_PARCEL['Savings']=LTL_to_PARCEL[charge]-(LTL_to_PARCEL['Estimated PARCEL$'])
    LTL_to_PARCEL=LTL_to_PARCEL[LTL_to_PARCEL['Savings']>1]
    #changing datatype
    LTL_to_PARCEL=LTL_to_PARCEL.astype({'Savings':int,'Estimated PARCEL$':int})
    ltltoPARCEL_Savings=int(LTL_to_PARCEL['Savings'].sum())             
    ltltoPARCEL_charge=int(LTL_to_PARCEL[charge].sum())

    LTL_to_PARCEL=LTL_to_PARCEL.sort_values(by='Savings',ascending=False) # sort_by_savings
    #formatting
    st.header("LTL To Parcel Mode Optimization")
    st.subheader("Based On Weight We Recommend " + str(f'{LTL_to_PARCEL.shape[0]:,}')+ " Shipments Can Be Shipped via PARCEL Ground")
    LTL_to_PARCEL[charge] = '$ ' + LTL_to_PARCEL[charge].astype(str)
    LTL_to_PARCEL['Estimated PARCEL$'] = '$ ' + LTL_to_PARCEL['Estimated PARCEL$'].astype(str)
    LTL_to_PARCEL['Savings'] = '$ ' + LTL_to_PARCEL['Savings'].astype(str)
    st.write(LTL_to_PARCEL[[count,shipper_zip,consignee_zip,carriername,weight,charge,'Estimated PARCEL$','Savings']].reset_index(drop=True))
    st.subheader("Total Spend $"+str(f'{ltltoPARCEL_charge:,}'))          
    st.subheader("Total Savings $"+str(f'{ltltoPARCEL_Savings:,}'))

else:
      df_ltl=df1[df1['Mode']=='LTL']
      LTL_to_PARCEL=df_ltl[df_ltl[weight]<150]
      if LTL_to_PARCEL.shape[0]>1:
            ltltoPARCEL_charge=int(LTL_to_PARCEL[charge].sum())
            st.header("LTL To Parcel Mode Optimization")
            st.write(":red[Exclusion from Savings: Component Excluded Due to Null Charges]")
            st.subheader("Based On Weight We Recommend " + f":red[{str(f'{LTL_to_PARCEL.shape[0]:,}')}]"+ " Shipments Can Be Shipped via PARCEL Ground")
            # st.subheader("Opportunities: Based On Weight We Recommend <span style='color:red;'>" + str(f'{LTL_to_PARCEL.shape[0]:,}')+ "</span> Shipments Can Be Shipped via PARCEL Ground", unsafe_allow_html=True)

            LTL_to_PARCEL[charge] = '$ ' + LTL_to_PARCEL[charge].astype(str)
            st.write(LTL_to_PARCEL[[count,shipper_zip,consignee_zip,carriername,weight]].reset_index(drop=True))
             
            print("LTL to parcel completed")    
print("LTL to parcel completed")
# ###############################################PARCEL to LTL####################################
print("Parcel to LTL")
PARCEL=df[df['Mode']=='PARCEL']
PARCEL_to_LTL=PARCEL[PARCEL[weight]>150]
PARCEL_to_LTL['cpp']=costPerPound(PARCEL_to_LTL,'LTL')
PARCEL_to_LTL=PARCEL_to_LTL[PARCEL_to_LTL['cpp']!=0]
PARCEL_to_LTL['Estimated Freight$']=PARCEL_to_LTL['cpp'] * PARCEL_to_LTL[weight]
if PARCEL_to_LTL.shape[0]>1:
    #setting limit
    PARCEL_to_LTL.loc[(PARCEL_to_LTL['Estimated Freight$'] <LTL_limit),'Estimated Freight$' ]=LTL_limit
    PARCEL_to_LTL['Savings']=PARCEL_to_LTL[charge]-(PARCEL_to_LTL['Estimated Freight$'])
    PARCEL_to_LTL=PARCEL_to_LTL[PARCEL_to_LTL['Savings']>1]
    #changing data type
    PARCEL_to_LTL=PARCEL_to_LTL.astype({'Savings':int,'Estimated Freight$':int})
    PARCELtoltl_Savings=int(PARCEL_to_LTL['Savings'].sum())
    PARCELtoltl_charge=int(PARCEL_to_LTL[charge].sum())

    PARCEL_to_LTL=PARCEL_to_LTL.sort_values(by='Savings',ascending=False) # sort_by_savings
    #formatting
    st.header("Parcel To LTL Mode Optimization")
    st.subheader("Based On Weight We Recommend " + str(f'{PARCEL_to_LTL.shape[0]:,}')+ " Shipements Can Be Shipped via LTL")
    PARCEL_to_LTL[charge] = '$ ' + PARCEL_to_LTL[charge].astype(str)
    PARCEL_to_LTL['Estimated Freight$'] = '$ ' + PARCEL_to_LTL['Estimated Freight$'].astype(str)
    PARCEL_to_LTL['Savings'] = '$ ' + PARCEL_to_LTL['Savings'].astype(str)
    st.write(PARCEL_to_LTL[[count,shipper_zip,consignee_zip,carriername,weight,charge,'Estimated Freight$','Savings']].reset_index(drop=True)) 
    st.subheader("Total Spend $"+str(f'{PARCELtoltl_charge:,}'))                         
    st.subheader("Total Savings $"+str(f'{PARCELtoltl_Savings:,}')) 

else:
      PARCEL=df1[df1['Mode']=='PARCEL']
      PARCEL_to_LTL=PARCEL[PARCEL[weight]>150]
      if PARCEL_to_LTL.shape[0]>1:
            PARCELtoltl_charge=int(PARCEL_to_LTL[charge].sum())
            st.header("Parcel To LTL Mode Optimization")
            st.write(":red[Exclusion from Savings: Component Excluded Due to Null Charges]")
            st.subheader("Based On Weight We Recommend " + f":red[{str(f'{PARCEL_to_LTL.shape[0]:,}')}]"+ " Shipements Can Be Shipped via LTL")
            PARCEL_to_LTL[charge] = '$ ' + PARCEL_to_LTL[charge].astype(str)
            st.write(PARCEL_to_LTL[[count,shipper_zip,consignee_zip,carriername,weight]].reset_index(drop=True)) 
            
          
print("Parcel to LTL completed")
###############################################LTL to TL####################################
print("LTL to TL")
ltl=df[df['Mode']=='LTL']
LTL_to_TL=ltl[ltl[weight]>10000]
LTL_to_TL['Estimated Freight$']=0
# LTL_to_TL['Estimated Freight$']=dat_Rates(LTL_to_TL,shipper_zip,'Ceiling Rate')
LTL_to_TL=LTL_to_TL[LTL_to_TL['Estimated Freight$']!=0]

if LTL_to_TL.shape[0]>1:
    #setting limit
    LTL_to_TL.loc[(LTL_to_TL['Estimated Freight$'] <truckload_limit),'Estimated Freight$' ]=truckload_limit
    LTL_to_TL['Savings']=LTL_to_TL[charge]-(LTL_to_TL['Estimated Freight$'])
    LTL_to_TL=LTL_to_TL[LTL_to_TL['Savings']>0]
    # changing datatype
    LTL_to_TL=LTL_to_TL.astype({'Savings':int,'Estimated Freight$':int})
    PARCELtoltl_Savings=int(LTL_to_TL['Savings'].sum())
    PARCELtoltl_charge=int(LTL_to_TL[charge].sum())

    LTL_to_TL=LTL_to_TL.sort_values(by='Savings',ascending=False)# sort_by_savings
    #formatting
    st.header("LTL To TL Mode Optimization")
    st.subheader("Based On Weight We Recommend " + str(f'{LTL_to_TL.shape[0]:,}')+ " Shipements Can Be Shipped via TL")
    LTL_to_TL[charge] = '$ ' + LTL_to_TL[charge].astype(str)
    LTL_to_TL['Estimated Freight$'] = '$ ' + LTL_to_TL['Estimated Freight$'].astype(str)
    LTL_to_TL['Savings'] = '$ ' + LTL_to_TL['Savings'].astype(str)
    # st.write(LTL_to_TL[[count,shipper_zip,consignee_zip,carriername,weight,charge,'Estimated Freight$','Savings']].reset_index(drop=True)) 
    st.subheader("Total Spend $"+str(f'{PARCELtoltl_charge:,}'))                         
    st.subheader("Total Savings $"+str(f'{PARCELtoltl_Savings:,}')) 
else:
      ltl=df1[df1['Mode']=='LTL']
      LTL_to_TL=ltl[ltl[weight]>10000]
    #   LTL_to_TL['Estimated Freight$']=dat_Rates(LTL_to_TL,shipper_zip,'Ceiling Rate')
      if LTL_to_TL.shape[0]>1:
            PARCELtoltl_charge=int(LTL_to_TL[charge].sum())

            st.header("LTL To TL Mode Optimization")
            st.write(":red[Exclusion from Savings: Component Excluded Due to Null Charges]")
            st.subheader("Based On Weight We Recommend " + f":red[{str(f'{LTL_to_TL.shape[0]:,}')}]"+ " Shipements Can Be Shipped via TL")
            LTL_to_TL[charge] = '$ ' + LTL_to_TL[charge].astype(str)
            st.dataframe(LTL_to_TL[[count,shipper_zip,consignee_zip,carriername,weight]].reset_index(drop=True), use_container_width=True)
            
                
print("LTL to TL completed")    
######################################################################consolidating PARCEL##################################################
print("consolidation")  
# df['Consolidated_data']=df[consignee_name]+df[consignee_city]+df[consignee_state]+df[consignee_zip]
df['Consolidated_data']=df[consignee_state]+df[consignee_zip].astype(str)
consolidation=df[[shipper_city,shipper_state,shipper_zip,count,shipdate,carriername,consignee_zip,consignee_state,'Shipper_3digit_zip','Consignee_3digit_zip',
                  'Mode','Consolidated_data',weight,charge,'WeekNumber']]
consolidation.dropna(inplace=True)

df1['Consolidated_data']=df1[consignee_name]+df1[consignee_city]+df1[consignee_state]+df1[consignee_zip]
consolidation1=df1[[shipper_city,shipper_state,shipper_zip,count,shipdate,carriername,consignee_zip,consignee_state,'Shipper_3digit_zip','Consignee_3digit_zip',
                  'Mode','Consolidated_data',weight,charge,'WeekNumber']]
consolidation1.dropna(inplace=True)

#PARCEL consolidation
consolidation_by_mode_PARCEL=consolidation[consolidation['Mode']=='PARCEL']
aggregation_functions = {
    count: 'count',           
    weight: 'sum',    
    charge: 'sum'      
}
cons_by_PARCEL = consolidation_by_mode_PARCEL.groupby([shipper_city,shipper_zip,shipper_state,consignee_state,consignee_zip,'Shipper_3digit_zip','Consignee_3digit_zip',
                                                       'Consolidated_data', shipdate]).agg(aggregation_functions)

cons_by_PARCEL=cons_by_PARCEL.reset_index()
shipment_consolidated_PARCEL=cons_by_PARCEL[cons_by_PARCEL[count]>1]

#PARCEL consolidation
consolidation_by_mode_PARCEL1=consolidation1[consolidation1['Mode']=='PARCEL']
aggregation_functions = {
    count: 'count',           
    weight: 'sum',    
    charge: 'sum'      
}
cons_by_PARCEL1 = consolidation_by_mode_PARCEL1.groupby([shipper_city,shipper_zip,shipper_state,consignee_state,consignee_zip,'Shipper_3digit_zip','Consignee_3digit_zip',
                                                       'Consolidated_data', shipdate]).agg(aggregation_functions)

cons_by_PARCEL1=cons_by_PARCEL1.reset_index()
shipment_consolidated_PARCEL1=cons_by_PARCEL1[cons_by_PARCEL[count]>1]

if (shipment_consolidated_PARCEL.shape[0])>1 :
    st.header('Parcel To LTL Consolidation')
    shipment_consolidated_PARCEL1=shipment_consolidated_PARCEL.reset_index().sort_values(by=[count,weight],ascending=False)
    #these can be consolidated
    shipment_consolidated_PARCEL1[[shipper_city,shipper_state,shipdate,'Consolidated_data',weight,charge,count]].reset_index(drop=True)

    shipment_consolidated_PARCEL1=shipment_consolidated_PARCEL.reset_index().sort_values(by=[count,weight],ascending=False)

    st.subheader("In PARCEL Out Of "+str(f'{consolidation_by_mode_PARCEL.shape[0]:,}')
                +" Shipments, "+str(f'{shipment_consolidated_PARCEL1.shape[0]:,}')+" Can Be Consolidated")

    
    shipment_consolidated_PARCEL1[charge] = shipment_consolidated_PARCEL1[charge].astype(str)
    shipment_consolidated_PARCEL1[charge]='$ '+shipment_consolidated_PARCEL1[charge]
    st.write(shipment_consolidated_PARCEL1[[shipper_city,shipdate,'Consolidated_data',weight,charge,count]].reset_index(drop=True))
    shipment_consolidated_PARCEL1[charge] = shipment_consolidated_PARCEL1[charge].str.replace('$', '')
    shipment_consolidated_PARCEL1[charge] = shipment_consolidated_PARCEL1[charge].astype(int)
    ############################################ consolidating PARCEL to LTL######################################
    shipment_consolidated_PARCEL_LTL=shipment_consolidated_PARCEL1[(shipment_consolidated_PARCEL1[weight]>150)]
    if (shipment_consolidated_PARCEL_LTL.shape[0]>1):
        shipment_consolidated_PARCEL_LTL['cpp']=costPerPound(shipment_consolidated_PARCEL_LTL,'LTL')
        shipment_consolidated_PARCEL_LTL=shipment_consolidated_PARCEL_LTL[shipment_consolidated_PARCEL_LTL['cpp']!=0]
        shipment_consolidated_PARCEL_LTL['Estimated Freight$']=shipment_consolidated_PARCEL_LTL['cpp']*shipment_consolidated_PARCEL_LTL[weight]
        
        #setting limit
        shipment_consolidated_PARCEL_LTL.loc[(shipment_consolidated_PARCEL_LTL['Estimated Freight$'] <LTL_limit),'Estimated Freight$' ]=LTL_limit
        shipment_consolidated_PARCEL_LTL['Savings']=(shipment_consolidated_PARCEL_LTL[charge]-(shipment_consolidated_PARCEL_LTL['Estimated Freight$']))
        shipment_consolidated_PARCEL_LTL=shipment_consolidated_PARCEL_LTL[shipment_consolidated_PARCEL_LTL['Savings']>0]
        #changing datatype
        shipment_consolidated_PARCEL_LTL=shipment_consolidated_PARCEL_LTL.astype({'Savings':int,'Estimated Freight$':int})
        consolidation_Savings=int(shipment_consolidated_PARCEL_LTL['Savings'].sum())
        consolidation_charge=int(shipment_consolidated_PARCEL_LTL[charge].sum())

        shipment_consolidated_PARCEL_LTL=shipment_consolidated_PARCEL_LTL.sort_values(by='Savings',ascending=False) # sort_by_savings
        #formatting
        st.subheader("By Consolidating "+str(f'{shipment_consolidated_PARCEL1.shape[0]:,}')+" Shipments,"+str(shipment_consolidated_PARCEL_LTL.shape[0])+" Shipments Can Go via LTL Service")
        
        shipment_consolidated_PARCEL_LTL[charge] = '$ ' + shipment_consolidated_PARCEL_LTL[charge].astype(str)
        shipment_consolidated_PARCEL_LTL['Estimated Freight$'] = '$ ' + shipment_consolidated_PARCEL_LTL['Estimated Freight$'].astype(str)
        shipment_consolidated_PARCEL_LTL['Savings'] = '$ ' + shipment_consolidated_PARCEL_LTL['Savings'].astype(str)
        st.write(shipment_consolidated_PARCEL_LTL[[shipper_city,shipdate,'Consolidated_data',weight,charge,count,'Estimated Freight$','Savings']].reset_index(drop=True))
        st.subheader("Total Spend $"+str(f'{consolidation_charge:,}'))
        st.subheader("Total Savings $"+str(f'{consolidation_Savings:,}'))
   
elif (shipment_consolidated_PARCEL1.shape[0])>1 :
    st.header('Parcel To LTL Consolidation')
    shipment_consolidated_PARCEL1=shipment_consolidated_PARCEL1.reset_index().sort_values(by=[count,weight],ascending=False)
    #these can be consolidated
    shipment_consolidated_PARCEL1[[shipper_city,shipper_state,shipdate,'Consolidated_data',weight,charge,count]].reset_index(drop=True)

    shipment_consolidated_PARCEL1=shipment_consolidated_PARCEL.reset_index().sort_values(by=[count,weight],ascending=False)

    st.subheader("In PARCEL Out Of "+str(f'{consolidation_by_mode_PARCEL.shape[0]:,}')
                +" Shipments, "+str(f'{shipment_consolidated_PARCEL1.shape[0]:,}')+" Can Be Consolidated")

    
    shipment_consolidated_PARCEL1[charge] = shipment_consolidated_PARCEL1[charge].astype(str)
    shipment_consolidated_PARCEL1[charge]='$ '+shipment_consolidated_PARCEL1[charge]
    st.write(shipment_consolidated_PARCEL1[[shipper_city,shipdate,'Consolidated_data',weight,charge,count]].head(10).reset_index(drop=True))
    shipment_consolidated_PARCEL1[charge] = shipment_consolidated_PARCEL1[charge].str.replace('$', '')
    shipment_consolidated_PARCEL1[charge] = shipment_consolidated_PARCEL1[charge].astype(int)    
    ############################################ consolidating PARCEL to LTL######################################
    shipment_consolidated_PARCEL_LTL=shipment_consolidated_PARCEL1[(shipment_consolidated_PARCEL1[weight]>150)]
    if (shipment_consolidated_PARCEL_LTL.shape[0]>1):
       
        consolidation_charge=int(shipment_consolidated_PARCEL_LTL[charge].sum())
        #formatting
        st.subheader("By Consolidating PARCEL Shipments,"+str(shipment_consolidated_PARCEL_LTL.shape[0])+" Shipments Can Go via LTL Service")
        
        shipment_consolidated_PARCEL_LTL[charge] = '$ ' + shipment_consolidated_PARCEL_LTL[charge].astype(str)
        st.subheader("Total Spend $"+str(f'{consolidation_charge:,}'))
        st.write(shipment_consolidated_PARCEL_LTL[[shipper_city,shipdate,'Consolidated_data',weight,charge,count]].head(10).reset_index(drop=True))
       
print("parcel to LTL consolidation completed")
       
###################################################################consolidating LTL##################################################
def split_shipment(row):
    if row[weight] > 40000:
        num_shipments = row[weight] // 40000
        remaining_weight = row[weight] % 40000
        for i in range(num_shipments):
            yield {'Consolidated_data': row['Consolidated_data'], weight: 40000}
        if remaining_weight > 0:
            yield {'Consolidated_data': row['Consolidated_data'], weight: remaining_weight}
consolidation_by_mode_LTL=consolidation[consolidation['Mode']=='LTL']

aggregation_functions = {
    count: 'count',           
    weight: 'sum',    
    charge: 'sum'      
}

def LTL_TL_cons(consbyLTL,a,var):
    consbyLTL=consbyLTL.reset_index()
    print(consbyLTL)
    shipment_consolidated_LTL=consbyLTL[consbyLTL['# Shipments']>1]
    if shipment_consolidated_LTL.shape[0]>1:
        st.header('LTL To TL Consolidation'+var)
        shipment_consolidated_LTL1=shipment_consolidated_LTL.reset_index().sort_values(by='# Shipments',ascending=False)
        st.subheader("In LTL Out Of "+str(f'{consolidation_by_mode_LTL.shape[0]:,}')
                    +" Shipments, "+str(shipment_consolidated_LTL1.shape[0])+" Can Be Consolidated")
        
              
        # shipment_consolidated_LTL1[weight] = shipment_consolidated_LTL1[weight].apply(lambda x: min(x, 40000))
        shipment_consolidated_LTL1[charge]=shipment_consolidated_LTL1[charge].astype(str)
        shipment_consolidated_LTL1[charge]='$ '+shipment_consolidated_LTL1[charge].astype(str)

        st.write(shipment_consolidated_LTL1[[shipper_city,a,'Consolidated_data',weight,charge,'# Shipments']].reset_index(drop=True))
        shipment_consolidated_LTL1[charge]=shipment_consolidated_LTL1[charge].str.replace('$', '')
        shipment_consolidated_LTL1[charge]=shipment_consolidated_LTL1[charge].astype(int)

        ############################################ consolidating LTL to TL######################################
        shipment_consolidated_LTL_TL=shipment_consolidated_LTL1[(shipment_consolidated_LTL1[weight]>10000)]
        if (shipment_consolidated_LTL_TL.shape[0]>1):
            shipment_consolidated_LTL_TL[weight] = shipment_consolidated_LTL_TL[weight].apply(lambda x: min(x, 40000))
            shipment_consolidated_LTL_TL['Estimated Freight$']=0
            # shipment_consolidated_LTL_TL['Estimated Freight$']=dat_Rates(shipment_consolidated_LTL_TL,shipper_zip,'Ceiling Rate')

            shipment_consolidated_LTL_TL = shipment_consolidated_LTL_TL[shipment_consolidated_LTL_TL['Estimated Freight$'] ==0]
            # shipment_consolidated_LTL_TL = shipment_consolidated_LTL_TL[shipment_consolidated_LTL_TL['Estimated Freight$'] !=0]
            


            shipment_consolidated_LTL_TL['Savings']=(shipment_consolidated_LTL_TL[charge]-(shipment_consolidated_LTL_TL['Estimated Freight$']))
            shipment_consolidated_LTL_TL=shipment_consolidated_LTL_TL[shipment_consolidated_LTL_TL['Savings']>0]
            #changing datatype
            shipment_consolidated_LTL_TL=shipment_consolidated_LTL_TL.astype({'Savings':int,'Estimated Freight$':int})
            consolidation_Savings=int(shipment_consolidated_LTL_TL['Savings'].sum())
            consolidation_charge=int(shipment_consolidated_LTL_TL[charge].sum())

            shipment_consolidated_LTL_TL=shipment_consolidated_LTL_TL.sort_values(by='Savings',ascending=False)#sort_by_savings
            #formatting
            st.subheader("By Consolidating  "+str(shipment_consolidated_LTL1.shape[0])+" Shipments,"+str(shipment_consolidated_LTL_TL.shape[0])+" Shipments Can Go via TL Service")
            
            shipment_consolidated_LTL_TL[charge] = '$ ' + shipment_consolidated_LTL_TL[charge].astype(str)
            shipment_consolidated_LTL_TL['Estimated Freight$'] = '$ ' + shipment_consolidated_LTL_TL['Estimated Freight$'].astype(str)
            shipment_consolidated_LTL_TL['Savings'] = '$ ' + shipment_consolidated_LTL_TL['Savings'].astype(str)
            st.write(shipment_consolidated_LTL_TL[[shipper_city,a,'Consolidated_data',weight,charge,'# Shipments','Estimated Freight$','Savings']].reset_index(drop=True))
            st.subheader("Total Spend $"+str(f'{consolidation_charge:,}'))
            st.subheader("Total Savings $"+str(f'{consolidation_Savings:,}'))
    print("LTL to TL consolidation completed")


cons_by_LTL = LTL_TL_cons(consolidation_by_mode_LTL.groupby([shipper_city,shipper_zip,shipper_state,consignee_state,consignee_zip,'Shipper_3digit_zip','Consignee_3digit_zip',
                                                       'Consolidated_data', shipdate]).agg(aggregation_functions),shipdate," ")

##################################### TRUCKLOAD #########################################################

# st.header('TL vs TL DAT Rates')
# st.write ("As of today's date rate")
# # st.header('TL to TL_DAT Rates <span style="font-size:small;">(As on 4/25/2024 rates)</span>', unsafe_allow_html=True)

# df_tl=df[df[weight]>=10000]

# # df_tl['Average Market Rate']=dat_Rates(df_tl,shipper_zip,'Average Market Rate')
# # df_tl['Celing Rate']=dat_Rates(df_tl,shipper_zip,'Ceiling Rate')
# df_tl=df_tl[(df_tl['Average Market Rate']>0) & (df_tl['Celing Rate']>0)]
# print(df_tl)
# #setting limit
# # df_tl.loc[(df_tl[charge] <truckload_limit),charge ]=truckload_limit
# df_tl['Market savings']=df_tl[charge]-df_tl['Average Market Rate']
# df_tl['celing savings']=df_tl[charge]-df_tl['Celing Rate']

# df_tl=df_tl[(df_tl['Market savings']>0) & (df_tl['celing savings']>0)]

# total=int(df_tl[charge].sum())
# estimated=int(df_tl['Market savings'].sum())
# high=int(df_tl['celing savings'].sum())
# print(total)
# print(estimated)
# print(high)
# # savings_estimated=round(((estimated)/total)*100,2)
# try:
#   savings_high=round(((high)/total)*100,2)
# except:
#       savings_high =0   

# df_tl['Average Market Rate']=df_tl['Average Market Rate'].round(2)
# df_tl['Celing Rate']=df_tl['Celing Rate'].round(2)
# #formatting
# df_tl[charge]='$ ' + df_tl[charge].astype(str)
# df_tl['Average Market Rate']= '$ ' + df_tl['Average Market Rate'].astype(str)
# df_tl['Celing Rate']= '$ ' + df_tl['Celing Rate'].astype(str)
# st.dataframe(df_tl[['sZip','cZip','Charge','Average Market Rate','Celing Rate']].reset_index(drop=True))
# st.subheader("Total Audited Charge $"+str(f'{total:,}'))
# # st.subheader('Average Market Rate - Savings '+str(f'{(estimated):,}')+" ("+str(savings_estimated)+"%)")
# st.subheader('Ceiling Rate - Savings $'+str(f'{(high):,}')+" ("+str(savings_high)+"%)")
# print("DAT rates completed")

########################################## Inventory transfer cost ##############################################

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

# st.header("Inventory Transfer Cost Savings")


# data = {
#     " ": ["Total Trucks actually used","Weight", "Cost $", "Optimal Trucks", "Optimal Trucks Cost $"],
#     "   ": [str(f'{count1:,}'),str(f'{weight1:,}'), str(f'{transfer_shipments[charge].sum():,}'), str(f'{round(optimal_truck):,}'), str(f'{round(derived_cost):,}')]
# }

# dfasas = pd.DataFrame(data)
# df_inventory_savings=dfasas.reset_index(drop=True)
# st.dataframe(df_inventory_savings.reset_index(drop=True))
# st.header("Savings $"+str(f'{round(savings):,}'))
################################ warehouse ######################################
st.subheader("------------------------------------------------------------------------------")
st.header("Additional Potential Savings")
#additional savings 
d=['Consolidation weekwise']
c=[31753]
saving_percentage=int(((sum(c))/(total_charge))*100)
total_saving=int(sum(c))
st.subheader("Total Savings $"+str(f'{total_saving:,}')+" ("+str(saving_percentage)+"%)")


cons_by_LTL = LTL_TL_cons(consolidation_by_mode_LTL.groupby([shipper_city,shipper_zip,shipper_state,consignee_state,consignee_zip,'Shipper_3digit_zip','Consignee_3digit_zip',
                                                       'Consolidated_data', 'WeekNumber']).agg(aggregation_functions),'WeekNumber'," Weekwise")

st.header("Warehouse Analysis Based On Distance")

# Debug print to check the initial DataFrame shape
print("Initial DataFrame shape:", df.shape)

df=df[(df[shipper_country]=='US') & (df[consignee_country]=='US')]# taking US to US

# Debug print to check the shape after filtering by shipper_zips_of_interest
considering_outbound = df.copy()
# print("Shape after filtering by shipper_zips_of_interest:", considering_outbound.shape)
# print(df[shipper_zip].head())
# print(df[shipper_zips_of_interest].head())
# Debug print to check the shape after filtering by weight
considering_outbound = considering_outbound[considering_outbound[weight]<10000]
# print("Shape after filtering by weight:", considering_outbound.shape)

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


