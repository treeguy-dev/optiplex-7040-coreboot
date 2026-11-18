-- SPDX-License-Identifier: GPL-2.0-or-later

with HW.GFX.GMA;
with HW.GFX.GMA.Display_Probing;

use HW.GFX.GMA;
use HW.GFX.GMA.Display_Probing;

--  Port list derived from this unit's own VBT (data.vbt, captured from the
--  stock firmware). BDB block 2 child-device table, decoded:
--
--    handle          device_type            dvo_port   aux_ch
--    EFP1 0x0004     0x60d2 HDMI/DVI        DDI B      none     -> rear HDMI
--    EFP2 0x0040     0x60d6 DP++ dual-mode  DDI C      AUX C    -> rear DisplayPort 1
--    EFP3 0x0020     0x60d6 DP++ dual-mode  DDI D      AUX D    -> rear DisplayPort 2
--    EFP4 0x0010     0x68c6 DisplayPort     DDI E      AUX A    -> VGA daughter board
--
--  Cross-checks that make this map trustworthy:
--    * four distinct DDIs, each used exactly once
--    * DDI B carries no AUX channel, consistent with HDMI-only (0x60d2)
--    * DDI E reports AUX A, which is correct for Skylake - DDI E has no AUX of
--      its own and shares DDI A's, and it is why the board needs
--      SOC_INTEL_GFX_ENABLE_DDI_E_BIFURCATION for the VGA output
--    * matches the GPIO dump: GPP_I0/I1/I2 = DDPB/C/D_HPD with CTRLCLK+CTRLDATA
--      pairs on I5..I10, GPP_I3 = DDPE_HPD3 with no DDC pair
--    * matches Linux DRM enumeration: DP-1/2/3 + HDMI-A-1/2/3
--
--  libgfxinit naming on Skylake: DP1/HDMI1 = DDI B, DP2/HDMI2 = DDI C,
--  DP3/HDMI3 = DDI D. DDI B is listed as HDMI only because the VBT says it has
--  no AUX and therefore cannot run DisplayPort. DDI C and DDI D are DP++ so
--  they are probed as both DP and HDMI.
private package GMA.Mainboard is

   --  Note: DDI E (VGA daughter board) is not supported by libgfxinit on
   --  Skylake (eDP in libgfxinit maps to DIGI_A / DP_A panel sequencing,
   --  not DDI E); the OS driver (i915) initializes DDI E via data.vbt and
   --  SOC_INTEL_GFX_ENABLE_DDI_E_BIFURCATION.
   ports : constant Port_List :=
	(HDMI1,	-- DDI B - rear HDMI
	DP3,	-- DDI D - rear DisplayPort 2
	HDMI3,	-- DDI D - DP++ to HDMI
	DP2,	-- DDI C - rear DisplayPort 1
	HDMI2,	-- DDI C - DP++ to HDMI
	others	=> Disabled);

end GMA.Mainboard;
