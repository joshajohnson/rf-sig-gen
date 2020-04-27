#include "max2871_registers.h"
#include <stdint.h>

static uint32_t registers[6];

void max2871RegsInit()
{
	registers[0] = 0x0;
	registers[1] = 0x1;
	registers[2] = 0x2;
	registers[3] = 0x3;
	registers[4] = 0x8c; // Disable RFOUT_A and _B
	registers[5] = 0x5;

}

uint32_t max2871GetRegister(uint8_t reg)
{
	return registers[reg];
}

// 0 = Frac-N, 1 = Int-N
void max2871Set_INT(uint32_t j)
{
	registers[0] &= ~(0x1 << 31);
	registers[0] |= j << 31;
}

// Integer Division Value
void max2871Set_N(uint32_t j)
{
	registers[0] &= ~(0xFFFF << 15);
	registers[0] |= j << 15;
}

// Fractional Division Value
void max2871Set_FRAC(uint32_t j)
{
	registers[0] &= ~(0xFFF << 3);
	registers[0] |= j << 3;
}

void max2871Set_CPOC(uint32_t j)
{
	registers[1] &= ~(0x1 << 31);
	registers[1] |= j << 31;
}

// Charge Pump Linearity
void max2871Set_CPL(uint32_t j)
{
	registers[1] &= ~(0x3 << 29);
	registers[1] |= j << 29;
}

// Charge Pump Test
void max2871Set_CPT(uint32_t j)
{
	registers[1] &= ~(0x3 << 27);
	registers[1] |= j << 27;
}

// Phase Value
void max2871Set_P(uint32_t j)
{
	registers[1] &= ~(0xFFF << 15);
	registers[1] |= j << 15;
}

// Fractional Modulus
void max2871Set_M(uint32_t j)
{
	registers[1] &= ~(0xFFF << 3);
	registers[1] |= j << 3;
}

// Lock Detect Speed
void max2871Set_LDS(uint32_t j)
{
	registers[2] &= ~(0x1 << 31);
	registers[2] |= j << 31;
}

// Low Noise / Spur Mode
void max2871Set_SDN(uint32_t j)
{
	registers[2] &= ~(0x3 << 29);
	registers[2] |= j << 29;
}

// Mux Config
void max2871Set_MUX(uint32_t j)
{
    registers[2] &= ~(0x7 << 26);
    registers[5] &= ~(0x1 << 18);
    registers[2] |= (j & 0x7) << 26;
    registers[5] |= ((j & 0x8) >> 3) << 18;
}

// Ref Doubler Mode
void max2871Set_DBR(uint32_t j)
{
    registers[2] &= ~(0x1 << 25);
    registers[2] |= j << 25;
}

// Ref Div 2 Mode
void max2871Set_RDIV2(uint32_t j)
{
    registers[2] &= ~(0x1 << 24);
    registers[2] |= j << 24;
}

// Ref Divider Mode
void max2871Set_R(uint32_t j)
{
    registers[2] &= ~(0x3FF << 14);
    registers[2] |= j << 14;
}

// Double Buffer
void max2871Set_REG4DB(uint32_t j)
{
    registers[2] &= ~(0x1 << 13);
    registers[2] |= j << 13;
}

// Charge Pump Tristate Mode
void max2871Set_TRI(uint32_t j)
{
    registers[2] &= ~(0x1 << 4);
    registers[2] |= j << 4;
}

// Lock Detect Function
void max2871Set_LDF(uint32_t j)
{
    registers[2] &= ~(0x1 << 8);
    registers[2] |= j << 8;
}
// Lock Detect Precision
void max2871Set_LDP(uint32_t j)
{
    registers[2] &= ~(0x1 << 7);
    registers[2] |= j << 7;
}

// Phase Detector Polarity
void max2871Set_PDP(uint32_t j)
{
    registers[2] &= ~(0x1 << 6);
    registers[2] |= j << 6;
}

// Shutdown Mode
void max2871Set_SHDN(uint32_t j)
{
    registers[2] &= ~(0x1 << 5);
    registers[2] |= j << 5;
}

// Charge Pump
void max2871Set_CP(uint32_t j)
{
    registers[2] &= ~(0xF << 9);
    registers[2] |= j << 9;
}

// Counter Reset
void max2871Set_RST(uint32_t j)
{
    registers[2] &= ~(0x1 << 3);
    registers[2] |= j << 3;
}

// VCO Selection
void max2871Set_VCO(uint32_t j)
{
    registers[3] &= ~(0x3F << 26);
    registers[3] |= j << 26;
}

// VAS Shutdown
void max2871Set_VAS_SHDN(uint32_t j)
{
    registers[3] &= ~(0x1 << 25);
    registers[3] |= j << 25;
}

// VAS Temp, also sets VAS_DLY
void max2871Set_VAS_TEMP(uint32_t j)
{
    registers[3] &= ~(0x1 << 24);
    registers[3] |= 0 << 24;
    registers[5] &= ~(0x3 << 29);
    registers[5] |= j << 29;
    registers[5] |= j << 30;
}

// Cycle Slip Mode
void max2871Set_CSM(uint32_t j)
{
    registers[3] &= ~(0x1 << 18);
    registers[3] |= j << 18;
}

// Mute Delay Mode
void max2871Set_MUTEDEL(uint32_t j)
{
    registers[3] &= ~(0x1 << 17);
    registers[3] |= j << 17;
}

// Clock Divider Mode
void max2871Set_CDM(uint32_t j)
{
    registers[3] &= ~(0x3 << 15);
    registers[3] |= j << 15;
}

// Clock Divider Value
void max2871Set_CDIV(uint32_t j)
{
    registers[3] &= ~(0xFFF << 3);
    registers[3] |= j << 3;
}

// Shutdown VCO LDO
void max2871Set_SDLDO(uint32_t j)
{
    registers[4] &= ~(0x1 << 28);
    registers[4] |= j << 28;
}

// Shutdown VCO Divider
void max2871Set_SDDIV(uint32_t j)
{
    registers[4] &= ~(0x1 << 27);
    registers[4] |= j << 27;
}

// Shutdown Ref Input
void max2871Set_SDREF(uint32_t j)
{
    registers[4] &= ~(0x1 << 26);
    registers[4] |= j << 26;
}

// Band-Select MSBs
void max2871Set_BS(uint32_t j)
{
    registers[4] &= ~(0x3 << 24);
    registers[4] &= ~(0xFF << 12);
    registers[4] |= ((j & 0x300) >> 8) << 24;
    registers[4] |= (j & 0xFF) << 12;
}

// VCO Feedback Mode
void max2871Set_FB(uint32_t j)
{
    registers[4] &= ~(0x1 << 23);
    registers[4] |= j << 23;
}

// RFOUT_ Output Divider Mode
void max2871Set_DIVA(uint32_t j)
{
    registers[4] &= ~(0x7 << 20);
    registers[4] |= j << 20;
}

// Shutdown VCO VCO
void max2871Set_SDVCO(uint32_t j)
{
    registers[4] &= ~(0x1 << 11);
    registers[4] |= j << 11;
}

// RFOUT Mute Until Lock Detect
void max2871Set_MTLD(uint32_t j)
{
    registers[4] &= ~(0x1 << 10);
    registers[4] |= j << 10;
}

// RFOUTB Output Path Select
void max2871Set_BDIV(uint32_t j)
{
    registers[4] &= ~(0x1 << 9);
    registers[4] |= j << 9;
}

// RFOUTB Output Enable
void max2871Set_RFB_EN(uint32_t j)
{
    registers[4] &= ~(0x1 << 8);
    registers[4] |= j << 8;
}
// RFOUTB Output Power
void max2871Set_BPWR(uint32_t j)
{
    registers[4] &= ~(0x3 << 6);
    registers[4] |= j << 6;
}

// RFOUTA Output Enable
void max2871Set_RFA_EN(uint32_t j)
{
    registers[4] &= ~(0x1 << 5);
    registers[4] |= j << 5;
}
// RFOUTA Output Power
void max2871Set_APWR(uint32_t j)
{
    registers[4] &= ~(0x3 << 3);
    registers[4] |= j << 3;
}

// PLL Shutdown
void max2871Set_SDPLL(uint32_t j)
{
    registers[5] &= ~(0x1 << 25);
    registers[5] |= j << 25;
}

// F01
void max2871Set_F01(uint32_t j)
{
    registers[5] &= ~(0x1 << 24);
    registers[5] |= j << 24;
}

// Lock Detect Function
void max2871Set_LD(uint32_t j)
{
    registers[5] &= ~(0x3 << 22);
    registers[5] |= j << 22;
}

// Reserved Values
void max2871Set_Reserved(void)
{
	registers[3] &= ~(0x7F << 17);
	registers[4] &= ~(0x1 << 10);
	registers[5] &= ~(0x3F << 25);
}

// Don't think we need to use these
//// ADC Start
//void max2871Set_ADCS(uint32_t j)
//{
//    registers[5] &= ~(0x1 << 6);
//    registers[5] |= j << 6;
//}
//
//// ADC Mode
//void max2871Set_ADCM(uint32_t j)
//{
//    registers[5] &= ~(0x7 << 3);
//    registers[5] |= j << 3;
//}



















