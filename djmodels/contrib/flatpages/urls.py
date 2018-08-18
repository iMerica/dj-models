from djmodels.contrib.flatpages import views
from djmodels.urls import path

urlpatterns = [
    path('<path:url>', views.flatpage, name='djmodels.contrib.flatpages.views.flatpage'),
]
