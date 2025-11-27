from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Autor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    nacionalidad = models.CharField(max_length=50)
    biografia = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre
    
class Libro(models.Model):
    ESTADOS = [
        ("disponible", "Disponible"),
        ("prestado", "Prestado"),
        ("mantenimiento", "Mantenimiento"),
    ]

    titulo = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    fecha_publicacion = models.DateField()
    numero_paginas = models.PositiveIntegerField()
    descripcion = models.TextField()
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name="libros")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name="libros")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="disponible")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
class Prestamo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prestamos")
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name="prestamos")
    fecha_prestamo = models.DateTimeField(auto_now_add=True)
    fecha_devolucion_esperada = models.DateField()
    fecha_devolucion_real = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    multa = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal(0))

    def __str__(self):
        return f"{self.usuario.username} - {self.libro.titulo}"