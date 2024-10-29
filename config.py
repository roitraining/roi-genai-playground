import os
from google.cloud import secretmanager

project_id = os.environ['GOOGLE_CLOUD_PROJECT']
region = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
restricted = os.getenv('RESTRICTED', 'FALSE').upper()


# collect secrets from Secret Manager
secrets = {}
client = secretmanager.SecretManagerServiceClient()
parent = f"projects/{project_id}"
for secret in client.list_secrets(request={"parent": parent}):
    secret_name = client.parse_secret_path(secret.name)["secret"]
    version_path = f"{secret.name}/versions/latest"
    response = client.access_secret_version(request={"name": version_path})
    secrets[secret_name] = response.payload.data.decode("UTF-8")

# collect markdown files
dir_path = "./"
files = os.listdir(dir_path)
md_files = [f for f in files if f.endswith('.md')]
md_dict = {}
for f in md_files:
    key = os.path.splitext(f)[0]
    with open(os.path.join(dir_path, f), 'r') as file:
        md_dict[key] = file.read()

chat_models = {
    'GPT-4o': 'gpt-4o',
    'Gemini 1.5 Flash': 'gemini-1.5-flash',
}

text_models = {
    'GPT-4o': 'gpt-4o',
    'Gemini 1.5 Flash': 'gemini-1.5-flash',
}

image_models = {
    "Dall-E 3": "dall-e-3",
}

if restricted == 'FALSE':
    chat_models['Claude 3.5 Sonnet'] = "claude-3-5-sonnet-v2@20241022"
    text_models['Claude 3.5 Sonnet'] = "claude-3-5-sonnet-v2@20241022"
    # Uncomment below to add older version of Imagen
    # image_models['Imagen 2'] = "imagegeneration@006"
    image_models['Imagen 3 Fast'] = "imagen-3.0-fast-generate-001"
    image_models['SD3 Large Turbo'] = "sd3-large-turbo"


gemini_models = [
    'Gemini 1.5 Pro',
    'Gemini 1.5 Flash',
    'Gemini 1.0 Pro'
]

non_gemini_google_models = [
    'PaLMv2',
    'Codey',
]

openai_models = [
    'GPT-4 Turbo',
    'GPT-3.5 Turbo',
    'GPT-4o',
    'GPT-4o mini'
]

claude_models = [
    'Claude 3 Opus',
    'Claude 3.5 Sonnet',
    'Claude 3 Haiku'
]

codey_models = [
    'Codey'
]

google_image_models = [
    "Imagen 2",
    "Imagen 3 Fast",
]

openai_image_models = [
    "Dall-E 3"
]

stability_image_models = [
    "SD3 Large Turbo"
]