# WS2 — Grupo 17: trayectoria del número 7

Robot diferencial exportado de Fusion 360, simulado en ROS 2 Jazzy y Gazebo Harmonic.
El código conserva el nombre del paquete entregado: `Samuel_WS2_description`.
ROS recomienda nombres en minúsculas; este nombre produce una advertencia al compilar.

## Contenido

- `src/Samuel_WS2_description/urdf/`: modelo, colores y plugin diferencial.
- `src/Samuel_WS2_description/meshes/`: geometría STL del CAD original.
- `src/Samuel_WS2_description/Samuel_WS2_description/trayectoria.py`: seguimiento del 7 por odometría.
- `src/Samuel_WS2_description/config/trayectoria.rviz`: robot coloreado y recorrido medido.
- `src/Samuel_WS2_description/launch/grupo17.launch.py`: inicio de la demostración.

## Ejecutar en Ubuntu 24.04 con ROS 2 Jazzy

Dependencias: ROS 2 Jazzy desktop, `ros-jazzy-ros-gz`, `ros-jazzy-xacro`,
`ros-jazzy-joint-state-publisher-gui` y `python3-colcon-common-extensions`.
No se necesita ros2_control: este proyecto utiliza el plugin DiffDrive de Gazebo.

Desde la raíz del proyecto:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch Samuel_WS2_description grupo17.launch.py
```

En esta computadora, la raíz desde WSL es:
`/mnt/c/Users/luisf/Documents/Robots_WS/WS2_proyecto`.
El controlador comienza después de 20 segundos y espera mensajes de odometría.
En RViz aparece una línea naranja con el recorrido real de la odometría.
Al terminar, publica velocidad cero continuamente. Ctrl+C cierra la demostración.
Para repetir desde el origen, cerrar la ejecución completa y lanzarla otra vez.
No ejecutar dos controladores simultáneamente.

## Ejecución separada

Terminal 1, con el entorno cargado:

```bash
ros2 launch Samuel_WS2_description gazebo.launch.py
```

Terminal 2, con el entorno cargado:

```bash
ros2 run Samuel_WS2_description trayectoria --ros-args -p grupo:=17 -p use_sim_time:=true
```

Terminal 3, desde la raíz del proyecto y con el entorno cargado:

```bash
rviz2 -d src/Samuel_WS2_description/config/trayectoria.rviz --ros-args -p use_sim_time:=true
```

Los puentes `/cmd_vel`, `/odom`, `/tf`, `/joint_states` y `/clock` arrancan con Gazebo.
No es necesario abrir otro parameter_bridge.

## Diseño y correcciones

El grupo 17 dibuja el dígito `17 % 10 = 7`. Los puntos, relativos a la posición inicial,
son `(0,0)`, `(1,0)` y `(0,-2)` metros: barra superior y diagonal descendente.
El controlador gira hacia cada punto y avanza hasta quedar a menos de 2.5 cm;
limita la velocidad a 0.12 m/s y 0.65 rad/s. Si deja de llegar odometría durante
un segundo, ordena detenerse. Es una demostración de simulación.

La odometría de control procede de `OdometryPublisher`: mide la posición física
del cuerpo en Gazebo. No se usa la integración de los encoders para dibujar el
trazo, porque puede dar un recorrido aparente si las ruedas patinan. Esto utiliza
información ideal de la simulación; en un robot real se necesitaría localización.

Se conservan las mallas visuales e inercias exportadas. Se añadieron colores azul, naranja,
negro y gris; se alineó el eje de la rueda derecha con el izquierdo; se añadió
DiffDrive y se corrigió `setup.cfg` para instalar el ejecutable en el paquete correcto.
El radio de rueda es 0.0375 m. La separación entre centros de las bandas de rodadura
es 0.16 m según los STL (y=±0.08); los pivotes del CAD están en las caras interiores
(y=±0.07). Para el contacto físico se utilizan cilindros en las ruedas y una esfera
sin fricción en el apoyo; se conserva su unión fija para que Gazebo aplique esa
fricción al apoyo por separado. Esto permite girar sin arrastrar la malla del apoyo.

## Entrega

Repositorio: https://github.com/FernandoVB01/WS2_Robot_Diferencial_17

Video: [WS2_Grupo17_Simulacion.mp4](evidencias/WS2_Grupo17_Simulacion.mp4).
Grabación real de RViz conectado a Gazebo, a 10 fotogramas por segundo, sin acelerar.
Muestra el modelo coloreado y la trayectoria obtenida de la posición física del robot.
La pantalla virtual usada para capturar el video no modifica la simulación.

Validación ejecutada el 21 de octubre de 2026:

- Compilación con `colcon build --symlink-install`: correcta.
- Robot cargado en Gazebo Harmonic con ROS 2 Jazzy.
- Recorrido completo del 7 y parada final comprobados.
- Objetivo final: `(0, -2)` m; posición final: `(0.00996, -1.97814)` m.
- Error final de posición: aproximadamente 2.40 cm, dentro de la tolerancia de 2.5 cm.
- Datos: [odometría](evidencias/odometria_grupo17.csv) y [resultado](evidencias/validacion.json).

Entregar el enlace del repositorio junto con el video.
No subir `build/`, `install/` ni `log/`. El video debe mostrar el robot coloreado,
el movimiento completo y el 7 terminado en RViz. No confundir el tutorial original
con la grabación propia de la simulación. Se puede adjuntar el MP4 por separado.

## Referencias

- Tutorial suministrado: https://www.youtube.com/watch?v=QeWczNtf1Eo
- Exportador indicado en los adjuntos: https://github.com/runtimerobotics/fusion360-urdf-ros2
- DiffDrive de Gazebo Harmonic: https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1DiffDrive.html
- OdometryPublisher: https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1OdometryPublisher.html

Los archivos originales proceden de los adjuntos del usuario. No se declara una
licencia nueva sobre el CAD recibido.
