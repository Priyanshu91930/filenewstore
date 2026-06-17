import asyncio
import aiohttp
import io
import base64

async def main():
    # 1x1 transparent GIF bytes
    gif_bytes = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
    
    async with aiohttp.ClientSession() as session:
        try:
            form = aiohttp.FormData()
            form.add_field("source", io.BytesIO(gif_bytes), filename="test.gif")
            form.add_field("action", "upload")
            # We don't supply key to see if guest upload works
            async with session.post("https://freeimage.host/api/1/upload", data=form) as resp:
                res = await resp.json()
                print("freeimage.host response:", res)
        except Exception as e:
            print("freeimage.host failed:", e)

asyncio.run(main())
