# Generación de Memoria OpenRAM 32x32 (32 bits)

En esta iteración se genera el macro de memoria estática síncrona **OpenRAM 32x32** (**32 palabras de 32 bits = 128 bytes**), con granularidad de escritura por byte (`wmask0[3:0]`), dimensionado para el estándar de la tecnología **SkyWater 130nm (Sky130A)**.

Esta memoria proporciona el doble de capacidad que la configuración anterior (128 bytes frente a 64 bytes) y conserva un bus de datos nativo de 32 bits, quedando lista como macro físico y lógico para su posterior integración con el procesador del sistema.

---

## 1. Especificaciones y Comparativa de Arquitectura

| Parámetro | Configuración 16x8 | Configuración 16x32 | **Nueva Configuración 32x32** |
| :--- | :--- | :--- | :--- |
| **Palabras (`num_words`)** | 16 | 16 | **32 palabras** |
| **Ancho de Palabra (`word_size`)** | 8 bits | 32 bits | **32 bits (4 bytes)** |
| **Capacidad Total** | 16 bytes (128 bits) | 64 bytes (512 bits) | **128 bytes (1024 bits)** |
| **Ancho de Dirección (`addr0`)** | 4 bits (`[3:0]`) | 4 bits (`[3:0]`) | **5 bits (`addr0[4:0]`)** |
| **Granularidad de Escritura** | Nivel de palabra (8b) | Byte (`wmask0[3:0]`) | **Nivel de byte (`wmask0[3:0]`)** |
| **Puertos** | 1 RW | 1 RW | **1 RW síncrono** |
| **Bus de Datos Físico (`din0`/`dout0`)** | 9 bits (8 + 1 spare) | 33 bits (32 + 1 spare) | **33 bits (32 + 1 spare)** |
| **Dimensiones Físicas (LEF)** | $230.13\ \mu\text{m} \times 84.58\ \mu\text{m}$ | $309.60\ \mu\text{m} \times 154.59\ \mu\text{m}$ | **$310.68\ \mu\text{m} \times 160.44\ \mu\text{m}$** |
| **Área del Macro** | $\approx 19,466\ \mu\text{m}^2$ | $\approx 47,861\ \mu\text{m}^2$ | **$\approx 49,846\ \mu\text{m}^2$** |
| **Ocupación en 4x2 Tiles** | $\approx 13.5\%$ | $\approx 33.2\%$ | **$\approx 34.5\%$** |

---

## 2. Generación del Macro con OpenRAM (`sky130_sram_32x32`)

### 2.1 Archivo de Configuración (`sram_32x32_config.py`)

Para compilar el macro con 32 palabras de 32 bits y soporte de máscara por byte en SkyWater 130nm, se empleó la siguiente configuración en OpenRAM:

```python
# Capacidad: 32 palabras x 32 bits (128 bytes)
word_size = 32              # Ancho de palabra: 32 bits
num_words = 32              # Profundidad: 32 palabras (5 bits de dirección)
write_size = 8              # Granularidad de escritura: genera el pin wmask0[3:0]

num_rw_ports = 1            # 1 puerto de lectura/escritura síncrono (1RW)
num_r_ports = 0
num_w_ports = 0
words_per_row = 1

# Requerido en Sky130 para simetría par en columnas de sensado
num_spare_cols = 1

tech_name = "sky130A"

# Opciones de compilación física
nominal_corner_only = True
analytical_delay = True
route_supplies = "ring"
check_lvsdrc = True

output_name = "sky130_sram_32x32"
output_path = "macro_32x32"
```

??? note "Detalles de Máscara de Escritura y Simetría en Sky130"
    1. **Máscara de Byte (`wmask0[3:0]`):** Con `write_size = 8` y `word_size = 32`, OpenRAM divide la fila en 4 campos de 8 bits. La señal `wmask0[0]` controla los bits `[7:0]`, `wmask0[1]` los bits `[15:8]`, `wmask0[2]` los bits `[23:16]` y `wmask0[3]` los bits `[31:24]`.
    2. **Bus de 33 bits y Columna de Reserva (`num_spare_cols = 1`):** SkyWater 130nm requiere paridad geométrica en las columnas de la matriz de celdas SRAM (`sky130_fd_bd_sram__sram_sp_cell_opt1`). Con 32 columnas de datos + 1 columna réplica, se agrega 1 columna de reserva para completar 34 columnas simétricas. Por ello, `din0` y `dout0` son de 33 bits (`[32:0]`), donde el bit `[32]` se fija a `0` y la entrada `spare_wen0` se conecta a nivel bajo (`1'b0`).
    3. **Direccionamiento de 5 bits (`addr0[4:0]`):** Con 32 palabras de profundidad ($2^5 = 32$), el decodificador de filas utiliza 5 líneas de dirección.

### 2.2 Proceso de Compilación Física

La síntesis de layout y verificación física del macro se realizó en el entorno de OpenRAM:

```bash
cd open_ram/OpenRAM
nix develop --extra-experimental-features "nix-command flakes" --command bash -c "
  export OPENRAM_HOME=\$(pwd)/compiler
  export OPENRAM_TECH=\$(pwd)/technology
  export PYTHONPATH=\$OPENRAM_HOME:\$PYTHONPATH
  .venv/bin/python sram_compiler.py sram_32x32_config.py
"
```

Los artefactos generados se ubicaron en `femto_UN/macros/`:
* `sky130_sram_32x32.gds`: Layout físico GDSII del macro ($310.68\ \mu\text{m} \times 160.44\ \mu\text{m}$).
* `sky130_sram_32x32.lef`: Información abstracta de geometría y pines para Place & Route (PnR).
* `sky130_sram_32x32_TT_1p8V_25C.lib`: Modelo de tiempos y potencia Liberty (*timing corner* típico 1.8V, 25°C).
* `sky130_sram_32x32.v`: Modelo funcional Verilog para simulación síncrona.
* `sky130_sram_32x32.sp`: Netlist SPICE con transistores extraídos para LVS.

??? info "Datasheet OpenRAM: sky130_sram_32x32 (Clic para expandir)"
    <iframe src="../../../assets/openram/sky130_sram_32x32.html" width="100%" height="700px" style="border: none;"></iframe>

* [Descargar archivo LEF (sky130_sram_32x32.lef)](../../assets/openram/sky130_sram_32x32.lef)

---

## 3. Presupuesto de Área en 4x2 Tiles

El presupuesto físico disponible para el diseño es de **4x2 tiles** en Tiny Tapeout:

* **Dimensiones totales del die (4x2 tiles):** $\approx 668\ \mu\text{m} \times 216\ \mu\text{m}$ (Área total $\approx 144,288\ \mu\text{m}^2$).
* **Dimensiones del Macro 32x32:** **$310.68\ \mu\text{m} \times 160.44\ \mu\text{m}$**.
* **Área ocupada por el Macro:** **$49,845.5\ \mu\text{m}^2$** ($\approx 34.5\%$ del área total).
* **Área libre disponible:** **$\approx 94,442\ \mu\text{m}^2$** ($\approx 65.5\%$).

El incremento de área respecto al macro 16x32 es de solo $1,985\ \mu\text{m}^2$ (+4.1%), pero otorga el doble de memoria utilizable, dejando suficiente holgura en el die para la integración del nuevo procesador y periféricos asociados.

---

## 4. Definición del Modelo Blackbox (`sky130_sram_32x32_bb.v`)

Para las herramientas de síntesis lógica (Yosys) y empaquetado del macro, se creó el módulo *blackbox* correspondiente respetando el pinout del archivo LEF:

```verilog
/* verilator lint_off UNUSED */
module sky130_sram_32x32 (
`ifdef USE_POWER_PINS
    inout  wire        vccd1,
    inout  wire        vssd1,
`endif
    input  wire        clk0,
    input  wire        csb0,
    input  wire        web0,
    input  wire [3:0]  wmask0,
    input  wire        spare_wen0,
    input  wire [4:0]  addr0,
    input  wire [32:0] din0,
    output wire [32:0] dout0
);
endmodule
/* verilator lint_on UNUSED */
```

El archivo se encuentra disponible en:
* `femto_UN/macros/sky130_sram_32x32_bb.v`
* `femto_UN/src/sky130_sram_32x32_bb.v`

---

## 5. Resumen de Archivos del Macro 32x32

| Archivo | Ubicación | Función |
| :--- | :--- | :--- |
| `sram_32x32_config.py` | `open_ram/OpenRAM/` | Configuración fuente del compilador OpenRAM. |
| `sky130_sram_32x32.gds` | `femto_UN/macros/` | Máscaras de layout físico GDSII. |
| `sky130_sram_32x32.lef` | `femto_UN/macros/` y `docs/assets/openram/` | Definición de geometría y pines para PnR. |
| `sky130_sram_32x32_TT_1p8V_25C.lib` | `femto_UN/macros/` | Librería de caracterización de tiempos y potencia. |
| `sky130_sram_32x32.v` | `femto_UN/macros/` | Modelo Verilog funcional de simulación. |
| `sky130_sram_32x32.sp` | `femto_UN/macros/` | Netlist SPICE con parásitos para LVS. |
| `sky130_sram_32x32_bb.v` | `femto_UN/macros/` y `femto_UN/src/` | Módulo Blackbox para síntesis con Yosys. |
| `sky130_sram_32x32.html` | `docs/assets/openram/` | Datasheet interactivo del macro OpenRAM. |


---

## 6. Viabilidad e Integración con el Procesador (`FemtoRV32 Quark IRQ`)

En la carpeta de descargas (`~/Downloads/femtorv32_quark_un_irq.v`) se identificó una versión actualizada del núcleo **FemtoRV32 Quark**. A continuación se analiza la viabilidad técnica de conectar la memoria **OpenRAM 32x32** generada y se detalla el procedimiento paso a paso para su futura integración.

### 6.1 Análisis del Procesador y Evaluación de Viabilidad

El archivo `femtorv32_quark_un_irq.v` implementa un procesador **RV32I** con máquina de estados finita explícita de 4 estados (`FETCH_INSTR`, `WAIT_INSTR`, `EXECUTE`, `WAIT_ALU_OR_MEM`) y soporte de interrupciones con registros CSR (`mstatus`, `mtvec`, `mepc`, `mcause`). 

Una mejora sustancial en esta versión es que el banco de registros (`registerFile`) ahora se lee de manera síncrona en el ciclo `WAIT_INSTR` (`rs1_ram <= registerFile[...]`), facilitando su inferencia física directa.

#### ¿Es posible implementar la memoria 32x32 en este procesador?
**Sí, es 100% viable y compatible.** Las razones técnicas son:

1. **Alineación de Bus de Datos (32 bits):**
   * El procesador dispone de un bus de datos de salida `mem_wdata[31:0]` y uno de entrada `mem_rdata[31:0]`.
   * El macro `sky130_sram_32x32` tiene palabras de 32 bits útiles (`din0[31:0]` y `dout0[31:0]`), por lo que no se requiere empaquetamiento ni conversión de anchos de palabra.

2. **Soporte Nativo de Máscara de Escritura por Byte (`wmask0[3:0]`):**
   * El procesador genera en la etapa de ejecución la señal `mem_wmask[3:0]` que activa exactamente los bytes que deben ser escritos según el tipo de instrucción:
     * `4'b0001`, `4'b0010`, `4'b0100` o `4'b1000` para `sb` (*store byte*).
     * `4'b0011` o `4'b1100` para `sh` (*store halfword*).
     * `4'b1111` para `sw` (*store word*).
   * El macro OpenRAM cuenta directamente con el puerto `wmask0[3:0]`, el cual habilita la escritura independiente de cada uno de los 4 bytes de la palabra seleccionada. La correspondencia es directa (1 a 1).

3. **Mapeo de Direcciones (5 bits de palabra):**
   * La memoria almacena 32 palabras ($2^5 = 32$), ocupando 128 bytes contiguos en el espacio de memoria.
   * La CPU emite direcciones orientadas a byte (`mem_addr[31:0]`).
   * Los bits `mem_addr[1:0]` corresponden al desplazamiento del byte dentro de la palabra (procesados internamente por la lógica de *load/store* de la CPU).
   * Los bits `mem_addr[6:2]` (5 bits) se conectan directamente a `addr0[4:0]` del macro para indexar las 32 palabras.

4. **Sincronismo y Tiempos de Respuesta (Single-Cycle SRAM):**
   * El macro OpenRAM en tecnología Sky130A posee un tiempo de acceso de lectura inferior a $3\text{ ns}$.
   * El procesador evalúa `needToWait = isLoad | isStore ...` pasando por `WAIT_ALU_OR_MEM`. Dado que la SRAM interna responde en el mismo ciclo de reloj, las señales de espera `mem_rbusy` y `mem_wbusy` para este espacio de memoria se mantienen en `0`, garantizando que las lecturas y escrituras se resuelvan en un solo ciclo sin penalizaciones de retardo.

---

### 6.2 Tabla de Conexión de Señales (Pin-to-Pin Mapping)

| Pin del Macro (`sky130_sram_32x32`) | Dirección | Señal en el Top-Level / SoC | Origen / Función |
| :--- | :--- | :--- | :--- |
| `clk0` | Entrada | `clk` | Reloj maestro síncrono del sistema. |
| `csb0` | Entrada | `sram_csb` | Chip Select activo en bajo: `~(sram_cs & (mem_rstrb \| wr))`. |
| `web0` | Entrada | `sram_web` | Write Enable activo en bajo: `~(sram_cs & wr)`. |
| `wmask0[3:0]` | Entrada | `mem_wmask[3:0]` | Máscara de byte generada por la CPU `FemtoRV32`. |
| `spare_wen0` | Entrada | `1'b0` | Deshabilita escritura en la columna de reserva. |
| `addr0[4:0]` | Entrada | `mem_addr[6:2]` | Selección de palabra (0 a 31) en los 128 bytes de la RAM. |
| `din0[32:0]` | Entrada | `{1'b0, mem_wdata[31:0]}` | Dato de escritura (bit 32 fijado a `0`). |
| `dout0[32:0]` | Salida | `sram_dout_raw[32:0]` | Dato leído (bits `[31:0]` van hacia el MUX de `mem_rdata`). |
| `vccd1` / `vssd1` | Alimentación | `1'b1` / `1'b0` | Rieles de potencia 1.8V y tierra (en modo `USE_POWER_PINS`). |

---

### 6.3 Procedimiento de Implementación Paso a Paso

Para implementar la memoria en el diseño cuando se decida integrarla con el procesador, se debe seguir la siguiente metodología sin alterar el núcleo `FemtoRV32`:

#### Paso 1: Asignar el Rango en el Mapa de Memoria
Se reserva una región de memoria en el decodificador de direcciones del SoC para la SRAM interna (por ejemplo, base `0x00410000` o la que defina la arquitectura):

```verilog
// Rango de 128 bytes: 0x00410000 a 0x0041007F
wire sram_cs = (mem_addr[31:16] == 16'h0041);
```

#### Paso 2: Generar las Señales de Control de Acceso
Se generan las señales de habilitación de chip select (`csb0`) y control de escritura (`web0`):

```verilog
wire wr = |mem_wmask;                        // Escritura activa si algún byte tiene wmask = 1
wire rd = mem_rstrb;                         // Lectura activa solicitada por la CPU

wire sram_csb = ~(sram_cs & (rd | wr));      // Activo en bajo cuando hay lectura o escritura en el rango
wire sram_web = ~(sram_cs & wr);             // Activo en bajo únicamente en ciclos de escritura
```

#### Paso 3: Instanciar el Macro de Memoria
En el módulo contenedor (Top-Level del SoC) se instancia `sky130_sram_32x32`:

```verilog
wire [32:0] sram_dout_raw;
wire [31:0] sram_dout = sram_dout_raw[31:0];

sky130_sram_32x32 u_sram (
`ifdef USE_POWER_PINS
    .vccd1(1'b1),
    .vssd1(1'b0),
`endif
    .clk0(clk),
    .csb0(sram_csb),
    .web0(sram_web),
    .wmask0(mem_wmask),
    .spare_wen0(1'b0),
    .addr0(mem_addr[6:2]),          // 5 bits: 32 palabras
    .din0({1'b0, mem_wdata[31:0]}), // 33 bits: bit spare = 0
    .dout0(sram_dout_raw)
);
```

#### Paso 4: Conectar el Multiplexor de Lectura (`mem_rdata`)
En el multiplexor central que alimenta `mem_rdata` de la CPU, se conecta la salida de la SRAM:

```verilog
always @(*) begin
    case (mem_addr[31:16])
        16'h0000: mem_rdata = flash_rdata;   // Memoria de programa Flash SPI
        16'h0040: mem_rdata = uart_rdata;    // Periférico UART
        16'h0041: mem_rdata = sram_dout;     // OpenRAM 32x32 (128 bytes)
        default:  mem_rdata = 32'h00000000;
    endcase
end
```

#### Paso 5: Gestión de Estados de Espera (`mem_rbusy` y `mem_wbusy`)
Dado que la OpenRAM interna es síncrona en un ciclo dentro del chip, cuando la CPU accede al rango `sram_cs`, no se deben activar líneas de espera:

```verilog
assign mem_rbusy = sram_cs ? 1'b0 : (flash_rbusy | spi_ram_rbusy);
assign mem_wbusy = sram_cs ? 1'b0 : spi_ram_wbusy;
```

---

### 6.4 Síntesis y Enrutamiento Físico en OpenLane / Tiny Tapeout

Para la integración física definitiva:
1. **Blackbox:** Incluir `sky130_sram_32x32_bb.v` en la lista `source_files` de `info.yaml`.
2. **Archivos Extra:** Declarar en `config.json`:
   * `EXTRA_LEFS`: `dir::../macros/sky130_sram_32x32.lef`
   * `EXTRA_GDS_FILES`: `dir::../macros/sky130_sram_32x32.gds`
   * `EXTRA_LIBS`: `dir::../macros/sky130_sram_32x32_TT_1p8V_25C.lib`
3. **Colocación:** Definir `location: [15, 30]` en la sección `MACROS` de `config.json` para aprovechar el presupuesto de **4x2 tiles**.
