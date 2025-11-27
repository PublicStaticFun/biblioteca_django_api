from rest_framework import serializers
from django.utils import timezone
from .models import Autor, Categoria, Libro, Prestamo
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

class AutorSerializer(serializers.ModelSerializer):
    edad = serializers.SerializerMethodField()

    class Meta:
        model = Autor
        fields = ["id", "nombre", "apellido", "fecha_nacimiento", "nacionalidad", "biografia", "activo", "edad"]

    def get_edad(self, obj):
        hoy = timezone.now().date()
        born = obj.fecha_nacimiento
        return hoy.year - born.year - ((hoy.month, hoy.day) < (born.month, born.day))
    
    def validate_nombre(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("El nombre solo debe contener letras.")
        return value
    
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion"]

class LibroSerializer(serializers.ModelSerializer):
    autor = AutorSerializer(read_only=True)
    autor_id = serializers.PrimaryKeyRelatedField(queryset=Autor.objects.filter(activo=True), write_only=True, source="autor")
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all(), write_only=True, source='categoria')
    disponibilidad = serializers.SerializerMethodField()

    class Meta:
        model = Libro
        fields = ["id","titulo","isbn","fecha_publicacion","numero_paginas","descripcion","autor","autor_id","categoria","categoria_id","estado","precio","fecha_agregado","disponibilidad"]

    def get_disponibilidad(self, obj):
        return obj.estado == "disponible"
    
    def validate_isbn(self, value):
        if len(value) not in (10, 13):
            raise serializers.ValidationError("ISBN debe tener 10 o 13 caracteres")
        return value

class PrestamoSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='usuario')
    libro = LibroSerializer(read_only=True)
    libro_id = serializers.PrimaryKeyRelatedField(queryset=Libro.objects.all(), write_only=True, source='libro')

    class Meta:
        model = Prestamo
        fields = ["id","usuario","usuario_id","libro","libro_id","fecha_prestamo","fecha_devolucion_esperada","fecha_devolucion_real","activo","multa"]
        read_only_fields = ["fecha_prestamo", "multa"]

        def validate(self, data):
            libro = data.get("libro")
            usuario = data.get("usuario")
            if libro.estado != "disponible":
                raise serializers.ValidationError("El libro no está disponible para este prestamo.")
            return data