from arq import create_pool
from api.config.ArqSettings import arqsettings


class Asyncrq:
    async def create_pool(self) -> None:
        self.pool = await create_pool(arqsettings)


asyncrq = Asyncrq()
