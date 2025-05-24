# your_app/tasks.py
from celery import shared_task
from BarakaApp.models import Customers, SalesTab
from prophet import Prophet
from .models import Prediction  # where you store predictions
import pandas as pd

@shared_task
def retrain_prophet_model(customer_id):
    print('CELERY TASK CALLED WITH ID:', customer_id)
    try:
        customer = Customers.objects.get(id=customer_id)
        purchases = SalesTab.objects.filter(customer=customer).order_by("date_sold")
        print('Purchase history ', purchases)

        if purchases.count() < 3:
            print('Not enough data to train.')
            return

        df = pd.DataFrame(list(purchases.values("date_sold", "total_amount")))
        df.rename(columns={"date_sold": "ds", "total_amount": "y"}, inplace=True)

        # Remove timezone awareness
        df["ds"] = pd.to_datetime(df["ds"]).dt.tz_localize(None)

        print('Cleaned DataFrame:', df)

        model = Prophet()
        model.fit(df)

        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        next_date = forecast["ds"].iloc[-1]

        Prediction.objects.create(customer=customer, predicted_date=next_date)

    except Customers.DoesNotExist:
        print(f'Customer with ID {customer_id} does not exist.')
