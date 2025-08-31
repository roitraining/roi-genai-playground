# ROI Training Generative AI Playground

A fun little demo app that shows chat, text, and image generation
using various models.

# To Run

### Create a virtual Environment
```
python3 -m venv ~/genai-demo-env
source ~/genai-demo-env/bin/activate
```


### Install the requirements
```
pip install -r requirements.txt 
```

### OpenAI API Key  Secret
In the project you are using you need an OpenAI API Key. Create this in Secret Manager. Use the key name: `openai_api_key`


### Environment Variables
You need an environment variables with your Project ID adn Regions

```
export GOOGLE_CLOUD_PROJECT='roidtc-genai-playground'
export GOOGLE_CLOUD_REGION='us-central1'
export RESTRICTED=FALSE
```

### Start the Program

```
streamlit run Chatbot.py
```

### Create Artifact Registry, Build and Push

```
gcloud artifacts repositories create roi-genai-app-docker-repo --repository-format=docker --location=us-central1 --description="Docker repository for ROI GenAI App"
```

```
gcloud builds submit --region=us-central1 --tag us-central1-docker.pkg.dev/roidtc-genai-playground/roi-genai-app-docker-repo/roi-genai-app-image:v1.1
```