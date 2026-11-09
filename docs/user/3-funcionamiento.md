

##  Guía de Prueba en Hardware Real (Silicio)

Guía paso a paso para la verificación del SoC `tt_um_femto` (Tiny Tapeout SKY 25b) en la placa de desarrollo ejecutando el demo completo (`uart_full_demo.s`).

??? info "1. Requisitos de Hardware y Conexiones"
    **Componentes requeridos:**

    * **Demo Board:** Tiny Tapeout v3.2 (RP2040) con el proyecto `tt_um_femto` seleccionado (Dirección MUX: `238`, Shuttle `SKY 25b`).
    * **Memoria Flash SPI:** Programada con el firmware del sistema.
    * **Adaptador USB-Serial (3.3V):** Conexión de pines hacia la placa:
      * `RXD` (Adaptador) `TXD` ASIC (`uo_out[7]`)
      * `TXD` (Adaptador) `RXD` ASIC (`ui_in[2]`)
      * `GND` (Adaptador) `GND` (Placa)



??? code "2. Configuración del RP2040 (MicroPython)"
    Ejecute el siguiente script en el REPL de la demo board para inicializar el reloj, liberar los buses SPI y configurar el Multiplexor:

    ```python
    from ttboard.demoboard import DemoBoard
    from ttboard.mode import RPMode
    from machine import Pin

    tt = DemoBoard.get()
    tt.clock_project_stop()
    tt.mode = RPMode.ASIC_RP_CONTROL
    tt.shuttle.tt_um_femto.enable()
    tt.shuttle.enabled

    # Libera celdas SPI hacia la memoria física externa
    tt.pins.ui_in0.init(Pin.IN)   # MISO Flash
    tt.pins.ui_in1.init(Pin.IN)   # MISO RAM
    tt.pins.uo_out2.init(Pin.IN)  # CS_N Flash (Alta Impedancia)
    tt.pins.uo_out5.init(Pin.IN)  # CLK Flash
    tt.pins.uo_out3.init(Pin.IN)  # CS_N RAM
    tt.pins.uo_out4.init(Pin.IN)  # CLK RAM

    # Ciclo de Reset y activación de reloj PWM
    tt.reset_project(True)
    tt.clock_project_PWM(24000000)
    tt.reset_project(False)

    print("Frecuencia activa:", tt.auto_clocking_freq)
    ```

??? example "3. Puntos de Operación Validados (Frecuencia vs. Baudrate)"
    Debido a ligeras desviaciones de sincronía en el PWM del RP2040, seleccione una de las siguientes combinaciones confirmadas en silicio:

    <table style="border-collapse: collapse; width: 100%; text-align: left; margin-top: 10px;">
      <thead>
        <tr>
          <th style="border: 1px solid #777; padding: 8px;">Frecuencia del Sistema (clk_sys)</th>
          <th style="border: 1px solid #777; padding: 8px;">Baudrate en Terminal</th>
          <th style="border: 1px solid #777; padding: 8px;">Observaciones</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="border: 1px solid #777; padding: 8px;"><code>22.5 MHz</code></td>
          <td style="border: 1px solid #777; padding: 8px;"><code>~89,286</code></td>
          <td style="border: 1px solid #777; padding: 8px;">Lectura de instrucciones limpia y repetible.</td>
        </tr>
        <tr>
          <td style="border: 1px solid #777; padding: 8px;"><code>24.0 MHz</code></td>
          <td style="border: 1px solid #777; padding: 8px;"><code>90,000</code></td>
          <td style="border: 1px solid #777; padding: 8px;">Punto recomendado (Transmisión y Recepción simultáneas confirmadas).</td>
        </tr>
        <tr>
          <td style="border: 1px solid #777; padding: 8px;"><code>25.0 MHz</code></td>
          <td style="border: 1px solid #777; padding: 8px;"><code>115,200</code> (Estándar)</td>
          <td style="border: 1px solid #777; padding: 8px;">Permite conectar periferia externa fija como M5Stack Chain RGB.</td>
        </tr>
      </tbody>
    </table>

    > **Nota:** Valide la recepción empíricamente en cada sesión, ya que pequeñas variaciones de reloj pueden exigir ajustar el baudrate de la terminal.

### 4. Compilación y Programación del Firmware

Asegúrese de definir el archivo `uart_full_demo.o` dentro del `Makefile` y ejecute:

```bash
cd femtoRV/firmware/asm/
make
```

??? info "Ver detalles de la ejecución interna (Clic para expandir)"
    El script de compilación ejecuta los siguientes pasos automáticamente:

    1. **Ensamblado y Enlace:** Compila el archivo de entrada y utiliza el script de linker `bram.ld`.
    2. **Ajuste de Fases:** Aplica la corrección `fix_shift.py --dir right --fill 0` para compensar el desfasaje del silicio.
    3. **Grabado de Hardware:** Invoca `flashrom` mediante un programador `CH341A` para escribir el binario directamente en la memoria Flash SPI.

### 5. Lectura Serial de la Prueba

Conecte la terminal serie especificando el puerto y la velocidad seleccionada:

```bash
minicom -b 90000 -D /dev/ttyUSB0 -H
```

*Use el parámetro `-H` si desea conmutar la visualización entre modo texto y formato hexadecimal.*

??? abstract "6. Secuencia de Validación Ejecutada por el Demo"
    1. **Mensaje de Bienvenida:** Envía la cadena `"Hello World from femto UN\n\r"` por el puerto UART carácter a carácter.
    2. **Verificación Visual:** Conmuta el estado del LED (`uo_out[6]`) 2 veces a intervalos de `~0.5s`.
    3. **Bucle de Eco (Echo Loop):** Queda en espera de entrada de caracteres por `RX` y los retransmite de inmediato por `TX`.
    4. **Detección de Errores:** En caso de fallas de sincronía en el bus serie, retransmite el carácter `!` como alerta visual en la terminal.

??? warning "7. Guía de Resolución de Problemas (Troubleshooting)"
    <table style="border-collapse: collapse; width: 100%; text-align: left; margin-top: 10px;">
      <thead>
        <tr>
          <th style="border: 1px solid #777; padding: 8px;">Síntoma</th>
          <th style="border: 1px solid #777; padding: 8px;">Causa Probable</th>
          <th style="border: 1px solid #777; padding: 8px;">Acción Correctiva</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="border: 1px solid #777; padding: 8px;">Recepción continua de <code>0xFF</code></td>
          <td style="border: 1px solid #777; padding: 8px;">Firmware desactualizado en la Flash o lectura indebida de datos.</td>
          <td style="border: 1px solid #777; padding: 8px;">Recompile y vuelva a grabar la memoria comprobando que el archivo fuente se actualizó.</td>
        </tr>
        <tr>
          <td style="border: 1px solid #777; padding: 8px;">Texto corrupto / Caracteres ilegibles</td>
          <td style="border: 1px solid #777; padding: 8px;">Desalineación entre la velocidad del terminal y la frecuencia real de <code>clk_sys</code>.</td>
          <td style="border: 1px solid #777; padding: 8px;">Modifique el valor del parámetro <code>-b</code> en Minicom iterando entre los valores descritos en la tabla de frecuencias.</td>
        </tr>
        <tr>
          <td style="border: 1px solid #777; padding: 8px;">El LED no parpadea</td>
          <td style="border: 1px solid #777; padding: 8px;">El ciclo de conteo es demasiado extenso para la frecuencia del reloj configurada.</td>
          <td style="border: 1px solid #777; padding: 8px;">Ajuste las constantes del bucle de retardo en el código fuente en ensamblador.</td>
        </tr>
        <tr>
          <td style="border: 1px solid #777; padding: 8px;">Impresión recurrente del carácter <code>!</code></td>
          <td style="border: 1px solid #777; padding: 8px;">Variaciones periódicas en la señal de reloj generada por el RP2040.</td>
          <td style="border: 1px solid #777; padding: 8px;">Comportamiento esperado bajo el reloj PWM interno. Para aplicaciones que requieran tasa de error cero, utilice un generador de reloj externo.</td>
        </tr>
      </tbody>
    </table>