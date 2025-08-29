# apps/core/models.py
import uuid
from django.db import models

class BaseModel(models.Model):
    """
    Modelo base abstrato que fornece campos padrão para todos os outros modelos.
    
    Campos:
    - id: Chave primária sequencial (mais performática que UUID para consultas)
    - uuid: Identificador único para uso em APIs/URLs públicas
    - is_active: Para "soft delete" - desativar ao invés de deletar
    - created_at: Data/hora de criação automática
    - updated_at: Data/hora da última atualização automática
    """
    id = models.AutoField(primary_key=True, verbose_name="ID")
    uuid = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True,
        verbose_name="UUID",
        help_text="Identificador único usado em URLs públicas"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Ativo",
        help_text="Desmarque para desativar o registro em vez de excluí-lo"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        abstract = True
        ordering = ['-created_at']