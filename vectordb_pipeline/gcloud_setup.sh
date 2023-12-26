# create a bucket to store the data
gsutil mb -l us-central1 gs://griller_data

#create notification configuration for the data bucket
gsutil notification create -f json -t data_updated_topic gs://griller_data/

#Grant the Cloud Function permission to publish to the Pub/Sub topic
gcloud projects add-iam-policy-binding griller-490718 \
--member serviceAccount:$SERVICE_ACCOUNT \   #change the service account
--role roles/pubsub.publisher

# create a cloud function to trigger airflow dag upon 
# data update in the bucket

gcloud functions deploy db_update_function  \
--runtime python310 \
--trigger-resource gs://griller_data/ \
--trigger-event google.storage.object.finalize \
--entry-point gcloud_function \
--service-account $SERVICE_ACCOUNT