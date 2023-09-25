for PROJECT in $(gcloud projects list --format='value(projectId)') ;
do for BUCKET in $(gsutil ls -l -b -p $PROJECT gs://) ;
do gsutil -m du -s  $BUCKET | xargs -i echo "$PROJECT,{} " >> bucket_detail_new.csv ;
done ;
done ;

gcloud config set account space-usage@gcp-wow-rwds-ai-bi-prod.iam.gserviceaccount.com
gcloud auth activate-service-account --project=1060770463555 --key-file=spaceusagekey.json
for PROJECT in $(gcloud projects list --format='value(projectId)'); do   for BUCKET in $(gsutil ls -l -b -p $PROJECT gs://);   do     gsutil -m du -s  $BUCKET | xargs -i echo "$PROJECT,{} " >> bucket_size1.csv ;   done; done