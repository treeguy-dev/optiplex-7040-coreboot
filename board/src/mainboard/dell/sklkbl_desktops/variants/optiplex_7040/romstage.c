/* SPDX-License-Identifier: GPL-2.0-only */

#include <soc/romstage.h>
#include <spd_bin.h>

void mainboard_memory_init_params(FSPM_UPD *mupd)
{
	/* Four DDR4 UDIMM slots (DIMM1..DIMM4) on SMBus 0x50..0x53 */
	struct spd_block blk = { .addr_map = { 0x50, 0x51, 0x52, 0x53 } };

	get_spd_smbus(&blk);
	dump_spd_info(&blk);

	FSP_M_CONFIG *mem_cfg = &mupd->FspmConfig;

	mem_cfg->DqPinsInterleaved = true;
	mem_cfg->CaVrefConfig      = 0;
	mem_cfg->MemorySpdDataLen  = blk.len;
	mem_cfg->MemorySpdPtr00    = (uintptr_t)blk.spd_array[0];
	mem_cfg->MemorySpdPtr10    = (uintptr_t)blk.spd_array[2];
	mem_cfg->MemorySpdPtr01    = (uintptr_t)blk.spd_array[1];
	mem_cfg->MemorySpdPtr11    = (uintptr_t)blk.spd_array[3];
}
