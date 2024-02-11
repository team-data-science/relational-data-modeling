# Import libraries
import pandas as pd 
import numpy as np
from sqlalchemy import create_engine

# Establish the connection
conn = create_engine("mysql+pymysql://{user}:{pw}@localhost:{host}/{db}"
                       .format(user = "user",
                               pw = "password",
                               host = 42333,
                               db = "salesdb"))

# Change the path if you have your xls dataset somewhere else
file_location = r'C:\Users\katep\OneDrive\Documents\Andreas\relational-data-modeling\assets_files\US_Regional_Sales_Data.xlsx'
basic = pd.read_excel(file_location, sheet_name = 0)
stores = pd.read_excel(file_location, sheet_name = 2)
products = pd.read_excel(file_location, sheet_name = 3)
employees = pd.read_excel(file_location, sheet_name = 5)
customers = pd.read_excel(file_location, sheet_name = 1)

def customers_tbl(df):
    """The function saves customer details to mysql customers table"""
    #split the full name column to first name & last name
    df[['customer_first_name', 'customer_last_name']] = df['Customer Names'].str.split(' ', expand = True)
    
    #rename multiple column names by label
    df.rename(columns={'_CustomerID':'customer_id'}, inplace = True)
    
    #save to database
    df = df[['customer_id', 'customer_first_name', 'customer_last_name']]
    df.to_sql(name = 'customer', con = conn, if_exists = 'append', index = False)
    
    return df


def states_tbl(df):
    """The function saves state details to mysql states table"""
   
    df = df[["State", "StateCode", "AreaCode"]].drop_duplicates(subset = "State")

    #rename multiple column names by label
    df.rename(columns={'State':'state', 'StateCode':'state_code', 'AreaCode':'area_code'}, inplace = True)
    
    #generate the auto incremental ID as in the original file, States' attributes are a part of the stores table
    df['state_id'] = np.arange(0, 0 + len(df)) + 1

    #save to database
    df.to_sql(name = 'state', con = conn, if_exists = 'append', index = False)

    return df


def cities_tbl(df):
    """The function saves cities details to mysql cities table"""
    df = df[["City Name", "State", "Type"]].drop_duplicates(subset = "City Name")
       
    #generate the auto incremental ID as in the original file, Cities' attributes are a part of the stores table 
    df['city_id'] = np.arange(0, 0 + len(df)) + 1
    
    states = states_tbl(stores)
    
    #merge existing states data with cities data to get a state ID
    df = pd.merge(df, states,  left_on='State', right_on='state')
    
    #rename multiple column names by label
    df.rename(columns={'City Name':'city_name', 'Type':'type'}, inplace = True)
    
    #save to database
    df = df[['city_id', 'city_name', 'type', 'state_id']]
    df.to_sql(name = 'city', con = conn, if_exists = 'append', index = False)

    return df


def channel_tbl(df):
    """The function saves sales details to mysql sales channel table"""

    df = df[["Sales Channel"]].drop_duplicates(subset = "Sales Channel")

    #generate the auto incremental ID as in the original file, Sales Channels' attributes are a part of the main table
    df['sales_channel_id'] = np.arange(0, 0 + len(df)) + 1

    #rename multiple column names by label
    df.rename(columns={'Sales Channel':'sales_channel_name'}, inplace = True)
    
    #save to database
    df.to_sql(name = 'sales_channel', con = conn, if_exists = 'append', index = False)

    return df


def products_tbl(df):
    """The function saves products details to mysql products table"""

    #rename multiple column names by label
    df.rename(columns={'_ProductID':'product_id', 'Product Name':'product_name'}, inplace = True)
    
    #save to database
    df.to_sql(name = 'product', con = conn, if_exists = 'append', index = False)

    return df


def stores_tbl(df):
    """The function saves stores details to mysql stores table"""
    cities = cities_tbl(stores)

    #merge existing states data with cities data to get a state ID
    df = pd.merge(df, cities, left_on = 'City Name', right_on = 'city_name')
    
    #rename multiple column names by label
    df.rename(columns={'_StoreID':'store_id', 'County':'location', 'Latitude':'latitude', 'Longitude':'longitude'}, inplace = True)

    #save to database
    df = df[['store_id', 'latitude', 'longitude', 'location', 'city_id']]
    df.to_sql(name = 'store', con = conn, if_exists = 'append', index = False)

    return df


def employees_tbl(df, main_dataset):
    """The function saves employees details to mysql employees table"""
    main = main_dataset[["_SalesTeamID", "_StoreID"]].drop_duplicates(subset = "_SalesTeamID")

    #split the full name column to first name & last name
    df[['employee_first_name', 'employee_last_name']] = df['Sales Team'].str.split(' ', expand = True)
    
    #merge existing employee data with sales order data to get a store ID
    df = pd.merge(df, main, on = '_SalesTeamID')

    #rename multiple column names by label
    df.rename(columns={'_SalesTeamID':'employee_id', '_StoreID': 'store_id'}, inplace = True)
    
    #save to database
    df = df[['employee_id', 'employee_first_name', 'employee_last_name', 'store_id']]
    df.to_sql(name = 'employee', con = conn, if_exists = 'append', index = False)

    return df


def orders_tbl(df):
    """The function saves orders details to mysql salesorders table"""
    channels = channel_tbl(basic)

    #merge existing basic data with channels data to get a channel ID
    df = pd.merge(df, channels, left_on = 'Sales Channel', right_on = 'sales_channel_name' )    

    #rename multiple column names by label
    df.rename(columns={'OrderNumber':'order_num', 'Order Quantity':'order_quantity',
                       'OrderDate':'order_date','CurrencyCode':'currency_code',
                       'ShipDate':'ship_date','DeliveryDate':'delivery_date','TotalCost':'total_cost','TotalPrice':'total_price',
                                   'ProcuredDate':'procure_date',
                                   'Discount Applied':'discount_applied', '_SalesTeamID':'employee_id',
                                   '_CustomerID':'customer_id', '_ProductID':'product_id'}, inplace = True)
    
    #save to database
    df = df[['order_num', 'order_date', 'currency_code', 'order_quantity', 'discount_applied', 'ship_date',
                                        'delivery_date', 'procure_date', 'total_cost', 'total_price', 'employee_id',
                                          'customer_id', 'sales_channel_id', 'product_id']]
    df.to_sql(name = 'sales_order', con = conn, if_exists = 'append', index = False)

    return df


def main():
    customers_tbl(customers)
    products_tbl(products)
    stores_tbl(stores)
    employees_tbl(employees, basic)    
    orders_tbl(basic)
if __name__ == '__main__':
    main()