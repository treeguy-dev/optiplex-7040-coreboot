/* SPDX-License-Identifier: GPL-2.0-only */

#include <soc/gpe.h>
#include <soc/gpio.h>
#include "../../../include/variant/gpio.h"

/*
 * Pads that must be right before ramstage runs.
 *
 * SMBus (GPP_C0/C1) is the one entry that is not optional: romstage reads the
 * DDR4 SPD EEPROMs at 0x50..0x53 over SMBus (see romstage.c), so these pads have
 * to be in native mode before mainboard_memory_init_params() runs. They come out
 * of reset native on Sunrise Point, so this is belt-and-braces rather than a fix
 * for an observed failure - but memory init is not where we want to discover we
 * were relying on a reset default.
 *
 * GPP_C8/C9 are the PCH UART0 pads. This board does not use them for console -
 * the coreboot console is the SCH555x LPC UART at 0x3f8 (confirmed present as a
 * real 16550A, PNP0501, IRQ 4). They are parked as low outputs, matching the
 * OEM configuration and the OptiPlex 5040 SFF port.
 */
static const struct pad_config early_gpio_table[] = {
	PAD_CFG_NF(GPP_C0, NONE, DEEP, NF1),	/* SMBCLK  - DIMM SPD */
	PAD_CFG_NF(GPP_C1, NONE, DEEP, NF1),	/* SMBDATA - DIMM SPD */

	PAD_CFG_GPO(GPP_C8, 0, PLTRST),		/* PCH UART0_RXD - unused */
	PAD_CFG_GPO(GPP_C9, 0, PLTRST),		/* PCH UART0_TXD - unused */
};

void variant_configure_early_gpios(void)
{
	gpio_configure_pads(early_gpio_table, ARRAY_SIZE(early_gpio_table));
}
