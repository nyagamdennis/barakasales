# your_app/tasks.py
from celery import shared_task
from .models import Customer, Purchase
from prophet import Prophet
from .models import Prediction  # where you store predictions
import pandas as pd

@shared_task
def retrain_prophet_model(customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        purchases = Purchase.objects.filter(customer=customer).order_by("created_at")
        
        if purchases.count() < 3:
            return  # Not enough data to model

        df = pd.DataFrame(list(purchases.values("created_at", "amount")))
        df.rename(columns={"created_at": "ds", "amount": "y"}, inplace=True)

        model = Prophet()
        model.fit(df)

        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        next_date = forecast["ds"].iloc[-1]

        Prediction.objects.create(customer=customer, predicted_date=next_date)

    except Customer.DoesNotExist:
        pass
