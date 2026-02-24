#!/usr/bin/env python3
"""Generate test images & videos across papergit projects to compare ComfyUI models.

Usage:
    python scripts/generate_test.py              # Generate all
    python scripts/generate_test.py images        # Images only
    python scripts/generate_test.py videos        # Videos only (requires images first)
    python scripts/generate_test.py --dry         # Print jobs without generating
"""

import json
import os
import random
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── Configuration ──────────────────────────────────────────────────────────

WRIGHT = "http://wright.gazelle-galaxy.ts.net:8188"
NEUMANN = "http://neumann.gazelle-galaxy.ts.net:8188"

# Model routing: FLUX → neumann (wright has attn_mask bug), SD3.5/z_turbo/Wan → wright
MODEL_SERVER = {
    "flux_dev": NEUMANN,
    "flux_schnell": NEUMANN,
    "sd35": WRIGHT,
    "z_turbo": WRIGHT,
    "wan_i2v": WRIGHT,
}

# Per-server model filenames (neumann has different naming)
NEUMANN_MODELS = {
    "flux_dev_unet": "flux1-dev-fp8-e4m3fn.safetensors",
    "flux_schnell_unet": "flux1-schnell-fp8-e4m3fn.safetensors",
    "t5xxl": "t5xxl_fp8_e4m3fn.safetensors",
}
WRIGHT_MODELS = {
    "flux_dev_unet": "flux1-dev-fp8.safetensors",
    "flux_schnell_unet": "flux1-schnell-fp8.safetensors",
    "t5xxl": "t5xxl_fp8_e4m3fn_scaled.safetensors",
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR = os.path.join(BASE_DIR, "test")

POLL_INTERVAL = 3
IMG_TIMEOUT = 300
VID_TIMEOUT = 2400

# Quality prefixes/suffixes for prompts
CIN_SUFFIX = (
    ", shot on ARRI Alexa 65, anamorphic lens, shallow depth of field, "
    "film grain, volumetric lighting, atmospheric haze, "
    "professional cinematography, 8K, hyperdetailed, photorealistic"
)
CIN_NEG = (
    "cartoon, anime, illustration, painting, drawing, blurry, out of focus, "
    "low quality, deformed, disfigured, text, watermark, signature, ugly, amateur"
)

WEB_SUFFIX = (
    ", vibrant saturated colors, dynamic composition, "
    "high quality digital art, detailed professional illustration"
)
WEB_NEG = (
    "photorealistic, photograph, 3d render, realistic skin, "
    "blurry, low quality, deformed, ugly, text, watermark"
)

# ─── Server Helpers ─────────────────────────────────────────────────────────


def get_available_servers():
    """Return list of online server URLs."""
    available = []
    for url in [WRIGHT, NEUMANN]:
        try:
            req = urllib.request.Request(f"{url}/queue")
            with urllib.request.urlopen(req, timeout=3) as resp:
                json.loads(resp.read())
            available.append(url)
        except Exception:
            pass
    return available


def submit_prompt(server_url, workflow):
    """Submit a workflow to the server, return prompt_id."""
    payload = json.dumps({"prompt": workflow}).encode()
    req = urllib.request.Request(
        f"{server_url}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    if "error" in data:
        raise RuntimeError(f"ComfyUI error: {data['error']}")
    return data["prompt_id"]


def poll_completion(server_url, prompt_id, timeout=IMG_TIMEOUT):
    """Poll /history until prompt is done. Return output info dict."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(f"{server_url}/history/{prompt_id}")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            if prompt_id in data:
                entry = data[prompt_id]
                status = entry.get("status", {})
                if status.get("completed", False):
                    return entry
                if status.get("status_str") == "error":
                    msgs = status.get("messages", [])
                    raise RuntimeError(f"Generation failed: {msgs}")
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            pass
        time.sleep(POLL_INTERVAL)
    raise TimeoutError(f"Prompt {prompt_id} timed out after {timeout}s")


def download_file(server_url, filename, subfolder, filetype, save_path):
    """Download a generated file from ComfyUI server."""
    params = urllib.parse.urlencode({
        "filename": filename,
        "subfolder": subfolder,
        "type": filetype,
    })
    url = f"{server_url}/view?{params}"
    urllib.request.urlretrieve(url, save_path)


def upload_image(server_url, image_path):
    """Upload an image to ComfyUI server's input directory. Return filename."""
    boundary = uuid.uuid4().hex
    filename = os.path.basename(image_path)
    with open(image_path, "rb") as f:
        image_data = f.read()

    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode()
    body += b"Content-Type: image/png\r\n\r\n"
    body += image_data
    body += f"\r\n--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="overwrite"\r\n\r\ntrue'.encode()
    body += f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"{server_url}/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    return result.get("name", filename)


# ─── Workflow Builders ──────────────────────────────────────────────────────


def workflow_flux_dev(prompt, width, height, seed):
    """FLUX.1 Dev: 20 steps, guidance 3.5, highest quality photorealistic."""
    models = NEUMANN_MODELS  # FLUX routed to neumann
    return {
        "1": {"class_type": "UNETLoader", "inputs": {
            "unet_name": models["flux_dev_unet"],
            "weight_dtype": "fp8_e4m3fn",
        }},
        "2": {"class_type": "DualCLIPLoader", "inputs": {
            "clip_name1": "clip_l.safetensors",
            "clip_name2": models["t5xxl"],
            "type": "flux",
        }},
        "3": {"class_type": "CLIPTextEncode", "inputs": {
            "text": prompt, "clip": ["2", 0],
        }},
        "4": {"class_type": "CLIPTextEncode", "inputs": {
            "text": "", "clip": ["2", 0],
        }},
        "5": {"class_type": "FluxGuidance", "inputs": {
            "guidance": 3.5, "conditioning": ["3", 0],
        }},
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {
            "width": width, "height": height, "batch_size": 1,
        }},
        "7": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": 20, "cfg": 1.0,
            "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
            "model": ["1", 0], "positive": ["5", 0],
            "negative": ["4", 0], "latent_image": ["6", 0],
        }},
        "8": {"class_type": "VAELoader", "inputs": {
            "vae_name": "ae.safetensors",
        }},
        "9": {"class_type": "VAEDecode", "inputs": {
            "samples": ["7", 0], "vae": ["8", 0],
        }},
        "10": {"class_type": "SaveImage", "inputs": {
            "filename_prefix": "gentest", "images": ["9", 0],
        }},
    }


def workflow_flux_schnell(prompt, width, height, seed):
    """FLUX.1 Schnell: 4 steps, no guidance, fast baseline."""
    models = NEUMANN_MODELS  # FLUX routed to neumann
    return {
        "1": {"class_type": "UNETLoader", "inputs": {
            "unet_name": models["flux_schnell_unet"],
            "weight_dtype": "fp8_e4m3fn",
        }},
        "2": {"class_type": "DualCLIPLoader", "inputs": {
            "clip_name1": "clip_l.safetensors",
            "clip_name2": models["t5xxl"],
            "type": "flux",
        }},
        "3": {"class_type": "CLIPTextEncode", "inputs": {
            "text": prompt, "clip": ["2", 0],
        }},
        "4": {"class_type": "CLIPTextEncode", "inputs": {
            "text": "", "clip": ["2", 0],
        }},
        "5": {"class_type": "EmptySD3LatentImage", "inputs": {
            "width": width, "height": height, "batch_size": 1,
        }},
        "6": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": 4, "cfg": 1.0,
            "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
            "model": ["1", 0], "positive": ["3", 0],
            "negative": ["4", 0], "latent_image": ["5", 0],
        }},
        "7": {"class_type": "VAELoader", "inputs": {
            "vae_name": "ae.safetensors",
        }},
        "8": {"class_type": "VAEDecode", "inputs": {
            "samples": ["6", 0], "vae": ["7", 0],
        }},
        "9": {"class_type": "SaveImage", "inputs": {
            "filename_prefix": "gentest", "images": ["8", 0],
        }},
    }


def workflow_sd35(prompt, neg_prompt, width, height, seed):
    """SD3.5 Large: 28 steps, cfg 4.5, cinematic aesthetic."""
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {
            "ckpt_name": "sd3.5_large_fp8_scaled.safetensors",
        }},
        "2": {"class_type": "CLIPTextEncode", "inputs": {
            "text": prompt, "clip": ["1", 1],
        }},
        "3": {"class_type": "CLIPTextEncode", "inputs": {
            "text": neg_prompt, "clip": ["1", 1],
        }},
        "4": {"class_type": "EmptySD3LatentImage", "inputs": {
            "width": width, "height": height, "batch_size": 1,
        }},
        "5": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": 28, "cfg": 4.5,
            "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
            "model": ["1", 0], "positive": ["2", 0],
            "negative": ["3", 0], "latent_image": ["4", 0],
        }},
        "6": {"class_type": "VAEDecode", "inputs": {
            "samples": ["5", 0], "vae": ["1", 2],
        }},
        "7": {"class_type": "SaveImage", "inputs": {
            "filename_prefix": "gentest", "images": ["6", 0],
        }},
    }


def workflow_z_turbo(prompt, width, height, seed):
    """z_image_turbo (Lumina2): 8 steps, fastest, manhwa-optimized."""
    return {
        "1": {"class_type": "UNETLoader", "inputs": {
            "unet_name": "z_image_turbo_bf16.safetensors",
            "weight_dtype": "default",
        }},
        "2": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": "qwen_3_4b.safetensors",
            "type": "lumina2",
        }},
        "3": {"class_type": "CLIPTextEncode", "inputs": {
            "text": prompt, "clip": ["2", 0],
        }},
        "4": {"class_type": "CLIPTextEncode", "inputs": {
            "text": "", "clip": ["2", 0],
        }},
        "5": {"class_type": "ModelSamplingAuraFlow", "inputs": {
            "shift": 3.0, "model": ["1", 0],
        }},
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {
            "width": width, "height": height, "batch_size": 1,
        }},
        "7": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": 8, "cfg": 1.0,
            "sampler_name": "res_multistep", "scheduler": "simple", "denoise": 1.0,
            "model": ["5", 0], "positive": ["3", 0],
            "negative": ["4", 0], "latent_image": ["6", 0],
        }},
        "8": {"class_type": "VAELoader", "inputs": {
            "vae_name": "ae.safetensors",
        }},
        "9": {"class_type": "VAEDecode", "inputs": {
            "samples": ["7", 0], "vae": ["8", 0],
        }},
        "10": {"class_type": "SaveImage", "inputs": {
            "filename_prefix": "gentest", "images": ["9", 0],
        }},
    }


def workflow_wan_i2v(motion_prompt, image_filename, seed, steps=20, length=49):
    """Wan 2.2 I2V 14B — official dual-expert MoE workflow.

    Uses BOTH high-noise and low-noise models with two-pass KSamplerAdvanced:
      Pass 1 (steps 0 to steps/2): High Noise expert — overall layout
      Pass 2 (steps/2 to steps):   Low Noise expert — detail refinement
    ModelSamplingSD3 shift=8.0 applied to both models. CFG=3.5 (official default).
    No CLIPVision — source image passed directly to WanImageToVideo.
    """
    half_steps = steps // 2
    neg_prompt = (
        "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，"
        "最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，"
        "画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，"
        "杂乱的背景，三条腿，背景人很多，倒着走"
    )
    return {
        # Load both expert models
        "1": {"class_type": "UNETLoader", "inputs": {
            "unet_name": "wan2.2_i2v_high_noise_14B_fp16.safetensors",
            "weight_dtype": "default",
        }},
        "2": {"class_type": "UNETLoader", "inputs": {
            "unet_name": "wan2.2_i2v_low_noise_14B_fp16.safetensors",
            "weight_dtype": "default",
        }},
        # ModelSamplingSD3 shift=8.0 for both
        "3": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": 8.0}},
        "4": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["2", 0], "shift": 8.0}},
        # Text encoder + VAE
        "5": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan",
        }},
        "6": {"class_type": "VAELoader", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
        # Prompts
        "7": {"class_type": "CLIPTextEncode", "inputs": {
            "text": motion_prompt, "clip": ["5", 0],
        }},
        "8": {"class_type": "CLIPTextEncode", "inputs": {
            "text": neg_prompt, "clip": ["5", 0],
        }},
        # Source image
        "9": {"class_type": "LoadImage", "inputs": {"image": image_filename}},
        # WanImageToVideo — no CLIPVision, direct image input
        "10": {"class_type": "WanImageToVideo", "inputs": {
            "positive": ["7", 0], "negative": ["8", 0], "vae": ["6", 0],
            "width": 832, "height": 480, "length": length, "batch_size": 1,
            "start_image": ["9", 0],
        }},
        # Pass 1: High Noise expert (steps 0 → half_steps)
        "11": {"class_type": "KSamplerAdvanced", "inputs": {
            "model": ["3", 0],
            "positive": ["10", 0], "negative": ["10", 1], "latent_image": ["10", 2],
            "noise_seed": seed, "steps": steps, "cfg": 3.5,
            "sampler_name": "euler", "scheduler": "simple",
            "add_noise": "enable", "start_at_step": 0, "end_at_step": half_steps,
            "return_with_leftover_noise": "enable",
        }},
        # Pass 2: Low Noise expert (half_steps → end)
        "12": {"class_type": "KSamplerAdvanced", "inputs": {
            "model": ["4", 0],
            "positive": ["10", 0], "negative": ["10", 1], "latent_image": ["11", 0],
            "noise_seed": seed, "steps": steps, "cfg": 3.5,
            "sampler_name": "euler", "scheduler": "simple",
            "add_noise": "disable", "start_at_step": half_steps, "end_at_step": 10000,
            "return_with_leftover_noise": "disable",
        }},
        "13": {"class_type": "VAEDecode", "inputs": {"samples": ["12", 0], "vae": ["6", 0]}},
        "14": {"class_type": "SaveAnimatedWEBP", "inputs": {
            "filename_prefix": "gentest_vid",
            "images": ["13", 0],
            "fps": 16.0,
            "lossless": True,
            "quality": 100,
            "method": "default",
        }},
    }


# ─── Prompt Definitions ────────────────────────────────────────────────────
# Each entry: (prompt_text, model_key)
# Models: "flux_dev", "flux_schnell", "sd35", "z_turbo"


CINEMATIC = {
    "come_together": [
        (
            "Cinematic portrait of an aging rock legend in his 60s, "
            "deep weathered wrinkles mapping decades of excess, piercing haunted blue eyes, "
            "long disheveled white hair falling past shoulders, gaunt wasted frame in a worn leather jacket, "
            "sitting alone in a grand but decaying mansion living room, dusty gold records on peeling wallpaper, "
            "faded concert posters curling at edges, cobwebs on crystal chandelier, "
            "single shaft of golden hour light cutting through broken venetian blinds, "
            "dust particles floating in the light beam, 85mm f/1.4 lens, Roger Deakins lighting"
            + CIN_SUFFIX,
            "flux_dev",
        ),
        (
            "Epic concert photography, aging rock star with flowing white hair performing solo on stage, "
            "single overhead spotlight cutting through dense theatrical smoke, "
            "sweat glistening on weathered face twisted in raw emotion, "
            "worn leather jacket open over bare chest, electric guitar mid-strum, "
            "audience silhouettes in foreground with beautiful bokeh, "
            "anamorphic lens flare streaking horizontally, arena concert lighting with amber and blue gels, "
            "wide cinematic composition, Emmanuel Lubezki natural light inspiration"
            + CIN_SUFFIX,
            "flux_dev",
        ),
        (
            "Young man in his early 20s with tousled brown hair and streetwear hoodie, "
            "climbing through a shattered window of a Victorian mansion at night, "
            "flashlight beam cutting through dusty air revealing decayed grandeur, "
            "moonlight filtering through storm clouds, dramatic chiaroscuro lighting, "
            "broken glass glinting on the floor, 35mm wide angle lens, "
            "thriller atmosphere, Denis Villeneuve color palette of teal and amber"
            + CIN_SUFFIX,
            "sd35",
        ),
        (
            "Battered vintage 1970s Volkswagen van on an endless American highway at golden hour, "
            "vast prairie grasslands stretching to the horizon, "
            "dramatic cumulus clouds lit vivid orange and magenta from below, "
            "long dust trail behind the van, painted desert mountains in far distance, "
            "road disappearing to vanishing point, Wim Wenders cinematography, "
            "65mm large format lens, warm nostalgic Kodak Portra color palette"
            + CIN_SUFFIX,
            "sd35",
        ),
        (
            "Distinguished elderly butler in his 70s, impeccable but threadbare black morning suit, "
            "silver hair perfectly combed with military precision, ramrod straight posture, "
            "standing in the doorway of a crumbling grand staircase, "
            "quiet dignity in every line of his weathered face, "
            "soft directional light from a tall window, English country house decay, "
            "medium shot, 50mm prime lens f/2, muted earth tones, Janusz Kaminski lighting"
            + CIN_SUFFIX,
            "flux_schnell",
        ),
    ],
    "dog": [
        (
            "Korean man in his mid-20s with forgettable plain features, wearing an ill-fitting cheap gray suit, "
            "sitting rigidly in a job interview across a bare metal desk, "
            "harsh overhead fluorescent tubes casting unflattering shadows under his eyes, "
            "corporate office with beige walls and motivational posters, "
            "nervous sweat on his upper lip, hands clasped too tightly, "
            "interviewer's silhouette in foreground, 35mm lens, "
            "Park Chan-wook meticulous framing, cold institutional color palette"
            + CIN_SUFFIX,
            "flux_dev",
        ),
        (
            "Korean man in his 40s with slicked-back balding hair, fake 1980s glamour, "
            "sitting in the driver seat of a black Porsche 911, lit only by dashboard instruments and passing city lights, "
            "Chinese pop music implied by the radio glow, "
            "one hand draped casually over the steering wheel, gold watch catching light, "
            "confident smirk revealing dangerous charisma, "
            "Chungking Express neon reflections on windshield, 40mm anamorphic, shallow focus"
            + CIN_SUFFIX,
            "flux_dev",
        ),
        (
            "Government intelligence office at night, rows of identical gray cubicles "
            "stretching into darkness, each with a glowing monitor showing Korean internet comments, "
            "single worker hunched over keyboard, overhead fluorescent creating pools of clinical white light, "
            "surveillance cameras visible in ceiling corners, "
            "cold blue-green color grade, David Fincher aesthetic, "
            "wide establishing shot, 21mm lens, institutional dread"
            + CIN_SUFFIX,
            "sd35",
        ),
        (
            "Night scene on the Han River embankment in Seoul, "
            "two male silhouettes facing each other under a lone sodium vapor streetlight, "
            "city skyline reflecting in dark water behind them, "
            "autumn leaves blowing across wet concrete, "
            "tension in the space between them, noir atmosphere, "
            "long shadows stretching toward camera, Gordon Willis darkness, "
            "50mm prime, deep shadows with minimal fill light"
            + CIN_SUFFIX,
            "sd35",
        ),
        (
            "Korean room salon interior, gaudy gold and crimson velvet booths, "
            "neon karaoke lights reflecting off champagne bottles, "
            "cigarette smoke layering the air in visible strata, "
            "middle-aged Korean businessmen laughing too loudly, "
            "hostess pouring soju in soft focus background, "
            "shallow depth of field centered on a crystal ashtray with a burning cigarette, "
            "35mm Leica lens, Wong Kar-wai saturated neon palette"
            + CIN_SUFFIX,
            "flux_schnell",
        ),
    ],
    "exodus": [
        (
            "Ancient Egyptian prince with striking deep blue eyes, tall and lean, "
            "standing before a massive sandstone palace at dawn, "
            "hieroglyphic-covered columns towering behind him, "
            "linen robes billowing in desert wind, golden pectoral necklace catching first light, "
            "sand particles suspended in amber morning air, "
            "epic scale with tiny human figures for reference, "
            "Ridley Scott Biblical epic framing, 65mm IMAX lens"
            + CIN_SUFFIX,
            "flux_dev",
        ),
        (
            "Interior of an alien spacecraft, organic stone-like walls with no visible seams, "
            "bioluminescent veins pulsing soft blue-green through living rock surfaces, "
            "furniture that appears grown rather than built, root-like structures forming chairs, "
            "no windows, light emanating from the walls themselves, "
            "a strange plant-like being with root tendrils embedded in hovering nutrient dishes, "
            "otherworldly yet serene atmosphere, HR Giger meets organic architecture, "
            "wide angle 24mm, Denis Villeneuve Arrival aesthetic"
            + CIN_SUFFIX,
            "flux_dev",
        ),
        (
            "Biblical epic scene of a vast sea parting, two towering walls of dark ocean water "
            "held back by invisible force, revealing seabed with stranded fish and coral, "
            "thousands of people walking through the gap as a tiny procession, "
            "storm clouds above with shafts of divine light breaking through, "
            "spray and mist at the edges of the water walls, "
            "epic IMAX wide shot, Terrence Malick sky, overwhelming scale"
            + CIN_SUFFIX,
            "sd35",
        ),
        (
            "Desolate mountain summit at night, a lone robed figure standing on bare rock, "
            "two bright planets aligned in the sky above forming a conjunction, "
            "stars blazing in unpolluted ancient sky, "
            "wind whipping the figure's robes, a faint ethereal glow emanating from a pendant on his chest, "
            "vast empty desert stretching below in moonlight, "
            "spiritual isolation, Christopher Nolan Interstellar scale"
            + CIN_SUFFIX,
            "sd35",
        ),
        (
            "Egyptian queen pharaoh in full ceremonial regalia, "
            "double crown of Upper and Lower Egypt, gold and lapis lazuli collar, "
            "kohl-lined eyes radiating maternal strength and royal authority, "
            "standing in a torch-lit temple chamber, hieroglyphic walls in warm orange light, "
            "medium close-up portrait, "
            "Vittorio Storaro golden hour warmth, 85mm f/1.8"
            + CIN_SUFFIX,
            "flux_schnell",
        ),
    ],
    "hague": [
        (
            "Wealthy Korean professor in his late 30s in a luxury penthouse, "
            "wearing a perfectly tailored navy Brioni suit, Patek Philippe watch catching window light, "
            "standing at floor-to-ceiling windows overlooking the Han River and Seoul skyline at dusk, "
            "warm amber interior lighting contrasting with cool blue city lights, "
            "crystal whiskey glass in hand, expression of supreme boredom, "
            "85mm portrait lens, Tom Ford advertising aesthetic, Robert Richardson lighting"
            + CIN_SUFFIX,
            "flux_dev",
        ),
        (
            "1907 European diplomatic building exterior in rain, "
            "grand Neoclassical architecture with gas lamps glowing in the drizzle, "
            "cobblestone street reflecting warm lamplight in puddles, "
            "a solitary Asian man in early 20th century Western formal suit walking with an umbrella, "
            "melancholy atmosphere of exile and futile diplomacy, "
            "Kazuo Ishiguro emotional restraint, Gordon Willis muted palette, "
            "wide shot 35mm, period-accurate Hague architecture"
            + CIN_SUFFIX,
            "flux_dev",
        ),
        (
            "Chaotic chase through a Korean traditional antique market, "
            "narrow alley packed with stacked ceramics and hanging scrolls, "
            "a well-dressed man in designer clothes sprinting through the clutter, "
            "motion blur on his Gucci shoes, stallkeepers diving out of the way, "
            "porcelain shattering mid-air in slow motion, "
            "Guy Ritchie kinetic energy, 24mm wide angle, dutch angle, "
            "warm tungsten market lighting"
            + CIN_SUFFIX,
            "sd35",
        ),
        (
            "Vast snowy Russian highway stretching to infinity under overcast sky, "
            "a lone sedan driving through fresh snow, birch forests on both sides, "
            "tire tracks the only marks on pristine white surface, "
            "muted gray-blue color palette, oppressive silence visible in the stillness, "
            "Andrei Tarkovsky landscape composition, "
            "ultra-wide 16mm lens, cold desaturated grade"
            + CIN_SUFFIX,
            "sd35",
        ),
        (
            "Young Korean woman in her late 20s with horn-rimmed glasses and leather jacket, "
            "examining a painting in a dimly lit museum restoration room, "
            "conservation lamp casting warm focused light on the canvas, "
            "her face lit by the painting's reflected glow showing intense concentration, "
            "brushes and solvents on the worktable, quiet intellectual passion, "
            "50mm f/1.4, Peter Suschitzky intimate lighting"
            + CIN_SUFFIX,
            "flux_schnell",
        ),
    ],
    "red_architect": [
        (
            "Japanese man in his late 70s with white hair tied neatly, "
            "performing a traditional tea ceremony with terrifying precision, "
            "wearing dark indigo hakama in a 400-year-old wooden tea room, "
            "each movement deliberate and loaded with meaning, "
            "steam rising from the chawan in late afternoon light, "
            "shoji screens filtering soft diffused light, tatami textures, "
            "medium shot, Ozu low angle, Akira Kurosawa composition"
            + CIN_SUFFIX,
            "flux_dev",
        ),
        (
            "Underground military war room in Beijing, "
            "massive wall displays showing maps of the Pacific with red threat indicators, "
            "Chinese military officers in uniform studying screens, "
            "single general standing apart with arms clasped behind his back, "
            "overhead strip lighting creating harsh shadows on emotionless faces, "
            "screens reflecting in polished floor, "
            "Stanley Kubrick Dr. Strangelove symmetry, 24mm wide angle"
            + CIN_SUFFIX,
            "flux_dev",
        ),
        (
            "Pacific Ocean naval fleet at sunset, "
            "massive aircraft carrier in the foreground with fighter jets on deck, "
            "escort destroyers and cruisers in formation stretching to the horizon, "
            "dramatic sky with towering cumulonimbus clouds lit blood-red, "
            "wake trails carving white lines in dark ocean, "
            "military power projection, Michael Bay dramatic scale, "
            "aerial wide shot, extreme cinematic scope"
            + CIN_SUFFIX,
            "sd35",
        ),
        (
            "Exclusive Ginza geisha house private room at night, "
            "two powerful men in suits across a lacquered table, "
            "one Japanese elderly with white hair, one tall American with gray hair, "
            "geisha silhouette visible through translucent screen, "
            "sake cups and a document folder between them, "
            "warm amber lantern light, shadows holding secrets, "
            "spy thriller tension, John le Carré atmosphere, 40mm anamorphic"
            + CIN_SUFFIX,
            "sd35",
        ),
        (
            "Seoul city skyline engulfed in flames and smoke at night, "
            "iconic buildings silhouetted against orange inferno, "
            "Han River reflecting the destruction in its dark surface, "
            "military helicopters as small dots against the smoke, "
            "ash falling like snow, apocalyptic devastation, "
            "news footage aesthetic crossed with cinematic scale, "
            "wide establishing shot, Janusz Kaminski war photography"
            + CIN_SUFFIX,
            "flux_schnell",
        ),
    ],
}

WEBTOON = {
    "come_together": [
        (
            "Korean manhwa webtoon style, dramatic close-up of weathered old hands "
            "playing an electric guitar, detailed gnarled fingers pressing steel strings, "
            "calluses and veins visible, dynamic speed lines radiating from the fretboard, "
            "warm amber stage lighting with dramatic rim light, "
            "heavy shadows, emotional intensity, clean bold linework"
            + WEB_SUFFIX,
            "z_turbo",
        ),
        (
            "Korean manhwa webtoon style, young man in his early 20s with messy brown hair "
            "wearing an oversized streetwear hoodie, livestreaming on his phone, "
            "modern bedroom with RGB LED strips and music equipment in background, "
            "screen glow illuminating his excited expression, "
            "speech bubble space above, energetic composition, clean cel shading"
            + WEB_SUFFIX,
            "z_turbo",
        ),
        (
            "Korean manhwa webtoon style, two men arguing inside a cramped vintage VW van, "
            "older man with long white hair pointing angrily, younger man in hoodie crossed arms defiant, "
            "desert highway visible through windshield, dramatic diagonal composition, "
            "tension lines between them, expressive exaggerated facial features, "
            "warm sunset colors flooding through windows"
            + WEB_SUFFIX,
            "flux_dev",
        ),
        (
            "Korean manhwa webtoon style, concert audience seen from behind, "
            "hundreds of mesmerized faces lit by warm amber stage light, "
            "hands reaching upward in ecstasy, tears on some faces, "
            "beautiful bokeh stage lights as circles in background, "
            "emotional catharsis moment, vertical scroll composition, rich warm palette"
            + WEB_SUFFIX,
            "flux_dev",
        ),
        (
            "Korean manhwa webtoon style, elderly butler with silver combed hair "
            "driving a van on a desert highway, stoic dignified expression, "
            "hands steady on the steering wheel, worn but immaculate black suit, "
            "warm sunset tones through windshield, dashboard reflected in his glasses, "
            "medium close-up, clean digital coloring"
            + WEB_SUFFIX,
            "flux_schnell",
        ),
    ],
    "dog": [
        (
            "Korean manhwa webtoon style, young Korean man in a tiny goshiwon room, "
            "sitting on a narrow bed surrounded by rejection letters and empty ramen cups, "
            "fluorescent light casting harsh shadows, phone screen the only warm glow, "
            "cramped space barely wider than his shoulders, desperation in hunched posture, "
            "dark moody palette with high contrast, psychological weight"
            + WEB_SUFFIX,
            "z_turbo",
        ),
        (
            "Korean manhwa webtoon style, stern middle-aged Korean man in dark government suit "
            "placing a handgun and three bullets on a desk with mechanical precision, "
            "his face completely emotionless, timer visible on his wrist, "
            "cold institutional lighting, the gun in sharp focus, "
            "thriller panel composition, heavy black shadows, minimal color"
            + WEB_SUFFIX,
            "z_turbo",
        ),
        (
            "Korean manhwa webtoon style, interior of a black Porsche from passenger perspective, "
            "driver is a charismatic Korean man in his 40s with slicked hair and gold watch, "
            "one hand casual on steering wheel, knowing smirk, "
            "city neon lights streaking past windows, dashboard glow on his face, "
            "power dynamic composition with driver dominating the frame"
            + WEB_SUFFIX,
            "flux_dev",
        ),
        (
            "Korean manhwa webtoon style, wall of computer monitors showing Korean internet comments, "
            "a young man's face reflected in the screens, eyes bloodshot from hours of scrolling, "
            "cubicle partition walls forming a cage, "
            "blue monitor glow as dominant light source, digital surveillance aesthetic, "
            "cyberpunk influenced panel, clean linework"
            + WEB_SUFFIX,
            "flux_dev",
        ),
        (
            "Korean manhwa webtoon style, love hotel parking lot at night, "
            "neon sign casting pink and purple light on wet asphalt, "
            "two dark figures near a car trunk, noir atmosphere, "
            "rain drizzle visible in neon glow, long shadows, "
            "film noir manhwa crossover, heavy blacks, minimal detail in shadows"
            + WEB_SUFFIX,
            "flux_schnell",
        ),
    ],
    "exodus": [
        (
            "Korean manhwa webtoon style, young man with striking blue eyes "
            "discovering a glowing pendant in a hidden stone chamber, "
            "torch light reflecting off hieroglyphic walls, the pendant's glow illuminating his face, "
            "sense of forbidden discovery, ancient treasure chamber, "
            "dramatic uplight, rich gold and blue palette, detailed linework"
            + WEB_SUFFIX,
            "z_turbo",
        ),
        (
            "Korean manhwa webtoon style, alien being composed of plant-like tendrils and roots, "
            "hovering above nutrient dishes, no visible face, "
            "bioluminescent glow emanating from its core, alien spacecraft interior, "
            "organic textures and flowing lines, science fiction manhwa aesthetic, "
            "cool blue-green palette, otherworldly beauty"
            + WEB_SUFFIX,
            "z_turbo",
        ),
        (
            "Korean manhwa webtoon style, vast desert landscape with thousands of tiny figures "
            "walking in a long procession across endless sand dunes, "
            "harsh sun bleaching the scene, heat shimmer distorting the horizon, "
            "feeling of monotonous endless wandering, "
            "panoramic wide composition, muted sandy palette, epic biblical scale"
            + WEB_SUFFIX,
            "flux_dev",
        ),
        (
            "Korean manhwa webtoon style, close-up of a man with radiation scars across his face, "
            "deep blue eyes still piercing through the disfigurement, "
            "speaking through another man who stands in front, acting as his voice, "
            "dramatic split composition showing both figures, "
            "heavy emotional weight, dark palette with blue accent on his eyes"
            + WEB_SUFFIX,
            "flux_dev",
        ),
        (
            "Korean manhwa webtoon style, massive organic spacecraft ascending into a star-filled sky, "
            "no metallic surfaces, the ship looks grown from stone and coral, "
            "desert people watching from below in awe and fear, "
            "speed lines and light trails, dynamic vertical composition, "
            "epic climactic moment, rich night sky colors"
            + WEB_SUFFIX,
            "flux_schnell",
        ),
    ],
    "hague": [
        (
            "Korean manhwa webtoon style, cherry red 1967 Ford Mustang convertible "
            "roaring down a modern Seoul street, "
            "the driver is a stylish Korean man in sunglasses and designer clothes, "
            "motion blur on background, speed lines, exhaust fumes, "
            "vibrant daytime colors, dynamic action composition"
            + WEB_SUFFIX,
            "z_turbo",
        ),
        (
            "Korean manhwa webtoon style, dignified Korean diplomat in 1907 Western formal suit "
            "standing before a grand European building in the rain, "
            "holding a leather briefcase containing a nation's last hope, "
            "gas lamps reflected in cobblestone puddles, "
            "historical drama composition, sepia-influenced muted palette with color accents"
            + WEB_SUFFIX,
            "z_turbo",
        ),
        (
            "Korean manhwa webtoon style, wealthy professor and female student "
            "arguing face-to-face over an old painting, "
            "he is gesturing dramatically in designer suit, she stands firm in leather jacket and glasses, "
            "the painting between them as contested object, "
            "comedy duo dynamic, expressive facial features, museum lighting"
            + WEB_SUFFIX,
            "flux_dev",
        ),
        (
            "Korean manhwa webtoon style, chaotic Korean antique market, "
            "vendors diving behind stalls, ceramics flying through the air, "
            "a well-dressed man leaping over a stack of traditional folding screens, "
            "dynamic action lines, multiple small panels within the composition, "
            "kinetic energy, comedy action genre, bright vibrant colors"
            + WEB_SUFFIX,
            "flux_dev",
        ),
        (
            "Korean manhwa webtoon style, interior of De Jong Hotel room in 1907, "
            "a dying Korean activist lying on an ornate bed, "
            "a small Van Gogh painting visible on the bedside table, "
            "rain streaking the window, gas lamp creating warm intimate light, "
            "emotional weight, historical drama, warm but somber palette"
            + WEB_SUFFIX,
            "flux_schnell",
        ),
    ],
    "red_architect": [
        (
            "Korean manhwa webtoon style, traditional Japanese wooden estate interior, "
            "400-year-old dark timber beams, scrolls and geopolitical maps on walls, "
            "an elderly man in hakama seated in the center examining documents, "
            "autumn light through shoji screens casting grid shadows, "
            "sense of centuries of accumulated power, warm wood tones"
            + WEB_SUFFIX,
            "z_turbo",
        ),
        (
            "Korean manhwa webtoon style, Chinese military general in full dress uniform, "
            "absolutely emotionless face like carved stone, "
            "standing before a wall of tactical displays, hands clasped behind back, "
            "small fleck of blood on his shirt cuff, "
            "cold institutional lighting, military thriller aesthetic, "
            "steel blue and dark green palette"
            + WEB_SUFFIX,
            "z_turbo",
        ),
        (
            "Korean manhwa webtoon style, White House situation room, "
            "American officials around an oval conference table, "
            "the President listening to an advisor lean in close, "
            "multiple screens showing satellite imagery, "
            "tension visible in body language, political thriller composition, "
            "cool desaturated palette with screen glow accents"
            + WEB_SUFFIX,
            "flux_dev",
        ),
        (
            "Korean manhwa webtoon style, North Korean leader in a dark suit "
            "standing at a window overlooking a city of new apartment buildings, "
            "pride in his expression, binoculars in hand, "
            "the view is bright and modern, but ominous clouds gathering outside, "
            "dramatic irony composition, contrast between hope and doom"
            + WEB_SUFFIX,
            "flux_dev",
        ),
        (
            "Korean manhwa webtoon style, extreme close-up of a bamboo shishiodoshi water dropper, "
            "water droplet frozen in mid-fall, bamboo about to strike stone, "
            "zen garden in soft focus background, metaphor for inevitable structural force, "
            "minimalist composition, single moment of impact, "
            "Japanese aesthetic wabi-sabi, muted green and brown palette"
            + WEB_SUFFIX,
            "flux_schnell",
        ),
    ],
}

VIDEO_SPECS = {
    "come_together": [
        ("camera slowly pulls back revealing the full decaying room, "
         "dust particles drift through golden light beam, curtain sways gently in a draft, "
         "the man breathes slowly, melancholy stillness",
         "come_together-c01-flux_dev.png"),
        ("spotlight flickers and shifts, smoke swirls around the performer, "
         "hair sways with head movement, guitar strings vibrate, "
         "crowd energy pulses in foreground shadows",
         "come_together-c02-flux_dev.png"),
    ],
    "dog": [
        ("fluorescent light flickers subtly overhead, "
         "the man swallows nervously, fingers tighten on lap, "
         "papers rustle slightly on the desk, tense stillness",
         "dog-c01-flux_dev.png"),
        ("car moves slowly through city at night, "
         "neon lights slide across the hood and windshield, "
         "the driver's face partially lit by changing dashboard glow, "
         "smoke from a cigarette drifts upward",
         "dog-c02-flux_dev.png"),
    ],
    "exodus": [
        ("desert wind blows sand across the frame, "
         "the man's robes billow and flutter, "
         "torch flames dance on the palace columns, "
         "clouds drift across the dawn sky, epic ancient atmosphere",
         "exodus-c01-flux_dev.png"),
        ("bioluminescent veins in the walls pulse slowly with light, "
         "the alien plant being's tendrils shift and undulate gently, "
         "organic surfaces seem to breathe, ethereal alien atmosphere",
         "exodus-c02-flux_dev.png"),
    ],
    "hague": [
        ("city lights twinkle across the Han River skyline, "
         "the man takes a slow sip of whiskey, "
         "golden hour light shifts subtly across the room, "
         "reflections dance on the glass",
         "hague-c01-flux_dev.png"),
        ("gentle rain continues falling, puddles ripple, "
         "gas lamps flicker in the drizzle, "
         "the man walks slowly under his umbrella, "
         "cobblestone reflections shimmer with each step",
         "hague-c02-flux_dev.png"),
    ],
    "red_architect": [
        ("steam rises elegantly from the tea cup, "
         "the old man's hand moves with precise deliberate ceremony, "
         "light shifts subtly through shoji screens, "
         "absolute controlled stillness, only the steam moves",
         "red_architect-c01-flux_dev.png"),
        ("screens flicker with updating data and maps, "
         "the general's eyes track slowly across the displays, "
         "overhead lights hum with fluorescent pulse, "
         "tension building in the stillness of the room",
         "red_architect-c02-flux_dev.png"),
    ],
}

# ─── Build Job List ─────────────────────────────────────────────────────────

SIZES = {
    "cinematic": (1280, 720),
    "webtoon": (768, 1024),
}

BUILDERS = {
    "flux_dev": lambda p, n, w, h, s: workflow_flux_dev(p, w, h, s),
    "flux_schnell": lambda p, n, w, h, s: workflow_flux_schnell(p, w, h, s),
    "sd35": lambda p, n, w, h, s: workflow_sd35(p, n, w, h, s),
    "z_turbo": lambda p, n, w, h, s: workflow_z_turbo(p, w, h, s),
}


def build_image_jobs():
    """Build the list of image generation jobs."""
    jobs = []
    for project, prompts in CINEMATIC.items():
        w, h = SIZES["cinematic"]
        for i, (prompt, model) in enumerate(prompts, 1):
            neg = CIN_NEG if model == "sd35" else ""
            jobs.append({
                "filename": f"{project}-c{i:02d}-{model}",
                "project": project,
                "type": "cinematic",
                "model": model,
                "prompt": prompt,
                "neg": neg,
                "width": w,
                "height": h,
                "seed": random.randint(0, 2**31),
            })
    for project, prompts in WEBTOON.items():
        w, h = SIZES["webtoon"]
        for i, (prompt, model) in enumerate(prompts, 1):
            neg = WEB_NEG if model == "sd35" else ""
            jobs.append({
                "filename": f"{project}-w{i:02d}-{model}",
                "project": project,
                "type": "webtoon",
                "model": model,
                "prompt": prompt,
                "neg": neg,
                "width": w,
                "height": h,
                "seed": random.randint(0, 2**31),
            })
    return jobs


def build_video_jobs():
    """Build the list of video generation jobs."""
    jobs = []
    for project, specs in VIDEO_SPECS.items():
        for i, (motion_prompt, source_image) in enumerate(specs, 1):
            jobs.append({
                "filename": f"{project}-v{i:02d}-wan_i2v",
                "project": project,
                "type": "video",
                "model": "wan_i2v",
                "motion_prompt": motion_prompt,
                "source_image": source_image,
                "seed": random.randint(0, 2**31),
            })
    return jobs


# ─── Execution ──────────────────────────────────────────────────────────────


def generate_images(servers, dry_run=False):
    """Generate all images, routing models to correct servers."""
    jobs = build_image_jobs()
    print(f"\n{'='*70}")
    print(f"  IMAGE GENERATION: {len(jobs)} images")
    print(f"  Routing: FLUX → neumann, SD3.5/z_turbo → wright")
    print(f"  Output: {TEST_DIR}/")
    print(f"{'='*70}\n")

    if dry_run:
        for j in jobs:
            target = MODEL_SERVER.get(j["model"], servers[0]).split("//")[1]
            print(f"  [{j['model']:14s}] {j['filename']}  ({j['width']}x{j['height']})  → {target}")
            print(f"    {j['prompt'][:100]}...")
        return

    # Submit all jobs routed to correct server
    submitted = []
    for i, job in enumerate(jobs):
        server = MODEL_SERVER.get(job["model"], servers[0])
        if server not in servers:
            print(f"  [{i+1:2d}/{len(jobs)}] SKIP     {job['filename']:40s} — server offline")
            continue
        builder = BUILDERS[job["model"]]
        workflow = builder(job["prompt"], job["neg"], job["width"], job["height"], job["seed"])
        try:
            prompt_id = submit_prompt(server, workflow)
            submitted.append((job, server, prompt_id))
            print(f"  [{i+1:2d}/{len(jobs)}] Submitted {job['filename']:40s} → {server.split('//')[1]:20s}  seed={job['seed']}")
        except Exception as e:
            print(f"  [{i+1:2d}/{len(jobs)}] FAILED   {job['filename']:40s} → {e}")

    # Poll and download
    print(f"\n  Waiting for {len(submitted)} jobs to complete...\n")
    completed = 0
    failed = 0
    for job, server, prompt_id in submitted:
        try:
            result = poll_completion(server, prompt_id, timeout=IMG_TIMEOUT)
            # Find output files in any output node
            for node_id, output in result.get("outputs", {}).items():
                for key in ("images", "videos", "gifs"):
                    for item in output.get(key, []):
                        ext = os.path.splitext(item["filename"])[1] or ".png"
                        save_path = os.path.join(TEST_DIR, job["filename"] + ext)
                        download_file(server, item["filename"], item.get("subfolder", ""), item["type"], save_path)
                        completed += 1
                        size_kb = os.path.getsize(save_path) / 1024
                        print(f"  [{completed:2d}/{len(submitted)}] Downloaded {job['filename'] + ext:45s} ({size_kb:.0f} KB)")
        except Exception as e:
            failed += 1
            print(f"  [FAIL] {job['filename']:45s} → {e}")

    print(f"\n  Images done: {completed} completed, {failed} failed\n")


def generate_videos(servers, dry_run=False):
    """Generate all videos using images as source frames."""
    jobs = build_video_jobs()
    print(f"\n{'='*70}")
    print(f"  VIDEO GENERATION: {len(jobs)} videos across {len(servers)} servers")
    print(f"{'='*70}\n")

    if dry_run:
        for j in jobs:
            print(f"  [{j['model']:14s}] {j['filename']}  ← {j['source_image']}")
            print(f"    {j['motion_prompt'][:100]}...")
        return

    # Check that source images exist
    for job in jobs:
        src = os.path.join(TEST_DIR, job["source_image"])
        if not os.path.exists(src):
            print(f"  ERROR: Source image not found: {src}")
            print(f"  Run image generation first: python scripts/generate_test.py images")
            return

    # Submit all video jobs (Wan I2V only on wright)
    submitted = []
    for i, job in enumerate(jobs):
        server = MODEL_SERVER.get(job["model"], WRIGHT)
        if server not in servers:
            print(f"  [{i+1:2d}/{len(jobs)}] SKIP     {job['filename']:40s} — server offline")
            continue
        src_path = os.path.join(TEST_DIR, job["source_image"])

        # Upload source image to server
        try:
            uploaded_name = upload_image(server, src_path)
            print(f"  Uploaded {job['source_image']} → {server.split('//')[1]} as {uploaded_name}")
        except Exception as e:
            print(f"  FAILED uploading {job['source_image']}: {e}")
            continue

        # Build and submit workflow
        workflow = workflow_wan_i2v(job["motion_prompt"], uploaded_name, job["seed"])
        try:
            prompt_id = submit_prompt(server, workflow)
            submitted.append((job, server, prompt_id))
            print(f"  [{i+1:2d}/{len(jobs)}] Submitted {job['filename']:40s} → {server.split('//')[1]}")
        except Exception as e:
            print(f"  [{i+1:2d}/{len(jobs)}] FAILED   {job['filename']:40s} → {e}")

    # Poll and download
    print(f"\n  Waiting for {len(submitted)} videos (this may take a while)...\n")
    completed = 0
    failed = 0
    for job, server, prompt_id in submitted:
        try:
            result = poll_completion(server, prompt_id, timeout=VID_TIMEOUT)
            for node_id, output in result.get("outputs", {}).items():
                for key in ("images", "videos", "gifs"):
                    for item in output.get(key, []):
                        ext = os.path.splitext(item["filename"])[1] or ".webp"
                        save_path = os.path.join(TEST_DIR, job["filename"] + ext)
                        download_file(server, item["filename"], item.get("subfolder", ""), item["type"], save_path)
                        completed += 1
                        size_kb = os.path.getsize(save_path) / 1024
                        print(f"  [{completed:2d}/{len(submitted)}] Downloaded {job['filename'] + ext:45s} ({size_kb:.0f} KB)")
        except Exception as e:
            failed += 1
            print(f"  [FAIL] {job['filename']:45s} → {e}")

    print(f"\n  Videos done: {completed} completed, {failed} failed\n")


def main():
    os.makedirs(TEST_DIR, exist_ok=True)
    random.seed(42)  # Reproducible seeds across runs

    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    dry_run = "--dry" in sys.argv

    if mode == "--dry":
        mode = "all"
        dry_run = True

    # Check servers
    servers = get_available_servers()
    if not servers and not dry_run:
        print("ERROR: No ComfyUI servers available!")
        sys.exit(1)
    print(f"Servers: {len(servers)} online — {', '.join(s.split('//')[1] for s in servers)}")

    if mode in ("all", "images"):
        generate_images(servers, dry_run)
    if mode in ("all", "videos"):
        generate_videos(servers, dry_run)

    if not dry_run:
        total = len([f for f in os.listdir(TEST_DIR) if not f.startswith(".")])
        print(f"\n{'='*70}")
        print(f"  ALL DONE — {total} files in {TEST_DIR}/")
        print(f"{'='*70}")


if __name__ == "__main__":
    main()
