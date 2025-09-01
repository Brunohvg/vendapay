# Funções de verificação de tipo de usuário

def is_administrador(user):
    return getattr(user, "user_type", None) == "ADMIN"
    
def is_vendedor(user):
    """Verifica se o usuário é um vendedor."""
    return getattr(user, "user_type", None) == "SELLER"

def is_gerente(user):
    """Verifica se o usuário é um caixa."""
    return getattr(user, "user_type", None) == "MANAGER"

