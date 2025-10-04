from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.urls import path
from django.template.response import TemplateResponse
from django.utils.html import format_html

# Register your models here.

class AdministradorSite(admin.AdminSite):
    site_header = "Administrador TRex"
    site_title = "Administrador TRex"
    index_title = "Panel de Control"
    index_template = "administrador/index.html"
    login_template = "administrador/login.html"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('vista-personalizada/', self.admin_view(self.vista_personalizada), name='vista_personalizada'),
            path('reportes/', self.admin_view(self.reportes_view), name='reportes'),
        ]
        return custom_urls + urls
    
    def vista_personalizada(self, request):
        context = {
            **self.each_context(request),
            'title': 'Vista Personalizada TRex',
            'opts': self._registry,
        }
        return TemplateResponse(request, "administrador/vista_personalizada.html", context)
    
    def reportes_view(self, request):
        stats = {
            'total_usuarios': User.objects.count(),
            'usuarios_activos': User.objects.filter(is_active=True).count(),
            'total_grupos': Group.objects.count(),
            'staff_users': User.objects.filter(is_staff=True).count(),
        }
        
        context = {
            **self.each_context(request),
            'title': 'Reportes TRex',
            'stats': stats,
        }
        return TemplateResponse(request, "administrador/reportes.html", context)

# Crear instancia
administrador_site = AdministradorSite(name='administrador')

# Registrar modelos
administrador_site.register(User, UserAdmin)
administrador_site.register(Group, GroupAdmin)