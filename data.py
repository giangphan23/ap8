# %% --------------------------------
# import
import numpy as np
import pandas as pd
import plotly.express as px

# %% transactional data
fact_order = pd.read_pickle('data/fact_order.pkl')
fact_order.head().T
cols = [
    'order_id',
    'actual_revenue',
    'store_id',
    'is_promotion',
    'created_at', ]

fact_order_cleaned = (fact_order
                      .loc[fact_order['actual_revenue'] <= 20000000, cols]
                      .set_index('order_id')
                      .dropna())
fact_order_cleaned = fact_order_cleaned.astype({'store_id': 'object',
                                                'is_promotion': 'bool',
                                                'created_at': 'datetime64'})

fact_order_cleaned = fact_order_cleaned.loc[fact_order_cleaned['created_at'].between(
    pd.Timestamp('2017-08-01'), pd.Timestamp('2021-04-01')), :]

fact_order_cleaned.info()

# %%
fact_order_cleaned.set_index('created_at', inplace=True)
gr = fact_order_cleaned.groupby('store_id')

fact_order_daily_sum = (gr.resample('D')
                        .sum()
                        # .drop(columns='store_id')
                        .reset_index(level=0)
                        .rename({'actual_revenue': 'sales',
                                 'is_promotion': 'promo_count'}, axis=1)
                        )

# filter out stores closed before Mar 2021
gr = fact_order_daily_sum.groupby('store_id')
fact_order_daily_sum = gr.filter(lambda x: (
    x.last('D').index.to_period('M') >= pd.Period('2021-03'))[0])

fact_order_daily_sum['store_id'].unique().shape  # 53 remaining stores
fact_order_daily_sum['store_id'] = fact_order_daily_sum['store_id'].astype('int').astype('object')

# plot store sales time series on the same index
fig_1 = px.line(fact_order_daily_sum.reset_index(),
              x='created_at', y='sales', color='store_id')
fig_1.update_xaxes(
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ])))
fig_1.show()


fig_2 = px.scatter(fact_order_daily_sum, x='sales', y='promo_count', color='store_id')
fig_2.show()


# %% store data
dim_store = pd.read_csv('data/dim_store.csv')
cols = ['store_name',
        'store_group',
        'store_format',
        'store_level',
        'store_segment',
        'opening_date',
        'store_area',
        'number_of_staff',
        'province',
        'channel']

# stores present in fact_order_daily_sum
dim_store = dim_store.set_index(
    'store_id').loc[fact_order_daily_sum['store_id'].unique(), cols]
dim_store.info()

