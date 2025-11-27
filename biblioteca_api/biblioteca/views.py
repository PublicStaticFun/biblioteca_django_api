from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics, filters
from .models import Autor, Libro, Prestamo, Categoria
from .serializers import AutorSerializer, LibroSerializer, PrestamoSerializer, CategoriaSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

class AutorListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        q = request.query_params.get("q")
        nacionalidad = request.query_params.get("nacionalidad")
        autores = Autor.objects.filter(activo=True)
        if nacionalidad:
            autores = autores.filter(nacionalidad__iexact=nacionalidad)
        if q:
            autores = autores.filter(Q(nombre__icontains=q) | Q(apellido__icontains=q))
        serializer = AutorSerializer(autores, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AutorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AutorDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Autor, pk=pk)
    
    def get(self, request, pk):
        autor = self.get_object(pk)
        serializer = AutorSerializer(autor)
        return Response(serializer.data)
    
    def put(self, request, pk):
        autor = self.get_object(pk)
        serializer = AutorSerializer(autor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        autor = self.get_object(pk)
        autor.activo = False
        autor.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class LibroListCreateView(generics.ListCreateAPIView):
    queryset = Libro.objects.select_related("autor", "categoria").all()
    serializer_class = LibroSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, 
                       DjangoFilterBackend]
    search_fields = ["titulo", "isbn", "autor__nombre", "autor__apellido"]
    ordering_fields = ["precio", "fecha_publicacion", "titulo"]
    filterset_fields = {
        "autor": ["exact"],
        "categoria": ["exact"],
        "estado": ["exact"],
        "precio": ["lt", "gt", "exact"],
        "fecha_publicacion": ["year"],
    }

    def perform_create(self, serializer):
        serializer.save()

class CrearPrestamoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        libro_id = request.data.get("libro_id")
        libro = get_object_or_404(Libro, pk=libro_id)

        if libro.estado != "disponible":
            return Response({"detail": "Libro no disponible."}, status=status.HTTP_400_BAD_REQUEST)
        
        hoy = timezone.now().date()
        vencidos = Prestamo.objects.filter(usuario=user, activo=True, fecha_devolucion_esperada__lt=hoy, fecha_devolucion_real__isnull=True)
        if vencidos.exists():
            return Response({"detail": "Tienes libros vencidos, no puedes pedir prestamos"}, status=status.HTTP_400_BAD_REQUEST)
        
        activos = Prestamo.objects.filter(usuario=user, activo=True, fecha_devolucion_real__isnull=True).count()
        if activos >= 3:
            return Response({"detail": "Has alcanzado el máximo número de prestamos."}, status=status.HTTP_400_BAD_REQUEST)
        
        fecha_devolucion_esperada = hoy + timedelta(days=15)
        prestamo = Prestamo.objects.create(
            usuario=user,
            libro=libro,
            fecha_devolucion_esperada=fecha_devolucion_esperada
        )

        libro.estado = "prestado"
        libro.save(update_fields=["estado"])
        
        serializer = PrestamoSerializer(prestamo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class DevolverPrestamoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        prestamo = get_object_or_404(Prestamo, pk=pk)
        if not(request.user == prestamo.usuario or request.user.is_staff):
            return Response({"detail": "No tienes permiso para devolver este libro."}, status=403)
        if prestamo.fecha_devolucion_real:
            return Response({"detail": "Prestamo ya devuelto."}, status=400)
        
        hoy = timezone.now().date()
        prestamo.fecha_devolucion_real = hoy

        if hoy > prestamo.fecha_devolucion_esperada:
            dias = (hoy - prestamo.fecha_devolucion_esperada).days
            tarifa_diaria = 5.0
            prestamo.multa = Decimal(dias) * Decimal(str(tarifa_diaria))
        prestamo.activo = False
        prestamo.save()

        libro = prestamo.libro
        libro.estado = "disponible"
        libro.save(update_fields=["estado"])

        return Response({"detail": "Devolucion registrada.", "multa": prestamo.multa})
    
class CategoriaListCreateView(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoriaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]