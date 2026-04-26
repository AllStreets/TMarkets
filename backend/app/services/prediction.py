from app.workers.celery_app import celery

@celery.task(name="app.services.prediction.run_prediction_pipeline")
def run_prediction_pipeline(signal_id: int):
    pass  # implemented in Task 6
