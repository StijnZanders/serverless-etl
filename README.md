Create a file called `limber.yaml` with the following configuration:

```
cloud:
    provider: google
    project: "<project name>"
    region: "europe-west1"
    key_file: "<path to key_file>"
    default_bucket: "<gcp cloud storage bucket name>"
```
    
In the main directory run:
1. python -m limber init
2. python -m limber terraform login
3. python -m limber plan
4. python -m limber apply

Google Cloud APIs enabled
1. CloudFunctions API
2. PubSub API
3. CloudScheduler API
4. Cloud Build API
5. Secret manager API

Other
1. Create app engine in your project: https://console.cloud.google.com/appengine

Service account needed roles:
1. Pub/Sub Editor
2. Service Account User
3. Cloud Scheduler Admin
4. Cloud Functions Developer
5. Storage Admin
6. Secret Manager Admin