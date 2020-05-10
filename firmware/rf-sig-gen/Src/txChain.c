#include "main.h"
#include "txChain.h"
#include "max2871.h"
#include "dwt_stm32_delay.h"
#include "usbd_cdc_if.h"
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include "STP08CP05.h"

extern ADC_HandleTypeDef hadc1;

struct txStruct txStatus;

char buf[128] = "";

// Sets up output for given frequency and power level
void sigGen(float frequency, float power, struct MAX2871Struct *max2871Status, struct txStruct *txStatus)
{
	max2871SetFrequency(frequency,FRAC_N,max2871Status);
	stpSpiTx(freqToLed(frequency));

	while (!max2871CheckLD(max2871Status));
	// Don't go any further until PLL has lock

	setOutputPower(power, max2871Status, txStatus);

	sprintf((char *)buf, "? %0.3f %0.2f \n", max2871Status->frequency, txStatus->measOutputPower);
	printUSB(buf);
}

// Sweeps through frequencies
void sweep(float lowerFreq, float higherFreq, float numSteps, float power, float sweepTime, struct MAX2871Struct *max2871Status, struct txStruct *txStatus)
{
	float stepSize = ((higherFreq - lowerFreq) / numSteps);
	int32_t delay = (sweepTime * 1000000 / numSteps) - 10; 	// Delay is in uS
	if (delay < 0) delay = 0;

	float currentFrequency = lowerFreq;

	while ((currentFrequency <= higherFreq + 0.1) && (RX_FIFO.dataReady == 0))
	{
		sigGen(currentFrequency, power, max2871Status, txStatus);
		DWT_Delay_us(delay);
		currentFrequency += stepSize;

	}
}

void txChainInit(struct MAX2871Struct *max2871Status, struct txStruct *txStatus)
{
	// init with lowest output power
	max2871RFDisable(max2871Status);
	disablePA(txStatus);
	setAttenuation(MAX_ATTENUATION,txStatus);
	max2871Setup(max2871Status);
}

// Sets attenuation for a SKY12347 attenuator
void setAttenuation(float atten, struct txStruct *txStatus)
{
	// Convert given attenuation value to the 8 bits which SKY12347 wants
	txStatus->attenuation = atten;
	uint8_t bitSequence = (atten * 4);
	bitSequence = ~bitSequence;

	// Init attenuator LE high
	HAL_GPIO_WritePin(ATTEN_LE_GPIO_Port,ATTEN_LE_Pin,1);
	// Begin by bringing LE low
	HAL_GPIO_WritePin(ATTEN_LE_GPIO_Port, ATTEN_LE_Pin, 0);

	// Transfer the bits
	for (uint8_t i = 6; i > 0 ; i--)
	{
		HAL_GPIO_WritePin(ATTEN_SDO_GPIO_Port, ATTEN_SDO_Pin, bitSequence & (1 << i));
		HAL_GPIO_WritePin(ATTEN_CLK_GPIO_Port, ATTEN_CLK_Pin, 1);
		HAL_GPIO_WritePin(ATTEN_CLK_GPIO_Port, ATTEN_CLK_Pin, 0);
	}
	HAL_GPIO_WritePin(ATTEN_SDO_GPIO_Port, ATTEN_SDO_Pin, 0);
	// Shift data in by bringing LE high
	HAL_GPIO_WritePin(ATTEN_LE_GPIO_Port, ATTEN_LE_Pin, 1);
}

// Very simple control of attenuator to set desired output power.
// Changes attenuation until AD8319 reads correct value or runs out of attenuation.
void setOutputPower(float setPower, struct MAX2871Struct *max2871Status, struct txStruct *txStatus)
{
	// Change MAX2871 output power to get full range, along with attenuator to prevent spikes in output power, if moving above / below 0 dBm
	if (setPower >= 0 && txStatus->setOutputPower < 0)
	{
		max2871SetPower(5, max2871Status);
		setAttenuation(txStatus->attenuation + 9, txStatus);
	}
	else if (setPower < 0 && txStatus->setOutputPower > 0)
	{
		max2871SetPower(-4, max2871Status);
		setAttenuation(txStatus->attenuation - 9, txStatus);
	}

	txStatus->setOutputPower = setPower;
	readAD8319(txStatus);

	// If power too high
	if (txStatus->measOutputPower > (txStatus->setOutputPower + STEP_ATTENUATION / 2))
	{
		// While power too high
		while (txStatus->measOutputPower > (txStatus->setOutputPower + STEP_ATTENUATION / 2))
		{
			if (txStatus->attenuation < MAX_ATTENUATION)
			{
				setAttenuation(txStatus->attenuation += STEP_ATTENUATION, txStatus);
				readAD8319(txStatus);
				printUSB((char *) "+ Adjusting Attenuation!\r\n");
			}
			else
			{
				printUSB((char *) "+ Ran out of attenuation!\r\n");
				break;
			}
		}
	}
	// If power too low
	if (txStatus->measOutputPower < (txStatus->setOutputPower - STEP_ATTENUATION / 2))
	{
		// While power too low
		while (txStatus->measOutputPower < (txStatus->setOutputPower - STEP_ATTENUATION / 2))
		{
			if (txStatus->attenuation > MIN_ATTENUATION)
			{
				setAttenuation(txStatus->attenuation -= STEP_ATTENUATION, txStatus);
				readAD8319(txStatus);
				printUSB((char *) "+ Adjusting Attenuation!\r\n");
			}
			else
			{
				printUSB((char *) "+ Ran out of attenuation!\r\n");
				break;
			}
		}
	}

}

// Sets power value in the txStatus struct
// Returns voltage measured from the AD8319
// TODO: Calibrate voltage to power conversion, requires test gear!
float readAD8319(struct txStruct *txStatus)
{
	float voltage, power;
	uint32_t adcValue = 0;
	uint32_t ch;
	uint16_t retVal;


	// Get a 8 sample average of the ADC data
	for (uint8_t i = 8; i > 0; i--)
	{
		while(HAL_ADC_PollForConversion(&hadc1, 1000) != HAL_OK)
		{
			// Wait
		}

		if(HAL_ADC_PollForConversion(&hadc1, 1000) == HAL_OK)
		{
			adcValue += HAL_ADC_GetValue(&hadc1);
		}
		DWT_Delay_us(1);
	}

	adcValue /= 8; // Get average value

	voltage = (VREF * adcValue) / NUM_STATES_12_BIT;	// Convert to voltage

	power = -44.4 * voltage + 33; 						// Voltage to power at SMA

	txStatus->measOutputPower = power;

	return voltage;
}

void enablePA(struct txStruct *txStatus)
{
	HAL_GPIO_WritePin(PA_PWDN_GPIO_Port,PA_PWDN_Pin,0);
	txStatus->paPwdn = 0;
}

void disablePA(struct txStruct *txStatus)
{
	HAL_GPIO_WritePin(PA_PWDN_GPIO_Port,PA_PWDN_Pin,1);
	txStatus->paPwdn = 1;
}

void txChainPrintStatus(uint8_t verbose, struct txStruct *txStatus)
{

	char str1[128] = "";

	printUSB((char *)"> ----  TX Chain  ----\n");

	sprintf((char *)str1, "> Attenuation = %0.1f dB\n", txStatus->attenuation);
	printUSB(str1);

	sprintf((char *)str1, "> PA Enabled = %d\n", !txStatus->paPwdn);
	printUSB(str1);

	sprintf((char *)str1, "> Set Output Power= %0.2f dBm\n", txStatus->setOutputPower);
	printUSB(str1);

	readAD8319(txStatus);

	sprintf((char *)str1, "> Measured Output Power = %0.2f dBm\n", txStatus->measOutputPower);
	printUSB(str1);

	if (verbose)
	{
		readAD8319(txStatus);
		sprintf((char *)str1, "> Measured Voltage= %0.2f V\n", readAD8319(txStatus));
		printUSB(str1);
	}
}
