import os
import fastapi_offline_swagger_ui
from fastapi import FastAPI, applications
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse


class AppConf:
    """
    A configuration class for setting up a FastAPI application
    with CORS and Swagger UI customization.

    Attributes:
        title (str): The title of the API.
        version (str): The version of the API.
        openapi_prefix (str): Prefix for OpenAPI documentation.
        assets_url (str): URL for static assets (Swagger UI files).
        openapi_url (str): URL for OpenAPI schema.
        docs_url (str): URL for the documentation UI.
        swagger_css_url (str): URL for a custom Swagger CSS file.
        swagger_js_url (str): URL for a custom Swagger JS file.
        swagger_favicon_url (str): URL for a custom Swagger favicon.
        origins (list): List of allowed origins for CORS.
        app (FastAPI): The FastAPI application instance.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initializes the configuration with given parameters."""

        self.title = kwargs.get("title")
        self.version = kwargs.get("version")
        self.openapi_prefix = kwargs.get("openapi_prefix")
        self.assets_url = kwargs.get("assets_url")
        self.openapi_url = kwargs.get("openapi_url")
        self.docs_url = kwargs.get("docs_url")
        self.swagger_css_url = kwargs.get("swagger_css_url")
        self.swagger_js_url = kwargs.get("swagger_js_url")
        self.swagger_favicon_url = kwargs.get("swagger_favicon_url")
        self.origins = kwargs.get("origins")
        self.app = None

    def setup(self) -> FastAPI:
        """
        Sets up and returns a FastAPI application with CORS and Swagger UI configurations.

        Returns:
            FastAPI: The configured FastAPI application instance.
        """

        self.app = FastAPI(
            title=self.title,
            version=self.version,
            openapi_url=self.openapi_url,
            docs_url=self.docs_url,
        )
        self.configure_cors()
        self.configure_swagger_ui()
        return self

    def configure_cors(self) -> None:
        """
        Configures Cross-Origin Resource Sharing (CORS) for the FastAPI app.
        """

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.origins,  # Allow specified origins
            allow_credentials=True,
            allow_methods=["*"],  # Allow all HTTP methods
            allow_headers=["*"],  # Allow all headers
        )

    def configure_swagger_ui(self) -> None:
        """
        Configures Swagger UI with custom assets if all required URLs are provided.
        """

        if all(
            [
                self.assets_url,
                self.swagger_css_url,
                self.swagger_js_url,
                self.swagger_favicon_url,
            ]
        ):
            asset_path = fastapi_offline_swagger_ui.__path__[0]
            css_file_path = os.path.join(asset_path, "swagger-ui.css")
            js_file_path = os.path.join(asset_path, "swagger-ui-bundle.js")

            # Check if the necessary Swagger UI files exist before mounting
            if os.path.exists(css_file_path) and os.path.exists(js_file_path):
                self.app.mount(
                    self.assets_url,
                    StaticFiles(directory=asset_path),
                    name="assets",
                )
                # Monkey-patch FastAPI's Swagger UI function to use custom assets
                applications.get_swagger_ui_html = self._swagger_monkey_patch

    def _swagger_monkey_patch(self, *args, **kwargs) -> HTMLResponse:
        """
        Customizes the Swagger UI by injecting custom CSS, JS, and favicon.

        Returns:
            HTMLResponse: The customized Swagger UI HTML response.
        """

        return get_swagger_ui_html(
            *args,
            **kwargs,
            swagger_favicon_url=self.swagger_favicon_url,
            swagger_css_url=self.swagger_css_url,
            swagger_js_url=self.swagger_js_url,
        )
