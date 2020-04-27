#ifndef MAX2871_REGISTERS_H
#define MAX2871_REGISTERS_H
#include <stdint.h>

void max2871RegsInit(void);
uint32_t max2871GetRegister(uint8_t r);

void max2871Set_INT(uint32_t j);
void max2871Set_N(uint32_t j);
void max2871Set_FRAC(uint32_t j);
void max2871Set_CPOC(uint32_t j);
void max2871Set_CPL(uint32_t j);
void max2871Set_CPT(uint32_t j);
void max2871Set_P(uint32_t j);
void max2871Set_M(uint32_t j);
void max2871Set_LDS(uint32_t j);
void max2871Set_SDN(uint32_t j);
void max2871Set_MUX(uint32_t j);
void max2871Set_DBR(uint32_t j);
void max2871Set_RDIV2(uint32_t j);
void max2871Set_R(uint32_t j);
void max2871Set_REG4DB(uint32_t j);
void max2871Set_CP(uint32_t j);
void max2871Set_LDF(uint32_t j);
void max2871Set_LDP(uint32_t j);
void max2871Set_PDP(uint32_t j);
void max2871Set_SHDN(uint32_t j);
void max2871Set_TRI(uint32_t j);
void max2871Set_RST(uint32_t j);
void max2871Set_VCO(uint32_t j);
void max2871Set_VAS_SHDN(uint32_t j);
void max2871Set_VAS_TEMP(uint32_t j);
void max2871Set_CSM(uint32_t j);
void max2871Set_MUTEDEL(uint32_t j);
void max2871Set_CDM(uint32_t j);
void max2871Set_CDIV(uint32_t j);
void max2871Set_SDLDO(uint32_t j);
void max2871Set_SDDIV(uint32_t j);
void max2871Set_SDREF(uint32_t j);
void max2871Set_BS(uint32_t j);
void max2871Set_FB(uint32_t j);
void max2871Set_DIVA(uint32_t j);
void max2871Set_SDVCO(uint32_t j);
void max2871Set_MTLD(uint32_t j);
void max2871Set_BDIV(uint32_t j);
void max2871Set_RFB_EN(uint32_t j);
void max2871Set_BPWR(uint32_t j);
void max2871Set_RFA_EN(uint32_t j);
void max2871Set_APWR(uint32_t j);
void max2871Set_SDPLL(uint32_t j);
void max2871Set_F01(uint32_t j);
void max2871Set_LD(uint32_t j);
void max2871Set_Reserved(void);
void max2871Set_ADCS(uint32_t j);
void max2871Set_ADCM(uint32_t j);

#endif 
