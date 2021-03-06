from datetime import datetime

from django.db import models
from safedelete.models import SafeDeleteModel


class BaseModel(SafeDeleteModel):
    """BaseModel for created and updated fields."""

    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        abstract = True

    @classmethod
    def has_unique_fields(cls):
        """BaseModel has ID as a unique field"""
        return True
