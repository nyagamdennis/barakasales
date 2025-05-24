from prophet import Prophet
from BarakaApp.models import Customers
from sales_ai.models import Prediction
from sales_ai.services.data import get_customer_sales_dataframe


def train_and_predict_customer(customer_id, periods=30):
    """
    Train Prophet on a customer's sales history and store the next predicted date.
    """
    try:
        customer = Customers.objects.get(id=customer_id)
    except Customers.DoesNotExist:
        return

    df = get_customer_sales_dataframe(customer_id)
    if df is None or len(df) < 3:
        return

    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    next_date = forecast['ds'].iloc[-1]

    Prediction.objects.update_or_create(
        customer=customer,
        defaults={'predicted_date': next_date}
    )