from django.conf import settings
from datetime import datetime
from cadastros_basicos.models import OfertaDeTurma

def jam_mei_context_processor(request):
    """
    Essa função é chamada no fim do processamento de cada view
    """
    ctx = dict(
        super_template='admin/base.html',
        debug=settings.DEBUG,
        now=datetime.now(),
        valores_sugeridos = OfertaDeTurma.objects.all()
    )
    return ctx
