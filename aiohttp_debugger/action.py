from aiohttp import hdrs
from aiohttp_jinja2 import template
from aiohttp.web import Response, WebSocketResponse
from asyncio import ensure_future, sleep
from .helper import WsResponseHelper
from . import api


@template("index.html")
async def dashboard(request):
    return {}


async def websocket(request):
    response = await WsResponseHelper.instance(request)
    proxy = api.WsMsgDispatcherProxy(response, api.WsMsgDispatcher(response))

    async for msg in response:
        ensure_future(proxy.recive(msg))

    return response


routes = (
    (hdrs.METH_GET, "/_debugger/ws/api", websocket),
    (hdrs.METH_GET, "/_debugger/dashboard", dashboard)
)
