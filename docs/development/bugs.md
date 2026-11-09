# Bugs de Silicio y Limitaciones Conocidas

??? bug "Bug 1: 65 flancos de SCK y skew CS_N/SCK (MappedSPIFlash)"
    * **Módulo afectado:** `MappedSPIFlash.v`
    * **Comportamiento:** Genera 65 flancos de reloj (`SCK`) mientras la señal `CS_N` permanece en nivel bajo.
    * **Causa:** El silicio físico muestrea en flanco ascendente (*posedge*), mientras que la simulación (`spiflash.v`) lo hace en descendente (*negedge*). Al bajar `CS_N` simultáneamente con `SCK` en las transacciones 1 y 2, el tiempo de setup es casi nulo, provocando que la Flash lea `0x06` (WREN) en lugar de `0x03` (READ).
    * **Estado:** A partir de la tercera transacción el reloj se estabiliza y la Flash procesa correctamente el comando `0x03`.

??? bug "Bug 2: Captura de 31 bits en lectura RAM (MappedSPIRAM)"
    * **Módulo afectado:** `MappedSPIRAM.v`
    * **Comportamiento:** La recepción finaliza cuando `rcv_bitcount <= 1`, ejecutando únicamente 31 desplazamientos.
    * **Impacto:** El bit 31 del registro `rcv_data` retiene el valor almacenado en la lectura anterior.

??? bug "Bug 3: Escritura WRITE sin comando WREN en RAM (MappedSPIRAM)"
    * **Módulo afectado:** `MappedSPIRAM.v`
    * **Comportamiento:** Envía la instrucción `WRITE` (`0x02`) sin transmitir previamente el comando de habilitación `WREN` (`0x06`).
    * **Impacto:** La memoria FRAM física ignora las operaciones de escritura. El modelo de simulación (`spiram.v`) enmascara el fallo al forzar `WEL=1` de forma artificial.

---

## Limitaciones Conocidas del Sistema

<table style="border-collapse: collapse; width: 100%; text-align: left; margin-top: 1rem;">
  <thead>
    <tr>
      <th style="border: 1px solid #777; padding: 8px;">Origen</th>
      <th style="border: 1px solid #777; padding: 8px;">Limitación Identificada</th>
      <th style="border: 1px solid #777; padding: 8px;">Efecto y Mitigación en Firmware</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><b>Reset SPI</b></td>
      <td style="border: 1px solid #777; padding: 8px;">Corrimiento de fase en la primera transacción tras el reset.</td>
      <td style="border: 1px solid #777; padding: 8px;">Mitigado en firmware al evitar la dependencia de que el primer <i>fetch</i> sea exacto.</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><b>Lectura Flash</b></td>
      <td style="border: 1px solid #777; padding: 8px;">Fallo en instrucciones de carga (<code>lb</code>, <code>lbu</code>, <code>lh</code>, <code>lhu</code>, <code>lw</code>) hacia la Flash.</td>
      <td style="border: 1px solid #777; padding: 8px;">Las cadenas de texto se embeben como valores inmediatos en el código fuente en lugar de leerse desde <code>.rodata</code> mediante punteros.</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 8px;"><b>UART RX</b></td>
      <td style="border: 1px solid #777; padding: 8px;">Pérdida ocasional de bytes en la recepción serie.</td>
      <td style="border: 1px solid #777; padding: 8px;">Causado por el <i>jitter</i> del reloj PWM del RP2040 al muestrear señales a baudios fijos. Se observa como caracteres <code>!</code> en terminal.</td>
    </tr>
  </tbody>
</table>