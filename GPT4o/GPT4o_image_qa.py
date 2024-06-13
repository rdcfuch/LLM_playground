import base64

from openai import OpenAI
import os

MODEL = "gpt-4o"
openai_api_key = "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"

client = OpenAI(api_key=openai_api_key)

# 1 basic chat

# completion = client.chat.completions.create(
#     model=MODEL,
#     messages=[
#         {"role": "system", "content": "you are a realty expert and you can give me advice about house buying"},
#         {"role": "user",
#          "content": "what is the average price for Fremont houses with 3 bedroom, 2 bathroom, sqft 1500?"}
#     ]
# )

# print(completion.choices[0].message.content)

# 2 image processing local Base64

IMG = "page8_img1.png"


def encode_image(image_file):
    with open(image_file, 'rb') as img:
        return base64.b64encode(img.read()).decode("utf-8")


encoded_image = encode_image(IMG)

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "you are a realty expert and you can give me advice about house buying"},
        {"role": "user", "content":
            [
                #{"type": "text", "text": "What is in this image?"},
                {"type": "text", "text": "Is this a map of plot plan?"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
            ]
         }
    ],
    temperature=0
)

print(response.choices[0].message.content)



# 3 - Image Processing: URL
# response = client.chat.completions.create(
#     model=MODEL,
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant that responds in Markdown. Help me with my math homework!"},
#         {"role": "user", "content": [
#             {"type": "text", "text": "What's the area of the triangle?"},
#             {"type": "image_url", "image_url": {"url": "https://upload.wikimedia.org/wikipedia/commons/e/e2/The_Algebra_of_Mohammed_Ben_Musa_-_page_82b.png"}
#             }
#         ]}
#     ],
#     temperature=0.0,
# )
#
# print(response.choices[0].message.content)
