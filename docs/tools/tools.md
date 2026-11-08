# Entorno de Trabajo y Herramientas

Installation of the following tools is required.
## Tools overview

!!! info "Tools Summary"
    1. **Yosys:** Síntesis lógica (convierte código a compuertas).
    2. **Icarus Verilog:** Compilación de netlists y simulación.
    3. **GTKWave:** Visualización de ondas (debugging).
    4. **ngspice:** Simulación de circuitos a nivel de transistor.
    5. **OpenSTA:** (Static Timing Analysis).
    6. **Magic:** (Layout).
    7. **OpenLane:** Sistema automatizado que integra todas las herramientas.
    8. **Python venv & cocotb:** framework where user are allow to write Verilog testbenches in Python. .

---

## Instalación Paso a Paso (Flujo ASIC)

A continuación, haz clic en la herramienta que desees en el menú lateral derecho, o desplázate hacia abajo para ver los comandos de instalación.

### 1. Yosys

!!! abstract "Instalación y Configuración"
    **Función:** Framework principal para síntesis Verilog-RTL.

    ```bash title="Terminal"
    git clone [https://github.com/YosysHQ/yosys.git](https://github.com/YosysHQ/yosys.git)
    cd yosys
    sudo apt install make
    sudo apt-get install build-essential clang bison flex libreadline-dev gawk tcl-dev libffi-dev git graphviz xdot pkg-config python3 libboost-system-dev libboost-python-dev libboost-filesystem-dev zlib1g-dev
    make config-gcc
    make
    sudo make install
    ```

### 2. Icarus Verilog

!!! abstract "Instalación y Configuración"
    **Función:** Compilador rápido para probar el código RTL.

    ```bash title="Terminal"
    sudo apt-get install iverilog
    ```

### 3. GTKWave

!!! abstract "Instalación y Configuración"
    **Función:** Interfaz gráfica para ver los resultados de la simulación (archivos .VCD).

    ```bash title="Terminal"
    sudo apt install gtkwave
    ```

### 4. ngspice

!!! abstract "Instalación y Configuración"
    **Función:** Simulador analógico para circuitos. Requiere compilación manual.

    ```bash title="Terminal"
    sudo apt-get install build-essential libxaw7-dev
    tar -zxvf ngspice-40.tar.gz
    cd ngspice-40
    mkdir release
    cd release
    ../configure --with-x --with-readline=yes --disable-debug
    make
    sudo make install
    ```

### 5. OpenSTA

!!! abstract "Instalación y Configuración"
    **Función:** Comprueba que las señales eléctricas lleguen a tiempo.

    ```bash title="Terminal"
    sudo apt-get install cmake clang gcc tcl swig bison flex
    git clone [https://github.com/The-OpenROAD-Project/OpenSTA.git](https://github.com/The-OpenROAD-Project/OpenSTA.git)
    cd OpenSTA
    mkdir build
    cd build
    cmake ..
    make
    sudo make install
    ```

### 6. Magic

!!! abstract "Instalación y Configuración"
    **Función:** Herramienta para editar y ver los polígonos del chip (GDSII).

    ```bash title="Terminal"
    sudo apt-get install m4 tcsh csh libx11-dev tcl-dev tk-dev libcairo2-dev mesa-common-dev libglu1-mesa-dev libncurses-dev
    git clone [https://github.com/RTimothyEdwards/magic](https://github.com/RTimothyEdwards/magic)
    cd magic
    ./configure
    make
    sudo make install
    ```

### 7. OpenLane

!!! warning "Instalación y Configuración (Requiere Docker)"
    

    **Paso 1: Dependencias del sistema**
    ```bash title="Terminal"
    sudo apt-get update
    sudo apt install -y build-essential python3 python3-venv python3-pip make git
    ```

    **Paso 2: Instalar Docker (Si no lo tienes)**
    ```bash title="Terminal"
    sudo apt install apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL [https://download.docker.com/linux/ubuntu/gpg](https://download.docker.com/linux/ubuntu/gpg) | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] [https://download.docker.com/linux/ubuntu](https://download.docker.com/linux/ubuntu) $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install docker-ce docker-ce-cli containerd.io
    sudo groupadd docker
    sudo usermod -aG docker $USER
    ```
    *(Nota: Es necesario cerrar y volver a abrir la terminal tras este paso para aplicar los permisos de usuario).*

    **Paso 3: Clonar repositorio e instalar**
    ```bash title="Terminal"
    cd $HOME
    git clone [https://github.com/The-OpenROAD-Project/OpenLane](https://github.com/The-OpenROAD-Project/OpenLane)
    cd OpenLane
    make
    make test
    ```

---

## Herramientas Adicionales y Verificación

Se recomienda ampliamente el uso de un entorno virtual de Python (`venv`) para aislar las dependencias del proyecto y evitar conflictos con los paquetes del sistema operativo.

### Entorno Virtual de Python (venv)

!!! example "Configuración del Entorno Virtual"
    **Función:** Permite instalar paquetes y paquetes de verificación de forma aislada.

    **Paso 1: Instalar soporte para venv**
    ```bash title="Terminal"
    sudo apt update
    sudo apt install python3-venv python3-pip
    ```

    **Paso 2: Crear el entorno virtual**
    ```bash title="Terminal"
    python3 -m venv venv
    ```

    **Paso 3: Activar el entorno virtual**
    ```bash title="Terminal"
    source venv/bin/activate
    ```
    *(Sabrás que está activo porque aparecerá `(venv)` al inicio de tu terminal).*

    **Paso 4: Desactivar cuando termines de trabajar**
    ```bash title="Terminal"
    deactivate
    ```

### cocotb

!!! tip "Instalación de cocotb"
    **Función:** Entorno de verificación de hardware basado en python

    **Paso 1: Activar el entorno virtual (Recomendado)**
    ```bash title="Terminal"
    source venv/bin/activate
    ```

    **Paso 2: Instalar cocotb mediante pip**
    ```bash title="Terminal"
    pip install cocotb
    ```

    **Paso 3: Verificar la instalación**
    ```bash title="Terminal"
    cocotb-config --version
    ```
    