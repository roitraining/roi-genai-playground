#!/bin/bash
set -e

gcloud run deploy $_SERVICE_NAME --platform=managed \
    --image=$_AR_HOSTNAME/$PROJECT_ID/cloud-run-source-deploy/$REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA \
    --labels=managed-by=gcp-cloud-build-deploy-cloud-run,commit-sha=$COMMIT_SHA,gcb-build-id=$BUILD_ID,gcb-trigger-id=$_TRIGGER_ID \
    --region=$_DEPLOY_REGION \
    --ingress=internal-and-cloud-load-balancing \
    --min-instances=1 \
    --max-instances=10 \
    --set-env-vars=GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_PROJECT_NUMBER=$PROJECT_NUMBER,GOOGLE_CLOUD_REGION=$_DEPLOY_REGION \
    --quiet
    
gcloud run services update-traffic $_SERVICE_NAME --to-latest --region=$_DEPLOY_REGION
