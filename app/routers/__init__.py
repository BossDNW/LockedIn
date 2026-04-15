from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.utilities.flash import get_flashed_messages
from jinja2 import Environment, FileSystemLoader
from app.config import get_settings


template_env = Environment(loader = FileSystemLoader("app/templates",), )
template_env.globals['get_flashed_messages'] = get_flashed_messages
templates = Jinja2Templates(env=template_env)
static_files = StaticFiles(directory="app/static")

router = APIRouter(tags=["Jinja Based Endpoints"], include_in_schema=get_settings().env.lower() in ["dev","development"])
api_router = APIRouter(tags=["API Endpoints"], prefix="/api")

# Import all route modules
from . import index
from . import login
from . import register
from . import admin_home
from . import user_home
from . import users
from . import logout
from . import profile
from . import programmes
from . import applications
from . import api_programmes
from . import candidates
from . import my_applications
from . import admin_candidates

router.include_router(profile.router)
router.include_router(programmes.router)
router.include_router(candidates.router)
router.include_router(my_applications.router)
router.include_router(admin_candidates.router)
api_router.include_router(candidates.router)
api_router.include_router(api_programmes.router)
api_router.include_router(applications.router)