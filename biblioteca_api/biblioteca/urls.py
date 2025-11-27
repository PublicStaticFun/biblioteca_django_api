from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .auth_views import RegistroView, LogoutView
from .views import AutorListCreateAPIView, AutorDetailAPIView, LibroListCreateView, CrearPrestamoView, DevolverPrestamoView, CategoriaListCreateView, CategoriaDetailView

urlpatterns = [
    path("auth/registro/", RegistroView.as_view()),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path("auth/logout/", LogoutView.as_view()),

    path("autores/", AutorListCreateAPIView.as_view()),
    path("autores/<int:pk>/", AutorDetailAPIView.as_view()),

    path("libros/", LibroListCreateView.as_view()),
    path("categorias/", CategoriaListCreateView.as_view(), name="categorias-list"),
    path("categorias/<int:pk>/", CategoriaDetailView.as_view(), name="categorias-detail"),
    
    path("prestamos/crear/", CrearPrestamoView.as_view()),
    path("prestamos/<int:pk>/devolver/", DevolverPrestamoView.as_view()),
]
