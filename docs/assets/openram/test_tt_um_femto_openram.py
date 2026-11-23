import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, First, RisingEdge

# Programa de prueba OpenRAM 32x32 (128 bytes, palabras de 32 bits con wmask0[3:0]):
# 1. lui x1, 0x00410      (x1 = 0x00410000, base de OpenRAM)
# 2. lui x2, 0x12345; addi x2, x2, 0x64B  (x2 = 0x1234564B)
# 3. sw  x2, 0(x1)        (Escribe palabra completa de 32 bits en OpenRAM[0], wmask0 = 4'b1111)
# 4. lw  x3, 0(x1)        (Lee de vuelta palabra completa de 32 bits -> x3 = 0x1234564B)
# 5. li  x6, 0xAA         (x6 = 0xAA)
# 6. sb  x6, 1(x1)        (Escribe byte en offset 1: prueba wmask0 = 4'b0010 sin alterar bytes 0, 2, 3)
# 7. lw  x3, 0(x1)        (Lee de vuelta palabra -> x3 = 0x1234AA4B)
# 8. lui x4, 0x00400      (x4 = 0x00400000, base UART)
# 9. sb  x3, 8(x4)        (Transmite byte 0 'K' [0x4B] por UART)
# 10. li x5, 0x08; sb x5, 16(x4); sb x0, 16(x4)  (Dispara y limpia TX UART)
# 11. loop: j loop
OPENRAM_PROGRAM = bytes([
    0x13, 0x00, 0x00, 0x00,  # 0x00: nop
    0xB7, 0x00, 0x41, 0x00,  # 0x04: lui x1, 0x00410
    0x37, 0x51, 0x34, 0x12,  # 0x08: lui x2, 0x12345
    0x13, 0x01, 0xB1, 0x64,  # 0x0C: addi x2, x2, 0x64B (x2 = 0x1234564B)
    0x23, 0xA0, 0x20, 0x00,  # 0x10: sw x2, 0(x1)       (wmask0 = 4'b1111)
    0x83, 0xA1, 0x00, 0x00,  # 0x14: lw x3, 0(x1)       (x3 = 0x1234564B)
    0x13, 0x03, 0xA0, 0x0A,  # 0x18: li x6, 0xAA
    0xA3, 0x80, 0x60, 0x00,  # 0x1C: sb x6, 1(x1)       (wmask0 = 4'b0010)
    0x83, 0xA1, 0x00, 0x00,  # 0x20: lw x3, 0(x1)       (x3 = 0x1234AA4B)
    0x37, 0x02, 0x40, 0x00,  # 0x24: lui x4, 0x00400
    0x23, 0x04, 0x32, 0x00,  # 0x28: sb x3, 8(x4)       (carga byte 0 [0x4B = 'K'] a UART)
    0x93, 0x02, 0x80, 0x00,  # 0x2C: li x5, 0x08
    0x23, 0x08, 0x52, 0x00,  # 0x30: sb x5, 16(x4)      (tx_wr = 1)
    0x23, 0x08, 0x02, 0x00,  # 0x34: sb x0, 16(x4)      (tx_wr = 0)
    0x6F, 0x00, 0x00, 0x00,  # 0x38: j loop
])


class SpiFlash:
    def __init__(self, dut, contents):
        self.dut = dut
        self.contents = contents
        self.reads = []

    def read_byte(self, address):
        if address < len(self.contents):
            return self.contents[address]
        return 0

    async def run(self):
        self.dut.flash_miso.value = 0

        while True:
            await FallingEdge(self.dut.flash_cs_n)
            request = 0

            for _ in range(32):
                await RisingEdge(self.dut.flash_clk)
                request = (request << 1) | int(self.dut.flash_mosi.value)

            command = (request >> 24) & 0xFF
            address = request & 0xFFFFFF
            assert command == 0x03, f"Comando SPI inesperado: 0x{command:02x}"
            self.reads.append((command, address))

            while not int(self.dut.flash_cs_n.value):
                value = self.read_byte(address)
                address += 1

                for bit in range(7, -1, -1):
                    await First(
                        FallingEdge(self.dut.flash_clk),
                        RisingEdge(self.dut.flash_cs_n),
                    )
                    if int(self.dut.flash_cs_n.value):
                        self.dut.flash_miso.value = 0
                        break
                    self.dut.flash_miso.value = (value >> bit) & 1
                else:
                    continue
                break


async def uart_rx_monitor(dut, received_bytes, clks_per_bit=208):
    """Decodifica tramas UART 8N1 en dut.uart_tx (27 MHz / 115200 baud = 234 ciclos/bit)."""
    while True:
        await FallingEdge(dut.uart_tx)
        await ClockCycles(dut.clk, clks_per_bit // 2)
        if int(dut.uart_tx.value) != 0:
            continue

        byte_val = 0
        for bit_idx in range(8):
            await ClockCycles(dut.clk, clks_per_bit)
            byte_val |= (int(dut.uart_tx.value) & 1) << bit_idx

        await ClockCycles(dut.clk, clks_per_bit)
        received_bytes.append(byte_val)
        char_repr = chr(byte_val) if 32 <= byte_val < 127 else f"\\x{byte_val:02x}"
        dut._log.info(f"[UART RX] Byte recibido en pin uart_tx: 0x{byte_val:02X} ('{char_repr}')")


@cocotb.test()
async def test_openram_write_read_uart(dut):
    """Verifica OpenRAM 32x32: escritura y lectura de 32 bits (sw/lw), byte-mask (sb) y salida UART."""
    dut.rst_n.value = 0
    dut.uart_rx.value = 1
    dut.ram_miso.value = 0
    dut.flash_miso.value = 0

    try:
        clock = Clock(dut.clk, 37038, units="ps")  # ~27 MHz
    except TypeError:
        clock = Clock(dut.clk, 37038, unit="ps")
    cocotb.start_soon(clock.start())

    flash = SpiFlash(dut, OPENRAM_PROGRAM)
    cocotb.start_soon(flash.run())

    uart_bytes = []
    cocotb.start_soon(uart_rx_monitor(dut, uart_bytes))

    await ClockCycles(dut.clk, 8)
    dut.rst_n.value = 1

    sram_read_verified = False
    for _ in range(20000):
        await RisingEdge(dut.clk)

        if not sram_read_verified:
            try:
                # Verificamos que x3 cargue 0x1234AA4B (demuestra escritura word 32b y byte mask parcial)
                if int(dut.dut.femto0.CPU.registerFile[3].value) == 0x1234AA4B:
                    sram_read_verified = True
                    dut._log.info("[SRAM OK] Registro x3 cargó 0x1234AA4B desde OpenRAM 32x32")
            except Exception:
                pass

        if len(uart_bytes) >= 1:
            break
    else:
        raise AssertionError(
            f"Timeout esperando UART; bytes recibidos={uart_bytes}, "
            f"PC=0x{int(dut.debug_pc.value):06x}"
        )

    assert sram_read_verified, "El registro x3 nunca recibió 0x1234AA4B desde OpenRAM 32x32"
    assert uart_bytes[0] == 0x4B, (
        f"Se esperaba 'K' (0x4B) por UART, se recibió: {uart_bytes}"
    )
    dut._log.info("Prueba OpenRAM 32x32 + UART hardware completada con éxito: 0x1234AA4B y 'K' (0x4B) verificados.")
