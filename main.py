import io
import requests
import streamlit as st

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from PIL import Image, ImageDraw, ImageFont


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Diwali Wishes Generator",
    page_icon="🪔",
    layout="wide"
)


# =====================================================
# 2. FESTIVE THEME STYLING
# =====================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            135deg, #1a0000 0%, #330000 50%, #1a0500 100%
        );
        color: #fff5e6;
    }

    h1 {
        color: #ff9933 !important;
        text-shadow: 0px 2px 4px rgba(255,153,51,0.4);
        font-family: serif;
    }

    h2, h3 {
        color: #ffcc66 !important;
    }

    .stSelectbox label {
        color: #ffcc66 !important;
        font-weight: 600;
    }

    .stButton button, .stDownloadButton button {
        background: linear-gradient(
            90deg, #ff8000 0%, #ff3300 100%
        );
        color: white;
        border: none;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }

    .stButton button:hover,
    .stDownloadButton button:hover {
        background: linear-gradient(
            90deg, #ff9933 0%, #ff4d4d 100%
        );
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# 3. GOOGLE API KEY
# =====================================================

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]


# =====================================================
# 4. OVHCLOUD IMAGE GENERATION & DEITY PROMPTS
# =====================================================

OVH_IMAGE_URL = (
    "https://stable-diffusion-xl.endpoints."
    "kepler.ai.cloud.ovh.net/api/text2image"
)

DEITY_PROMPTS = {
    "Lord Ganesh": (
        "A majestic, divine depiction of Lord Ganesha with an elephant head, "
        "gentle expression, golden crown, holding a modak, soft warm divine halo, "
        "surrounded by glowing diyas and marigold flowers."
    ),
    "Hanuman": (
        "A divine and powerful depiction of Lord Hanuman as a noble vanara warrior "
        "with a serene and devoted expression, muscular physique, wearing traditional ornaments, "
        "holding a golden mace (gada), with a glowing divine aura and sacred background."
    ),
    "Lord Shiva": (
        "A majestic depiction of Lord Shiva as a serene ascetic god with ash on his forehead, "
        "a crescent moon and matted hair, a glowing third eye, peaceful meditative expression, "
        "blue neck shade, holding a trishula (trident), divine spiritual aura."
    ),
    "Sai Baba": (
        "A revered spiritual saint in traditional white robe and headwear, "
        "serene, compassionate and peaceful expression, sitting gracefully with a warm divine background."
    ),
    "Goddess Durga": (
        "A powerful multi-armed warrior goddess riding a majestic lion, "
        "holding sacred weapons and a lotus, wearing rich traditional silk attire and jewelry, "
        "divine glowing aura."
    ),
    "Goddess Lakshmi": (
        "A radiant divine goddess of wealth seated on a pink lotus flower, "
        "gently showering gold coins from her hand, wearing rich traditional Indian attire and jewelry, "
        "surrounded by glowing lamps."
    ),
    "Goddess Saraswathi": (
        "A graceful goddess of knowledge seated on a white lotus, playing a classical veena instrument, "
        "wearing a pure white silk saree, calm and wise expression, serene divine background."
    ),
    "Lord Ram": (
        "A noble and heroic prince with a divine crown, calm and righteous expression, "
        "holding a traditional bow and arrow, glowing radiant aura and festive background."
    )
}


def load_font(size):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf"
    ]

    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue

    return ImageFont.load_default()


def fit_font(draw, text, max_width, starting_size):
    size = starting_size
    while size >= 12:
        font = load_font(size)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
        size -= 2
    return load_font(12)


def add_diwali_text(image):
    image = image.convert("RGB")
    width, height = image.size
    draw = ImageDraw.Draw(image, "RGBA")

    banner_width = int(width * 0.90)
    banner_height = int(height * 0.21)

    left = (width - banner_width) // 2
    top = height - banner_height - int(height * 0.045)
    right = left + banner_width
    bottom = top + banner_height

    draw.rounded_rectangle(
        (left, top, right, bottom),
        radius=max(12, width // 35),
        fill=(30, 5, 0, 225),
        outline=(255, 190, 65, 255),
        width=max(2, width // 180)
    )

    title = "HAPPY DIWALI"
    subtitle = "Wishing You Happiness & Prosperity"

    title_font = fit_font(
        draw, title, int(banner_width * 0.88), max(24, width // 13)
    )
    subtitle_font = fit_font(
        draw, subtitle, int(banner_width * 0.90), max(14, width // 30)
    )

    center_x = width // 2

    draw.text(
        (center_x, top + int(banner_height * 0.36)),
        title,
        font=title_font,
        fill=(255, 211, 91, 255),
        anchor="mm",
        stroke_width=max(1, width // 300),
        stroke_fill=(90, 20, 0, 255)
    )

    draw.text(
        (center_x, top + int(banner_height * 0.73)),
        subtitle,
        font=subtitle_font,
        fill=(255, 255, 255, 255),
        anchor="mm"
    )

    return image


def generate_diwali_image(prompt):
    headers = {
        "Accept": "application/octet-stream",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "negative_prompt": (
            "blurry, low quality, distorted faces, deformed limbs, "
            "bad anatomy, watermark, text, letters, ugly, mutant"
        )
    }

    response = requests.post(
        OVH_IMAGE_URL,
        headers=headers,
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    image = Image.open(io.BytesIO(response.content))
    image.load()

    return add_diwali_text(image)


# =====================================================
# 5. MAIN APPLICATION
# =====================================================

col1, col2 = st.columns(2, gap="large")

with col1:
    st.title("Happy Diwali Kusuma🥰❤️")
    st.write("🪔 Here you can create your personalized Diwali wishes🌸❤️")
    st.write("Please select all options and click on generate button😊")
    st.markdown("---")

    Color = st.selectbox(
        "Select your favorite color😊",
        ["green", "blue", "pink", "orange", "maroon"]
    )

    God = st.selectbox(
        "Pick your favorite God😊",
        [
            "Lord Ganesh",
            "Hanuman",
            "Lord Shiva",
            "Sai Baba",
            "Goddess Durga",
            "Goddess Lakshmi",
            "Goddess Saraswathi",
            "Lord Ram"
        ]
    )

    Language = st.selectbox(
        "Pick any language😊",
        ["Kannada", "Telugu", "English", "Hindi"]
    )

    st.markdown("")
    generate_button = st.button("✨ Generate My Diwali Wish ✨")


# =====================================================
# 6. RIGHT COLUMN
# =====================================================

with col2:
    st.subheader("🌟 Diwali Blessing for you🥰😊")

    if not generate_button:
        st.markdown("### 🪔✨ Happy Diwali ✨🪔")
        st.write("Select your favorite color, God and language.")
        st.write("Your personalized Diwali blessing and beautiful AI-generated artwork will appear here. ❤️")
        st.markdown("### 🪔 🌸 🎆 ❤️")

    else:
        st.markdown("### 🪔 Your Personalized Blessing")

        with st.spinner("✨ Lighting up diyas and crafting your wish..."):
            try:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-3.5-flash-lite",
                    temperature=0.7,
                    google_api_key=GOOGLE_API_KEY
                )

                pt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            "You are a warm, traditional festival poet. "
                            "Write a short, heartfelt Diwali blessing "
                            "in {Language} focusing on {God}. "
                            "Dedicated to a kind-hearted girl Kusuma. "
                            "Return only the plain text poem/message."
                        ),
                        (
                            "human",
                            "Create a blessing wishing prosperity, health, and light."
                        )
                    ]
                )

                chain = pt | llm
                response = chain.invoke({"Language": Language, "God": God})

                message = response.content if hasattr(response, "content") else str(response)

                st.markdown(
                    f"""
                    <div style='
                        background-color: rgba(255,153,51,0.1);
                        padding: 20px;
                        border-radius: 10px;
                        border-left: 5px solid #ff9933;
                        margin-bottom: 20px;
                        white-space: pre-wrap;
                        color: #fff5e6;
                    '>{message}</div>
                    """,
                    unsafe_allow_html=True
                )

            except Exception as e:
                st.error(f"Wish generation failed: {e}")

        st.markdown("### 🎨 Your Personalized Diwali Artwork")

        god_description = DEITY_PROMPTS.get(God, f"A respectful divine depiction of {God}.")

        image_prompt = (
            "A high-resolution professional digital painting "
            "of an Indian Diwali celebration with glowing traditional diyas, "
            "colorful fireworks in a starry night sky, elegant golden rangoli, "
            "marigold flowers, warm golden ambient light and festive decorations. "
            f"The dominant color theme is {Color}. "
            f"{god_description} "
            "Cinematic composition, highly detailed, vibrant colors, masterpiece. "
            "Leave clear space near the bottom for a greeting banner. "
            "Do not generate any random text, words, letters or watermark."
        )

        with st.spinner(f"🎨 Creating a beautiful Diwali image featuring {God}..."):
            try:
                generated_image = generate_diwali_image(image_prompt)

                st.image(
                    generated_image,
                    caption=f"Diwali artwork featuring {God}",
                    use_container_width=True
                )

                image_buffer = io.BytesIO()
                generated_image.save(image_buffer, format="PNG")
                image_buffer.seek(0)

                st.download_button(
                    label="⬇️ Download Your Diwali Image",
                    data=image_buffer.getvalue(),
                    file_name="Kusuma_Diwali_Wishes.png",
                    mime="image/png",
                    use_container_width=True
                )

                st.success("Your personalized Diwali artwork is ready! ❤️")

            except requests.exceptions.Timeout:
                st.error("Image generation timed out. Please try again.")
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response is not None else "Unknown"
                st.error(f"OVHcloud image generation failed: HTTP {status_code}")
                if e.response is not None:
                    st.code(e.response.text[:2000])
            except Exception as e:
                st.error(f"Image generation failed: {e}")
