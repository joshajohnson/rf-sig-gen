#include "main.h"
#include "max2871.h"
#include "max2871_registers.h"
#include "dwt_stm32_delay.h"
#include "usbd_cdc_if.h"
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#define MOD 4095
#define STR1_SIZE 128
char str1[STR1_SIZE] = "";

struct MAX2871Struct max2871Status;

// Setup of the MAX2871 PLL, 50MHz, output off
void max2871Setup(struct MAX2871Struct *max2871Status)
{
	// Set to initial known state
	max2871ChipEnable(max2871Status);
	max2871RFDisable(max2871Status);
	HAL_GPIO_WritePin(MAX_CLK_GPIO_Port, MAX_CLK_Pin, 0);
	HAL_GPIO_WritePin(MAX_DAT_GPIO_Port, MAX_DAT_Pin, 0);
	HAL_GPIO_WritePin(MAX_MUX_GPIO_Port, MAX_MUX_Pin, 0);
	HAL_GPIO_WritePin(MAX_LE_GPIO_Port, MAX_LE_Pin, 1);

	max2871RegsInit();

	// Initial writing of registers, with wait time
	uint32_t txReg;
	for (int j = 1; j >= 0; j--)
	{
		for (int i = 5; i >= 0; i--)
		{
			txReg = max2871GetRegister(i);
			max2871SpiWrite(txReg);
			if (i == 5) HAL_Delay(20);
		}
		HAL_Delay(20);
	}

	// Set initial register values
	max2871Set_INT(0); 		// Frac N
	max2871Set_N(83);		// Init to 50Mhz
	max2871Set_FRAC(1365);
	max2871Set_CPOC(0);
	max2871Set_CPL(0);
	max2871Set_CPT(0);
	max2871Set_P(1);
	max2871Set_M(4095);
	max2871Set_LDS(1);
	max2871Set_SDN(0);
	max2871Set_MUX(0xC); 	// Reg 6 Readback 0xC
	max2871Set_DBR(1);
	max2871Set_RDIV2(0);
	max2871Set_R(1); 		// 38.4MHz f_PFD
	max2871Set_REG4DB(0);
	max2871Set_CP(15);
	max2871Set_LDF(0);
	max2871Set_LDP(0);
	max2871Set_PDP(1);
	max2871Set_SHDN(0);
	max2871Set_TRI(0);
	max2871Set_RST(0);
	max2871Set_VCO(0);
	max2871Set_VAS_SHDN(0);
	max2871Set_VAS_TEMP(1);
	max2871Set_CSM(0);
	max2871Set_MUTEDEL(1);
	max2871Set_CDM(0);
	max2871Set_CDIV(38);
	max2871Set_SDLDO(0);
	max2871Set_SDDIV(0);
	max2871Set_SDREF(0);
	max2871Set_BS(768);		//BS = fPFD / 50KHz
	max2871Set_FB(1);
	max2871Set_DIVA(6);
	max2871Set_SDVCO(0);
	max2871Set_MTLD(1);
	max2871Set_BDIV(0);
	max2871Set_RFB_EN(0);
	max2871Set_BPWR(0);
	max2871Set_RFA_EN(0);	// Begin with power off
	max2871Set_APWR(3);
	max2871Set_SDPLL(0);
	max2871Set_F01(0);
	max2871Set_LD(1);
	max2871Set_Reserved();

	// Update info in struct
	max2871Status->RFA_EN = 0;
	max2871Status->rfPower = 3;
	max2871Status->frequency = 50;

	// Send updated registers over SPI
	max2871WriteRegisters();
	HAL_Delay(10);

	// Check if the PLL has locked
	max2871CheckLD(max2871Status);
}

// Writes given register to MAX2871
void max2871SpiWrite(uint32_t r)
{
	// Ensure LE high
	HAL_GPIO_WritePin(MAX_LE_GPIO_Port, MAX_LE_Pin, 1);

	// Start by bringing LE low
	HAL_GPIO_WritePin(MAX_LE_GPIO_Port, MAX_LE_Pin, 0);

	// Transmit all the bits!
	for (int8_t bit = 32; bit > 0; bit--)
	{
		HAL_GPIO_WritePin(MAX_DAT_GPIO_Port, MAX_DAT_Pin, ((r) & (1 << (bit - 1))) ? 1 : 0);
		HAL_GPIO_WritePin(MAX_CLK_GPIO_Port, MAX_CLK_Pin, 1);
		HAL_GPIO_WritePin(MAX_CLK_GPIO_Port, MAX_CLK_Pin, 0);
	}

	// Ensure DAT is low afterwards
	HAL_GPIO_WritePin(MAX_DAT_GPIO_Port, MAX_DAT_Pin, 0);
	// Once Transfer complete, pull LE high
	HAL_GPIO_WritePin(MAX_LE_GPIO_Port, MAX_LE_Pin, 1);
}

// Readback register 6 from MAX2871. Requires MUX to be set in readback mode (0xC)
uint32_t max2871SpiRead(void)
{
	uint32_t dataReturn = 0;

	max2871SpiWrite(0x06);

	// Ensure LE High
	HAL_GPIO_WritePin(MAX_LE_GPIO_Port, MAX_LE_Pin, 1);

	// Receive all the bits!
	for (int8_t bit = 32; bit > 0; bit--)
	{
		HAL_GPIO_WritePin(MAX_CLK_GPIO_Port, MAX_CLK_Pin, 1);
		dataReturn |= HAL_GPIO_ReadPin(MAX_MUX_GPIO_Port, MAX_MUX_Pin) << bit;
		HAL_GPIO_WritePin(MAX_CLK_GPIO_Port, MAX_CLK_Pin, 0);
	}

	return dataReturn;
}

// Writes registers 5 - 0 to MAX2871
void max2871WriteRegisters(void)
{
	for (int i = 5; i >= 0; i--)
	{
		max2871SpiWrite(max2871GetRegister(i));
	}
}

// Calculates values for given frequency and INT_N / FRAC_N mode
void max2871SetFrequency(float mhz, uint8_t intN, struct MAX2871Struct *max2871Status)
{
	// Determine DIVA
	int8_t  diva = -1;
	if ((mhz >= 23.5) &&  (mhz < 46.875))
		diva = 7;
	else if (mhz < 93.75)
		diva = 6;
	else if (mhz < 187.5)
		diva = 5;
	else if (mhz < 375)
		diva = 4;
	else if (mhz < 750)
		diva = 3;
	else if (mhz < 1500)
		diva = 2;
	else if (mhz < 3000)
		diva = 1;
	else if (mhz <= 6000)
		diva = 0;
	else
	{
		printUSB((char *) "+ Bad input frequency to max2871SetFrequency\r\n");
		return;
	}

	// Calculate fOUT
	float fComp = 38.4;
	float fVCO = mhz * (2 << (diva - 1));
	if (diva == 0) fVCO = mhz; // Gets around 2^0 error
	float n = fVCO / fComp;
	uint32_t N = (uint16_t) n;

	float F = round((n - N) * MOD);

	// Determine fVCO
	if (intN == 1)
		fVCO = N * fComp;
	else if (!intN)
		fVCO = (N + (F/MOD)) * fComp;

	float fOUT = fVCO / pow(2,diva);
	if (diva == 0) fOUT = fVCO;

	// Set registers for Int-N configuration
	if (intN == 1)
	{
		max2871Set_INT(1);
		max2871Set_N(N);
		max2871Set_FRAC(F);
		max2871Set_CPL(0);
		max2871Set_M(MOD);
		max2871Set_LDF(1);
		max2871Set_DIVA(diva);
		max2871Set_F01(0);
	}
	// Set registers for Frac-N configuration
	else if (!intN)
	{
		max2871Set_INT(0);
		max2871Set_N(N);
		max2871Set_FRAC(F);
		max2871Set_CPL(1);
		max2871Set_M(MOD);
		max2871Set_LDF(0);
		max2871Set_DIVA(diva);
		max2871Set_F01(1);
	}
	max2871Status->intN_nFracN = intN;
	max2871Status->frequency = fOUT;

	// Update MAX registers with new frequency info
	max2871WriteRegisters();
}

void max2871ChipEnable(struct MAX2871Struct *max2871Status)
{
	HAL_GPIO_WritePin(MAX_CE_GPIO_Port, MAX_CE_Pin, 1);
	max2871Status->CHIP_EN = 1;
}

void max2871ChipDisable(struct MAX2871Struct *max2871Status)
{
	HAL_GPIO_WritePin(MAX_CE_GPIO_Port, MAX_CE_Pin, 0);
	max2871Status->CHIP_EN = 0;
}

void max2871RFEnable(struct MAX2871Struct *max2871Status)
{
	max2871Set_RFA_EN(1);
	HAL_GPIO_WritePin(MAX_RFOUT_EN_GPIO_Port, MAX_RFOUT_EN_Pin, 1);
	max2871ChipEnable(max2871Status);
	max2871Status->RFA_EN = 1;
	max2871Status->RF_CHIP_EN = 1;
	max2871WriteRegisters();
}

void max2871RFDisable(struct MAX2871Struct *max2871Status)
{
	max2871Set_RFA_EN(0);
	HAL_GPIO_WritePin(MAX_RFOUT_EN_GPIO_Port, MAX_RFOUT_EN_Pin, 0);
	max2871Status->RFA_EN = 0;
	max2871Status->RF_CHIP_EN = 0;
	max2871WriteRegisters();
}

void max2871SetPower(int8_t dbm, struct MAX2871Struct *max2871Status)
{
	switch (dbm)
	{
		case -4:
			max2871Status->rfPower = 0;
			break;

		case -1:
			max2871Status->rfPower = 1;
			break;

		case 2:
			max2871Status->rfPower = 2;
			break;

		case 5:
			max2871Status->rfPower = 3;
			break;
		default:
			printUSB((char *) "> Bad input power to max2871SetPower");
	}

	max2871Set_APWR(max2871Status->rfPower);
	max2871WriteRegisters();
}

int8_t max2871CheckLD(struct MAX2871Struct *max2871Status)
{
	max2871Status->ldState = HAL_GPIO_ReadPin(MAX_LD_GPIO_Port, MAX_LD_Pin);

	if (max2871Status->ldState)
		return 1;
	else
		return -1;
}

void max2871PrintRegisters(void)
{
	uint32_t txReg;

	for (int8_t i = 0; i <= 5; i++)
	{
		txReg = max2871GetRegister(i);
		sprintf(str1, "> Register %d = 0x%x\n", i, (unsigned int) txReg);
		printUSB(str1);
		HAL_Delay(10);

	}

	txReg = max2871SpiRead();
	sprintf(str1, "> Register 6 = 0x%x\n", (unsigned int) txReg);
	printUSB(str1);
}

void max2871PrintStatus(uint8_t verbose, struct MAX2871Struct *max2871Status)
{
	int8_t powerArray[4] = {-4, -1, 2, 5};

	printUSB("> ----  MAX2871  ----\n");

	sprintf(str1, "> Chip Enable = %d\n", max2871Status->CHIP_EN);
	printUSB(str1);

	max2871CheckLD(max2871Status);
	sprintf(str1, "> LD Status = %d\n", max2871Status->ldState);
	printUSB(str1);

	sprintf(str1, "> Set Frequency = %0.2f MHz\n", max2871Status->frequency);
	printUSB(str1);

	sprintf(str1, "> Int-N / nFrac-N = %d\n", max2871Status->intN_nFracN);
	printUSB(str1);

	sprintf(str1, "> RFA Enable = %d\n", max2871Status->RFA_EN);
	printUSB(str1);

	sprintf(str1, "> RF Out Enable = %d\n", max2871Status->RF_CHIP_EN);
	printUSB(str1);

	sprintf(str1, "> RF Power = %d dBm\n", powerArray[max2871Status->rfPower]);
	printUSB(str1);

	if (verbose)
	{
		max2871PrintRegisters();
	}
}


