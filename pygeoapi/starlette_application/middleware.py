from starlette.datastructures import URL
from starlette.responses import (
    RedirectResponse,
    Response,
)
from starlette.types import (
    ASGIApp,
    Receive,
    Scope,
    Send,
)


class ApiRulesMiddleware:
    """ Custom middleware to properly deal with trailing slashes.
    See https://github.com/encode/starlette/issues/869.
    """

    def __init__(
            self,
            app: ASGIApp,
            url_prefix: str,
            use_strict_slashes: bool,
    ) -> None:
        self.app = app
        self.prefix = url_prefix
        self.use_strict_slashes = use_strict_slashes

    async def __call__(self, scope: Scope,
                       receive: Receive, send: Send) -> None:
        if scope['type'] == "http" and self.use_strict_slashes:
            path = scope['path']
            if path == self.prefix:
                # If the root (landing page) is requested without a trailing
                # slash, redirect to landing page with trailing slash.
                # Starlette will otherwise throw a 404, as it does not like
                # empty Route paths.
                url = URL(scope=scope).replace(path=f"{path}/")
                response = RedirectResponse(url)
                await response(scope, receive, send)
                return
            elif path != f"{self.prefix}/" and path.endswith('/'):
                # Resource paths should NOT have trailing slashes
                response = Response(status_code=404)
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
