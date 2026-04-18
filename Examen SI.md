# Examen máquinas virtuales, instalación de sistemas operativos y gestión de discos y procesos.

Una vez descargado este documento se debe desconectar la conexión a la Red hasta finalizar el examen. Tampoco se podrán conectar USBs o medios extraibles una vez copiados los archivos ISO necesarios.

Antes de empezar no se podrá tener ninguna máquina virtual ya creada en Virtual Box ni acceder a ningún documento de memoria o documentación de las prácticas.

---

## 1. Crea una máquina virtual con las siguientes características: (1p)

- 2 cores

- 2 GB de RAM

- 40 GB de almacenamiento

- No se usará la instalación desatendida

- La máquina se debe encontrar en una carpeta llamada ExamenSI ubicada en el escritorio.

- Iso de windows 10 insertada

> **Comprobación:** Mostrar las características de la máquina virtual una vez creada. 

## 2. Instala windows (1p)

- Instalar windows 10 en el disco de 20GB

- Realizar el proceso de instalación local (sin cuenta microsoft) con los siguientes parámetros:
  
  - **Nombre de usuario:** Examen(Nombre)SI
  
  - **Contraseña:** windows10
    
        

> **Comprobación:** Mostrar el acceso al sistema operativo  con las credenciales anteriores

## 3. Instalar las guest additions (1p)

- Instala las guest additions 

- Activa el portapapeles bidireccional

- Activa el cambio de resolución

- Crea una carpeta compartida ubicada en el escritorio del ordenador anfitrión

> **Comprobaciones:** 
> 
> - Copiar y pegar un texto
> 
> - Cambiar a modo pantalla completa
> 
> - Compartir un archivo mediante la carpeta compartida 

## 4. Clona la máquina virtual creada (0.5p)

- Clona la máquina virtual que acabas de crear 

- Usa los siguientes parámetros
  
  - **Nombre:** DualBoot(Nombre)
  
  - **Ruta:** Escritorio/ExamenSI

- Genera una nueva dirección MAC

> **Comprobación:** Hay una máquina con windows en la ruta indicada 

## 5. Instala linux mint en la misma máquina virtual (2p)

- Instala linux mint en el mismo disco con arranque dual

> **Comprobación:** Puede arrancar desde los 2 sistemas operativos  

## 6. Instala las guest additions en linux mint (1p)

- Instala las guest additions

- Activa el portapapeles bidireccional

- Activa el cambio de resolución

> **Comprobaciones:**
> 
> - Copiar y pegar un texto
> 
> - Cambiar a modo pantalla completa 

## 7. Crea una instantánea en Linux mint (0.5p)

- Crea una instantánea sin archivos en el escritorio

- Cambia el fondo de pantalla y añade un archivo.txt en el escritorio con una frase

- Restaura la instantánea anterior

> **Comprobación:** Se restaura la instantánea y vuelve al fondo original sin el archivo 

## 8. Revisa el activity (0.5p)

- Revisar la actividad y consumo de las máquinas virtuales

> Comprobación: Captura con RAM y CPU consumida por la máquina virtual arrancando en windows y en linux 

## 9. Añadir discos y crear particiones (2p)

- Añade 2 discos de 5GB a la máquina virtual

- Crea una tabla de particiones en el formato más moderno en cada disco

- El primer disco tendrá una partición que ocupará todo el disco y se podrá acceder a él desde Linux Mint y Windows 10

- El segundo disco tendrá una partición de 3GB y una de 2GB y solo será accesible desde Linux Mint

> **Comprobación:** Guardar archivos txt desde distintos sistemas operativos y muestra los formatos de los discos 

## 10. Cierre forzoso de tareas en linux mint (0.5p)

- Abre una aplicación en linux 

- Muestra los procesos abiertos en la terminal

- Cierra de forma forzosa el proceso de la aplicación que has abierto desde la terminal

```bash
sudo apt install gparted
```

> **Comprobación:** Se cierra la aplicación abierta desde la consola
