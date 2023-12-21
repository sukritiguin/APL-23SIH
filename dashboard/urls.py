# yourapp/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.plotly_graph, name='dashboard'),
    path('aboutus/', views.aboutus_view, name='aboutus'),
    # path('dashboard/voltage-plot/', views.plot_voltage, name='plot_voltage'),
    # path('dashboard/voltage-current-analysis', views.plot_voltage_current_analysis, name='voltage_current_analysis'),
    path('dashboard/voltage-plot/', views.plot_voltage, name='plot_voltage'),
    path('dashboard/current-plot/', views.plot_current, name='plot_current'),
    path('send-report-email/', views.send_report_email, name='send_report_email'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
