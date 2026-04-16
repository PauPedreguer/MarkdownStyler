**Nombre:**                                    **Apellidos:**

# Examen Linux

Una clínica dental se encuentra en Benidorm, Villajoyosa y Altea. Cada una de las ubicaciones tiene sus propios trabajadores, citas, salas y material.

En el directorio /home del ordenador ExamenSI se ha creado una carpeta que organizará todo el sistema y que tiene los siguientes ficheros y directorios:

```bash
mint@ExameSI:/home/clinica$ tree
.
├── Altea
│   ├── citas
│   │   ├── listaClientes.csv
│   │   ├── listaTarifas.csv
│   │   └── presupuesto.sh
│   ├── material
│   │   └── herramientas
│   └── salas
│       └── sala1
├── Benidorm
│   ├── citas
│   │   ├── listaClientes.csv
│   │   ├── listaTarifas.csv
│   │   └── presupuesto.sh
│   ├── material
│   │   ├── herramientas
│   │   └── maquinaRadiografias
│   │       ├── radiografiasRealizadas
│   │       └── usarMaquina.sh
│   └── salas
│       ├── recepcion
│       └── sala2
└── Villajoyosa
 ├── citas
 │   ├── listaClientes.csv
 │   ├── listaTarifas.csv
 │   └── presupuesto.sh
 ├── material
 │   └── herramientas
 └── salas
     └── recepcion
```

## Directorios y ficheros

**1. Crea el directorio *sala1* dentro de la carpeta salas de Villajoyosa/salas y de Benidorm/Salas.** (0.25p)

```bash
mint@ExamenSI:/home/clinica$
```

**2. Crea el directorio *recepción* dentro de la carpeta salas de Altea.** (0.25p)

```bash
mint@ExamenSI:/home/clinica$
```

**3. Usa la ruta relativa para situarte en la carpeta *radiografiasRealizadas*** (0.5p)

```bash
mint@ExamenSI:/home/clinica/Villajoyosa/material/herramientas$
```

**4. Usa la ruta absoluta para situarte en la carpeta herramientas de Altea.** (0.5p)

```bash
mint@ExamenSI:/home/clinica/Altea$
```

**5. Intercambia el contenido de las carpetas Altea y Villajoyosa. Crea un archivo nuevo dentro de las 2 para poder diferenciarlas.** (0.5p)

```bash
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
```

**6. Finalmente la clínica ha perdido la mayoría de sus clientes y tiene que cerrar. Elimina todo el contenido de la carpeta Villajoyosa** (0.25p)

```bash
mint@ExamenSI:/home/clinica$
```

**7. La clínica de Benidorm necesita tener los archivos *listaClientes.csv* y *listaTarifas.csv* de Altea. Copialos a la carpeta citas de Benidorm con los nombres *listaClientesAltea.csv* y *listaTarifasAltea.csv*** (0.5p)

```bash
mint@ExamenSI:/home/clinica/Altea/citas$
mint@ExamenSI:/home/clinica/Altea/citas$
```

**8. Escribe en el fichero *listaTarifas.csv*: limpieza 50€, ortodoncia 1000€. La coma indica un salto de línea. No puedes usar ningún programa externo(incluidos vim y nano)** (0.5p)

```bash
mint@ExamenSI:/home/clinica$
```

**9. Muestra el contenido del fichero *listaTarifas.csv*** (0.25p)

```bash
mint@ExamenSI:/home/clinica$
```

**10. Cuál seria el resultado de ejecutar este comando? Que indica el símbolo "~"** (0.5p)

```bash
mint@ExamenSI:~$ pwd
```

## Usuarios, grupos y permisos

En el ordenador ExamenSI, a parte de los usuarios creados por el sistema, solo tenemos el usuario mint en el grupo sudo. Puedes crear más usuarios o grupos si lo consideras necesario o conveniente.

**11. En está clínica habrá 3 dentistas: *dentAltea*, *dentBenidorm1* y *dentBenidorm2*. Además necesitaremos 2 auxiliares: *auxAltea* y *auxBenidorm*. También habrá 2 recepcionistas: *recepAltea* y *recepBenidorm*. Crea todos estos usuarios, de manera que todos tengan directorio personal, contraseña y aparezca el prompt al usarlos**(0.5p)

```bash
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
```

**12. En la clínica se asignarán distintos grupos a los usuarios, de manera que debes crear los grupos: *dentistas*, *auxiliares*, *recepcionistas*, *benidorm* y *altea*. No uses ningún script interactivo para crear los usuarios** (0.5p)

```bash
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
```

**13. El grupo primario de *dentAltea, auxAltea y recepAltea* debe ser *altea*. El grupo primario de *dentBenidorm, dentBenidorm2, auxBenidorm y recepBendorm* debe ser benidorm. Además *dentAltea*, *dentBenidorm1*, *dentBenidorm2* deben estar en el grupo dentistas, *auxAltea y auxBenidorm* en el grupo auxiliares y *recepBenidorm y recepAltea* en el grupo recepcionistas** (0.5p)

```bash
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
```

**14. Las carpetas *Benidorm/citas* y *Altea/citas* y los ficheros y carpetas que haya en su interior deben ser propiedad de los recepcionistas de cada pueblo. Los directorios *Benidorm/salas, Benidorm/material* y los directorios y ficheros de su interior serán propiedad de los dentBendorm1. Los directorios *Altea/salas, Altea/material* y los directorios y ficheros de su interior serán propiedad de los dentAltea.** (0.5p)

```bash
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
```

```bash
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
```

**15. Todos los dentistas deben poder leer y acceder al contenido de todas las salas (Benidorm y Altea). Los demás usuarios no tendrán permisos** (0.5p)

```bash
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$ 
mint@ExamenSI:/home/clinica$ 
mint@ExamenSI:/home/clinica$ 
mint@ExamenSI:/home/clinica$ 
mint@ExamenSI:/home/clinica$ 
```

**16. Solo el recepcionista que sea dueño de la carpeta puede crear, modificar y ejecutar ficheros en citas. Los dentistas del pueblo, auxiliares del pueblo y los otros recepcionistas podrán leerlos. Si se crearán más usuarios no podrían ni tan solo acceder a la carpeta ni archivos del interior** (1p)

```bash
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$ 
mint@ExamenSI:/home/clinica$ 
mint@ExamenSI:/home/clinica$ 
mint@ExamenSI:/home/clinica$ 
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$
mint@ExamenSI:/home/clinica$ 
```

**17. Los dentistas y auxiliares de cada pueblo pueden acceder a la carpeta material y herramientas de ese pueblo. Solo ellos podrán añadir, modificar, ejecutar o leer los ficheros. Los demás no pueden ver el contenido ni acceder a ellas** (1p)

```bash
mint@ExamenSI:/home/clinica/Benidorm/Material$ 
mint@ExamenSI:/home/clinica/Benidorm/Material$ 
mint@ExamenSI:/home/clinica/Benidorm/Material$ 
mint@ExamenSI:/home/clinica/Benidorm/Material$ 
mint@ExamenSI:/home/clinica/Benidorm/Material$ 
mint@ExamenSI:/home/clinica/Benidorm/Material$
mint@ExamenSI:/home/clinica/Benidorm/Material$
mint@ExamenSI:/home/clinica/Benidorm/Material$
mint@ExamenSI:/home/clinica/Benidorm/Material$
mint@ExamenSI:/home/clinica/Benidorm/Material$
mint@ExamenSI:/home/clinica/Benidorm/Material$
mint@ExamenSI:/home/clinica/Benidorm/Material$ 
```

**18. Todos los dentistas deben poder acceder a la carpeta *maquinaRadiografias* y a los archivos y carpetas de su interior. Todos los dentistas podrán crear nuevos ficheros o carpetas, ver los que ya hay y ejecutar el script *usarMaquina.sh*** (1p)

```bash
mint@ExamenSI:/home/clinica/Benidorm/Material$
mint@ExamenSI:/home/clinica/Benidorm/Material$ 
mint@ExamenSI:/home/clinica/Benidorm/Material$ 
mint@ExamenSI:/home/clinica/Benidorm/Material$ 
mint@ExamenSI:/home/clinica/Benidorm/Material$ 
mint@ExamenSI:/home/clinica/Benidorm/Material$
mint@ExamenSI:/home/clinica/Benidorm/Material$
mint@ExamenSI:/home/clinica/Benidorm/Material$
mint@ExamenSI:/home/clinica/Benidorm/Material$
```

**19. Cuál seria el resultado del siguiente comando después de realizar los ejercicios anteriores. Usa el formato de la terminal especificando al menos: permisos, owner, grupo y nombreDelFichero** (0.5p)

```bash
mint@ExamenSI:/home/clinica$ sudo ls -l Altea/salas
```
