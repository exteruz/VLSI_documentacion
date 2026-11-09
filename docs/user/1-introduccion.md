# Introducción al SoC y Estructura del Proyecto

Bienvenido a la Guía de Usuario del SoC **`tt_um_femto`**. Este proyecto implementa un Sistema en Chip (*System on Chip*) basado en la arquitectura de código abierto **RISC-V (RV32I)**, diseñado para fabricación en tecnología de 130 nm (**SkyWater SKY130**) a través del programa **Tiny Tapeout**.

---

## 1. Visión General del SoC

El SoC `tt_um_femto` integra un núcleo procesador RISC-V (RV32I) con controladores de memoria externa y perifericos de multiplicacion y uart.


## 2. Estructura de Archivos del Repositorio VLSI

El repositorio se divide en tres directorios principales que organizan el hardware, la simulación y el software:


### femto_UN/src/ — Descripción RTL 

??? info "Descripción de Módulos RTL "
    * **`femto.v`**: Top-level de la arquitectura del procesador (`tt_um_femto` y `femto`).
    * **`femtorv32_quark_un_irq.v`**: Núcleo del procesador FemtoRV32 Quark (RV32I). Contiene la máquina de estados finita de control, el banco de 32 registros, la ALU y la lógica de interrupciones.
    * **`MappedSPIFlash.v`**: Controlador de alta velocidad para memoria flash.
    * **`MappedSPIRAM.v`**: Controlador para memoria RAM externa.
    * **`perip_uart.v` / `uart.v`**: Transmisor y receptor UART serie con divisor de baudios configurable.
    * **`perip_mult.v` / `mult.v`**: Acelerador por hardware para operaciones de multiplicación de 32 bits.
    * **`bram.v`**: Memoria RAM estática interna para pruebas o almacenamiento rápido.

### tinytapeout/ — Entorno de Simulación y Verificación

Contiene los scripts y bancos de prueba para verificar el hardware antes de su fabricación:

??? info "Archivos y Modelos de Simulación "
    * **`Makefile`**: Automatiza el flujo de simulación RTL con Icarus Verilog (`make sim`) y los bancos de prueba.
    * **`tt_um_femto_cocotb.v`**: Módulo envoltorio (*wrapper*) para Cocotb. Expone señales internas del procesador (PC, registros `x1` a `x31`, buses) sin alterar el diseño de silicio.
    * **`cores/sim_spi_flash/`**: Modelo de simulación en Verilog de memoria Flash SPI/QSPI (`spiflash.v`).
    * **`cores/sim_spi_ram/`**: Modelo de simulación en Verilog de memoria RAM SPI (`spiram.v`).


### femtoRV/ — Firmware y Herramientas de Software

Contiene programas en ensamblador RISC-V y utilidades de conversión:
??? info "Firmware y Utilidades de Software "
    * **`firmware/asm/`**: Código fuente de programas de prueba en ensamblador (por ejemplo, `test_ram_load.S`).
    * **`fix_shift.py`**: Script de utilidad para pre-desplazar el binario 1 bit y compensar el bug del chip físico original.
---

## 3. Mapa de Memoria (Memory Map)

<table style="border-collapse: collapse; width: 100%; text-align: left;">
  <thead>
    <tr>
      <th style="border: 1px solid #777; padding: 8px;">Rango de Direcciones</th>
      <th style="border: 1px solid #777; padding: 8px;">Módulo / Periférico</th>
      <th style="border: 1px solid #777; padding: 8px; text-align: center;">Acceso</th>
      <th style="border: 1px solid #777; padding: 8px;">Descripción</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>0x0000_0000</code> - <code>0x0000_FFFF</code></td>
      <td style="border: 1px solid #777; padding: 8px;">Memoria Flash SPI / QSPI</td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Lectura (R)</td>
      <td style="border: 1px solid #777; padding: 8px;">Espacio para código de programa e instrucciones.</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>0x0001_0000</code> - <code>0x0001_FFFF</code></td>
      <td style="border: 1px solid #777; padding: 8px;">Memoria RAM SPI Externa</td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Lectura / Escritura (R/W)</td>
      <td style="border: 1px solid #777; padding: 8px;">Espacio para variables, pila (stack) y datos.</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>0x0040_0000</code></td>
      <td style="border: 1px solid #777; padding: 8px;">UART</td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Lectura / Escritura (R/W)</td>
      <td style="border: 1px solid #777; padding: 8px;">Registro de transmisión (TX) y recepción (RX).</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>0x0041_0000</code></td>
      <td style="border: 1px solid #777; padding: 8px;">GPIO / LEDs</td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Escritura (W)</td>
      <td style="border: 1px solid #777; padding: 8px;">Control de pines de salida y LEDs de depuración.</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>0x0042_0000</code></td>
      <td style="border: 1px solid #777; padding: 8px;">Multiplicador Hardware</td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Lectura / Escritura (R/W)</td>
      <td style="border: 1px solid #777; padding: 8px;">Entrada de operandos y lectura del resultado.</td>
    </tr>
  </tbody>
</table>
---

## 4. Puntos Críticos y Cosas a Tener en Cuenta

Al trabajar con este proyecto, es fundamental considerar los siguientes aspectos técnicos:


### 1. Mapeo de Pines de Tiny Tapeout

El chip utiliza la interfaz estándar de 24 pines de Tiny Tapeout:

<table style="border-collapse: collapse; width: 100%; text-align: left; margin-bottom: 1.5rem;">
  <thead>
    <tr>
      <th style="border: 1px solid #777; padding: 8px;">Bus</th>
      <th style="border: 1px solid #777; padding: 8px;">Pin</th>
      <th style="border: 1px solid #777; padding: 8px; text-align: center;">Dirección</th>
      <th style="border: 1px solid #777; padding: 8px;">Función / Descripción</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="3" style="border: 1px solid #777; padding: 8px; vertical-align: middle;"><b><code>ui_in[7:0]</code></b><br>(Entradas Dedicadas)</td>
      <td style="border: 1px solid #777; padding: 8px;"><code>ui_in[0]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Entrada</td>
      <td style="border: 1px solid #777; padding: 8px;">MISO de SPI Flash tradicional</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>ui_in[2]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Entrada</td>
      <td style="border: 1px solid #777; padding: 8px;">UART RX (Recepción serie)</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>ui_in[3]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Entrada</td>
      <td style="border: 1px solid #777; padding: 8px;">Petición de interrupción (IRQ)</td>
    </tr>
    <tr>
      <td rowspan="5" style="border: 1px solid #777; padding: 8px; vertical-align: middle;"><b><code>uo_out[7:0]</code></b><br>(Salidas Dedicadas)</td>
      <td style="border: 1px solid #777; padding: 8px;"><code>uo_out[0]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Salida</td>
      <td style="border: 1px solid #777; padding: 8px;">MOSI de SPI Flash tradicional</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>uo_out[2]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Salida</td>
      <td style="border: 1px solid #777; padding: 8px;">Chip Select Flash tradicional (<code>CS#</code>)</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>uo_out[5]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Salida</td>
      <td style="border: 1px solid #777; padding: 8px;">Reloj SPI SCK tradicional</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>uo_out[6]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Salida</td>
      <td style="border: 1px solid #777; padding: 8px;">LED indicador de estado</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>uo_out[7]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Salida</td>
      <td style="border: 1px solid #777; padding: 8px;">UART TX (Transmisión serie)</td>
    </tr>
    <tr>
      <td rowspan="8" style="border: 1px solid #777; padding: 8px; vertical-align: middle;"><b><code>uio[7:0]</code></b><br>(Pines Bidireccionales - QSPI PMOD)</td>
      <td style="border: 1px solid #777; padding: 8px;"><code>uio[0]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Salida</td>
      <td style="border: 1px solid #777; padding: 8px;">Chip Select Flash QSPI (<code>ce[0]</code>, activo en bajo)</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>uio[1]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Bidireccional</td>
      <td style="border: 1px solid #777; padding: 8px;">SIO0 / MOSI</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>uio[2]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Bidireccional</td>
      <td style="border: 1px solid #777; padding: 8px;">SIO1 / MISO</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>uio[3]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Salida</td>
      <td style="border: 1px solid #777; padding: 8px;">Reloj serie SCK (QSPI)</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>uio[4]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Bidireccional</td>
      <td style="border: 1px solid #777; padding: 8px;">SIO2</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>uio[5]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Bidireccional</td>
      <td style="border: 1px solid #777; padding: 8px;">SIO3</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>uio[6]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Salida</td>
      <td style="border: 1px solid #777; padding: 8px;">Chip Select RAM SPI (<code>ce[1]</code>, activo en bajo)</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><code>uio[7]</code></td>
      <td style="border: 1px solid #777; padding: 8px; text-align: center;">Salida</td>
      <td style="border: 1px solid #777; padding: 8px;">Señal auxiliar en nivel alto (<code>1'b1</code>)</td>
    </tr>
  </tbody>
</table>






### 3. Sincronización del Reset (`rst_n`)

El pin de reset es activo en bajo (`0` = reset, `1` = ejecución normal).

Para evitar metaestabilidad en el silicio, la señal se registra internamente en el flanco de bajada de reloj (`negedge clk`) antes de propagarse a los módulos del SoC.



### 5. Formato de Instrucciones y Little-Endian

 El procesador opera en modo nativo **Little-Endian**.s
 Las direcciones de instrucción deben estar siempre alineadas a múltiplos de 4 bytes (`PC[1:0] == 2'b00`).

---



