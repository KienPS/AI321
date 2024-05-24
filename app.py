from pathlib import Path

from litestar import Litestar
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
from litestar.static_files import create_static_files_router

from routers import ToeicParserController


app = Litestar(
    route_handlers=[
        create_static_files_router(
            path="/static",
            directories=[Path("static")]
        ),
        ToeicParserController
    ],  
    template_config=TemplateConfig(
        directory=Path("templates"),
        engine=JinjaTemplateEngine
    )
)