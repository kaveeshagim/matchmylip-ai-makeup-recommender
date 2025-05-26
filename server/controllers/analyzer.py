import cv2
import numpy as np
import mediapipe as mp

# Predefined lipstick shades (name + hex color)
LIPSTICK_SHADES = [
    {
        "name": "MAC Ruby Woo",
        "hex": "#b32b2b",
        "image": "https://m.maccosmetics.com/media/export/cms/products/640x600/mac_sku_M6JC01_640x600_0.jpg",
        "link": "https://www.maccosmetics.com/product/13854/310/products/makeup/lips/lipstick/lipstick#/shade/Ruby_Woo"
    },
    {
        "name": "Maybelline Touch of Spice",
        "hex": "#a05d56",
        "image": "https://www.maybelline.com/~/media/mny/us/products/lips/lip-color/color-sensational-creamy-matte-lipstick/maybelline-lipstick-color-sensational-creamy-matte-touch-of-spice-041554433235-o.jpg",
        "link": "https://www.maybelline.com/lip-makeup/lipstick/color-sensational-creamy-matte-lipstick/touch-of-spice"
    },
    {
        "name": "NYX Soft Matte Cannes",
        "hex": "#c37c74",
        "image": "https://www.nyxcosmetics.com/dw/image/v2/BBLC_PRD/on/demandware.static/-/Sites-cpd-nyx-master-catalog/default/dw4c40533e/images/hi-res/SMLC19.jpg",
        "link": "https://www.nyxcosmetics.com/lip/lipstick/soft-matte-lip-cream/NYX_003.html"
    },
    {
        "name": "MAC Velvet Teddy",
        "hex": "#c58c85",
        "image": "https://m.maccosmetics.com/media/export/cms/products/640x600/mac_sku_M6JC19_640x600_0.jpg",
        "link": "https://www.maccosmetics.com/product/13854/310/products/makeup/lips/lipstick/lipstick#/shade/Velvet_Teddy"
    },
    {
        "name": "Fenty Beauty Uncensored",
        "hex": "#b80f0a",
        "image": "https://www.fentybeauty.com/dw/image/v2/AAJB_PRD/on/demandware.static/-/Sites-itemmaster_fenty/default/dw2402c539/hi-res/FB30001-FB2001_1.jpg",
        "link": "https://www.fentybeauty.com/stunna-lip-paint-longwear-fluid-lip-color/FB30001.html"
    },
    {
        "name": "Huda Bombshell",
        "hex": "#d1a29a",
        "image": "https://static.beautybay.com/media/catalog/product/cache/1/small_image/500x500/9df78eab33525d08d6e5fb8d27136e95/h/u/huda0054f_image_1.jpg",
        "link": "https://hudabeauty.com/us/en_US/bombshell-liquid-matte-lipstick"
    },
    {
        "name": "Charlotte Tilbury Pillow Talk",
        "hex": "#ce8e8e",
        "image": "https://www.charlottetilbury.com/media/catalog/product/cache/5/image/1000x/040ec09b1e35df139433887a97daa66f/p/i/pillow_talk_original_lipstick_packshot_1.jpg",
        "link": "https://www.charlottetilbury.com/us/product/matte-revolution-pillow-talk-original"
    }
]

def analyze_image(image_file):
    # Convert image to OpenCV format
    image_bytes = image_file.read()
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        return {"error": "Failed to read image"}

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)

    results = face_mesh.process(img_rgb)
    if not results.multi_face_landmarks:
        return {"error": "No face detected"}

    landmarks = results.multi_face_landmarks[0]
    undertone = detect_undertone(img_rgb, landmarks, img.shape)


    # Get lip landmark indices
    lip_indices = list(set(mp_face_mesh.FACEMESH_LIPS))

    lip_coords = []
    for pair in lip_indices:
        for idx in pair:
            x = int(landmarks.landmark[idx].x * img.shape[1])
            y = int(landmarks.landmark[idx].y * img.shape[0])
            lip_coords.append((x, y))

    # Bounding box
    xs = [pt[0] for pt in lip_coords]
    ys = [pt[1] for pt in lip_coords]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    # Crop the lips
    lip_crop = img[y_min:y_max, x_min:x_max]

    if lip_crop.size == 0:
        return {"error": "Failed to crop lips"}

    # Calculate average color
    avg_color_per_row = np.average(lip_crop, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    b, g, r = [int(c) for c in avg_color]

    lip_rgb = (r, g, b)

    # Find closest 3 shades
    shade_distances = []
    for shade in LIPSTICK_SHADES:
        dist = color_distance(lip_rgb, hex_to_rgb(shade["hex"]))
        shade_distances.append((dist, shade))

    shade_distances.sort()

    # Normalize distances for scoring
    max_distance = max([d[0] for d in shade_distances[:5]]) or 1  # prevent divide by 0

    recommended = []
    for dist, shade in shade_distances[:3]:
        confidence = round((1 - dist / max_distance) * 100)
        recommended.append({
            "name": shade["name"],
            "hex": shade["hex"],
            "image": shade["image"],
            "link": shade["link"],
            "confidence": confidence
        })


    return {
        "status": "Lip color extracted",
        "lip_bbox": {
            "x": x_min,
            "y": y_min,
            "width": x_max - x_min,
            "height": y_max - y_min
        },
        "average_lip_color": {
            "r": r,
            "g": g,
            "b": b
        },
        "hex": "#{:02x}{:02x}{:02x}".format(r, g, b),
        "undertone": undertone,
        "recommended_shades": recommended
    }


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def color_distance(c1, c2):
    return np.sqrt(sum((e1 - e2) ** 2 for e1, e2 in zip(c1, c2)))

def detect_undertone(img_rgb, landmarks, image_shape):
    h, w, _ = image_shape

    # Sample cheek regions
    cheek_indices = [234, 454]  # left and right cheek outer points

    pixels = []
    for idx in cheek_indices:
        x = int(landmarks.landmark[idx].x * w)
        y = int(landmarks.landmark[idx].y * h)
        if 0 <= x < w and 0 <= y < h:
            pixels.append(img_rgb[y, x])

    if not pixels:
        return "unknown"

    avg_color = np.mean(pixels, axis=0).astype(np.uint8)
    avg_hsv = cv2.cvtColor(np.uint8([[avg_color]]), cv2.COLOR_RGB2HSV)[0][0]

    hue, sat, _ = avg_hsv

    # Simple rule-based logic
    if sat >= 40:
        return "warm" if hue < 30 or hue > 150 else "cool"
    else:
        return "neutral"
