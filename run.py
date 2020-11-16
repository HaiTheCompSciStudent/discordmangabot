from bot import Index
import time
b = Index(command_prefix="O")

@b.event
async def on_ready():
    print("Yeah")
    time.sleep(3)
    for source in b.sources:
        print("SOURCE:", source)

    manga = await b.get_manga("https://mangadex.org/title/39")
    print(manga.__dict__)
b.run("NjcwNDIzMzc2MTQwOTU5NzY3.XiuKbA.EL9FfAug-NdTx3M6LtAa6c1nOEA")