from index.source import Source

class Mangadex(Source, color=0x0aaaa):

    URL = "https://mangadex.org/"

    def route(self, route):
        return self.URL + "/api/" + route

    async def get_manga(self, id):
        route = self.route("manga/" + id)
        data = await self.request_api(route)

