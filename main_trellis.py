import os

os.environ["ATTN_BACKEND"] = (
    "xformers"  # Can be 'flash-attn' or 'xformers', default is 'flash-attn'
)
os.environ["SPCONV_ALGO"] = "native"  # Can be 'native' or 'auto', default is 'auto'.
# 'auto' is faster but will do benchmarking at the beginning.
# Recommended to set to 'native' if run only once.

import imageio
from PIL import Image
from trellis.pipelines import TrellisImageTo3DPipeline
from trellis.utils import postprocessing_utils, render_utils
from utils.uid_utils import Uid

# Launch Craftsman on images from SSTK
INPUT_DIR = "/home/rsabathier/tools/output_tom"
SAVE_DIR = "/home/rsabathier/tools/output_trellis_rs"

uids = [
    # "2014741_002",  # CAT
    "2073515_003",  # FIREMAN-MATRIX
    # "1989494_000",  # BLUE MONSTER ONE-EYE
    # "1700228_000",  # SPIDER
    # "1423230_002",  # WINDMILL
    # "1486308_000",  # US-FLAG
    # "1241840_068",  # ORANGE DIVER
    # "2041812_015",  # ZOMBIE RUNNING
    # "1996785_000",  # CHINESE DRAGON
    # "1892119_002",  # CARTOON ELEPHANT
    # "2027477_002",  # ANIME-CAT
    # "1977441_020",  # BREAK DANCE PINK BERET
    # "1993403_001",  # DRAGON
    # "2004032_001",  # MAN-WALKING
    # "2006501_005",  # DUCK KNIGHT
    # "2038826_003",  # RACOON
]
camids = ["U000", "U004", "U008", "U012"]
N_keyframes = 8


# Load a pipeline from a model folder or a Hugging Face model hub.
pipeline = TrellisImageTo3DPipeline.from_pretrained(
    "/packages/omnivision_rsabathier_4d/cache/cache_trellis/TRELLIS-image-large"
)
pipeline.cuda()


for uid in uids:
    for camid in camids:
        for i in range(N_keyframes):
            rgba_path = os.path.join(INPUT_DIR, f"uid_{uid}_kf_{i}_camid_{camid}.png")

            output_dir = os.path.join(Uid(uid).get_uid_dir(SAVE_DIR), camid)
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)

            glb_out_path = os.path.join(output_dir, f"{uid}_{camid}_{i:03d}.glb")

            if os.path.isfile(glb_out_path):
                print(f"Skipping {glb_out_path}")
                continue

            # Load an image
            image = Image.open(rgba_path)

            # Run the pipeline
            outputs = pipeline.run(image, seed=1)

            # Render the outputs
            # video = render_utils.render_video(outputs["gaussian"][0])["color"]
            # imageio.mimsave("sample_gs.mp4", video, fps=30)
            # video = render_utils.render_video(outputs["radiance_field"][0])["color"]
            # imageio.mimsave("sample_rf.mp4", video, fps=30)
            # video = render_utils.render_video(outputs["mesh"][0])["normal"]
            # imageio.mimsave("sample_mesh.mp4", video, fps=30)

            # GLB files can be extracted from the outputs
            glb = postprocessing_utils.to_glb(
                outputs["gaussian"][0],
                outputs["mesh"][0],
                # Optional parameters
                simplify=0.95,  # Ratio of triangles to remove in the simplification process
                texture_size=1024,  # Size of the texture used for the GLB
            )

            glb.export(glb_out_path)
