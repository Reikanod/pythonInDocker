import os
from runwayml import RunwayML

client = RunwayML(
    api_key=os.environ.get("RUNWAY_API_KEY"),  # This is the default and can be omitted
)

image_to_video = client.image_to_video.create(
    model="gen4_turbo",
    prompt_image="https://i.ytimg.com/vi/sRFsTCF2sW8/maxresdefault.jpg",
    ratio="720:1280",
    prompt_text="The man is walking away",
)
print(image_to_video.id)
