from app.modules.common.repository import BaseExtRepository
from .models import Okeds


class OkedsRepo(BaseExtRepository):
    model = Okeds
