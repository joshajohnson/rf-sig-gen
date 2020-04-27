#ifndef MAX2871_H
#define MAX2871_H

typedef struct MAX2871Struct{
	uint8_t CHIP_EN;
	uint8_t	ldState;
	float 	frequency;
	uint8_t RFA_EN;
	uint8_t RF_CHIP_EN;
	uint8_t rfPower;
	uint8_t intN_nFracN;
}MAX2871Struct;

void max2871Setup(struct MAX2871Struct *max2871Status);
void max2871SpiWrite(uint32_t r);
uint32_t max2871SpiRead(void);
void max2871WriteRegisters(void);
void max2871SetFrequency(float mhz, uint8_t intN, struct MAX2871Struct *max2871Status);
void max2871ChipEnable(struct MAX2871Struct *max2871Status);
void max2871ChipDisable(struct MAX2871Struct *max2871Status);
void max2871RFEnable(struct MAX2871Struct *max2871Status);
void max2871RFDisable(struct MAX2871Struct *max2871Status);
void max2871SetPower(int8_t dbm, struct MAX2871Struct *max2871Status);
void max2871PrintRegisters(void);
int8_t max2871CheckLD(struct MAX2871Struct *max2871Status);
void max2871PrintStatus(uint8_t verbose, struct MAX2871Struct *max2871Status);

#endif
