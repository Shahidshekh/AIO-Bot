from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
import os

async def set_thumb(app, message):
    thumb_location = "/usr/src/app/thumb/"
    thumb_path = f"{thumb_location}{str(message.from_user.id)}.jpg"
    msg = await message.reply("Processing...", quote=True)
    if message.reply_to_message is not None:
        if not os.path.exist(thumb_location):
            os.makedirs(thumb_location)
        thumb_name = await app.download_media(
            message=message.reply_to_message, file_name=thumb_location 
        )
        Image.open(thumb_name).convert("RGB").save(thumb_name)
        metadata = extractMetadata(createParser(thumb_name))
        height = 0
        if metadata.has("height"):
            height = metadata.get("height")
        
        img = Image.open(thumb_name)
        img.resize((320, height))
        img.save(thumb_path, "JPEG")
        os.remove(thumb_name)

        await msg.edit("✅ Custom thumbnail saved. ")
    else:
        await msg.edit("❌ Reply to a photo to save custom thumbnail")

async def rm_thumb(app, message):
    thumb_location = "/usr/src/app/thumbnails/"
    thumb_path = f"{thumb_location}{str(message.from_user.id).jpg}"
    msg = await message.reply_text("processing ...")
    if os.path.exists(thumb_path):
        os.remove(thumb_path)
        await msg.edit("✅ Custom thumbnail cleared successfully.")
    else:
        await msg.edit("❌ Nothing to clear.")
