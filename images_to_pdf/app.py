import gradio as gr
from PIL import Image
import os

def get_images_from_folder(folder_path, image_type=None):
    supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    image_paths = []

    for f in os.listdir(folder_path):
        full_path = os.path.join(folder_path, f)
        if not os.path.isfile(full_path):
            continue

        fname = f.lower()
        if image_type:
            if fname.endswith(f".{image_type.lower()}"):
                image_paths.append(full_path)
        else:
            if fname.endswith(supported_extensions):
                image_paths.append(full_path)

    return image_paths

def sort_images(image_paths, sort_option):
    if sort_option == "None":
        return image_paths
    reverse = "↓" in sort_option

    if "Name" in sort_option:
        return sorted(image_paths, reverse=reverse)
    elif "Date" in sort_option:
        return sorted(image_paths, key=lambda x: os.path.getmtime(x), reverse=reverse)
    elif "Size" in sort_option:
        return sorted(image_paths, key=lambda x: os.path.getsize(x), reverse=reverse)

    return image_paths

def images_to_pdf_from_folder(folder_path, sort_option, image_type):
    if not os.path.isdir(folder_path):
        return None, "❌ Provided path is not a valid directory."

    image_paths = get_images_from_folder(folder_path, image_type)
    image_paths = sort_images(image_paths, sort_option)

    if not image_paths:
        return None, "⚠️ No matching images found in the folder."

    target_width = 2048  # A4 width
    images = []
    for path in image_paths:
        img = Image.open(path).convert("RGB")
        scale = target_width / img.width
        new_height = int(img.height * scale)
        resized = img.resize((target_width, new_height))
        images.append(resized)

    output_path = os.path.join(folder_path, "output.pdf")
    images[0].save(output_path, save_all=True, append_images=images[1:])

    return output_path, f"✅ PDF created: {len(images)} images scaled to {target_width}px wide (height auto)"


with gr.Blocks(title="📁 Folder to PDF") as demo:
    gr.Markdown("## 🖼️ Convert Images in a Folder to a PDF File")
    gr.Markdown("Enter the path to a folder containing images (JPG, PNG, BMP) to create a multi-page PDF.")

    folder_path = gr.Textbox(label="📂 Folder Path", placeholder="/Users/yourname/Desktop/images/")
    image_type = gr.Dropdown(
        choices=["jpg", "jpeg", "png", "bmp", None],
        value=None,
        label="Image Type (optional filter)"
    )
    sort_option = gr.Dropdown(
        choices=[
            "None",
            "Name ↑", "Name ↓",
            "Date ↑", "Date ↓",
            "Size ↑", "Size ↓"
        ],
        value="Name ↑",
        label="Sort By"
    )

    convert_btn = gr.Button("📄 Convert to PDF")
    output_pdf = gr.File(label="📥 Download PDF")
    status = gr.Textbox(label="Status")

    convert_btn.click(
        images_to_pdf_from_folder,
        inputs=[folder_path, sort_option, image_type],
        outputs=[output_pdf, status]
    )

demo.launch(allowed_paths=["/"])