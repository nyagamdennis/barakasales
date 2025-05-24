import pandas as pd
from BarakaApp.models import SalesTab


def get_customer_sales_dataframe(customer_id):
    """
    Build a DataFrame with columns ['ds', 'y'] for Prophet.
    """
    sales = (
        SalesTab.objects
        .filter(customer_id=customer_id)
        .order_by('date_sold')
    )
    if not sales.exists():
        return None

    df = pd.DataFrame.from_records(
        sales.values('date_sold', 'total_amount'),
        columns=['date_sold', 'total_amount']
    )
    df.rename(columns={'date_sold': 'ds', 'total_amount': 'y'}, inplace=True)
    df.dropna(subset=['y'], inplace=True)
    df = df[df['y'] > 0]
    print('data frame ', df)
    return df