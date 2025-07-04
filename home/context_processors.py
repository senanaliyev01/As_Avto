from asgiref.sync import sync_to_async
from .models import Header_Message, Firma, Mehsul, Sifaris
from django.contrib.auth.models import User

def is_async_request(request):
    # Django 4.1+ üçün, request.is_async mövcuddur
    return getattr(request, 'is_async', False)

async def global_data(request):
    context = {}
    context['header_messages'] = await sync_to_async(list)(Header_Message.objects.filter(aktiv=True).order_by('id'))
    context['total_user_count'] = await sync_to_async(User.objects.count)()
    context['total_seller_count'] = await sync_to_async(Mehsul.objects.exclude(sahib=None).values('sahib').distinct().count)()
    context['total_product_count'] = await sync_to_async(Mehsul.objects.count)()
    context['total_firma_count'] = await sync_to_async(Firma.objects.count)()
    context['brands'] = await sync_to_async(list)(Firma.objects.all())
    if request.user.is_authenticated:
        context['statistics'] = await sync_to_async(Sifaris.get_order_statistics)(request.user)
    return context 