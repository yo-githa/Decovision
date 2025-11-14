import replicate
import replicate

# This will automatically pick the token from the environment variable
client = replicate.Client()

# 🔐 Set your Replicate API token

# 🔄 Load the model (Stable Diffusion Img2Img)
model = replicate.models.get("stability-ai/stable-diffusion")

# Run inference
output = model.predict(
    input_image="https://replicate.delivery/pbxt/YOUR_INPUT_IMAGE.jpg",  # or local file via upload
    prompt="a cozy living room in boho style with warm lighting",
    strength=0.75,
    num_outputs=1
)

print("Generated image link:", output[0])
