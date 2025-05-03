
from django.apps import AppConfig
import threading


class AcquisitionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'acquisition'    

    def ready(self):
        from .agent_runner import start_agents_in_background
        threading.Thread(target=start_agents_in_background, daemon=True).start()
