#ifndef TXCHAIN_H_
#define TXCHAIN_H_

// ADC values
#define VREF 				3.3
#define NUM_STATES_12_BIT	4096

// Attenuator
#define MAX_ATTENUATION 	31.5
#define MIN_ATTENUATION 	0
#define STEP_ATTENUATION	0.5

extern struct MAX2871Struct max2871Status;

typedef struct txStruct{
	float measOutputPower;
	float setOutputPower;
	float attenuation;
	uint8_t paPwdn;
}txStruct;

void sweep(float lowerFreq, float higherFreq, float numSteps, float power, float sweepTime, struct MAX2871Struct *max2871Status, struct txStruct *txStatus);
void setFrequency(float frequency, struct MAX2871Struct *max2871Status, struct txStruct *txStatus);
void sigGen(float frequency, float power, struct MAX2871Struct *max2871Status, struct txStruct *txStatus);
void setOutputPower(float setPower, struct MAX2871Struct *max2871Status, struct txStruct *txStatus);
void txChainInit(struct MAX2871Struct *max2871Status, struct txStruct *txStatus);
void setAttenuation(float atten, struct txStruct *txStatus);
float readAD8319(struct txStruct *txStatus);
void enablePA(struct txStruct *txStatus);
void disablePA(struct txStruct *txStatus);
void txChainPrintStatus(uint8_t verbose, struct txStruct *txStatus);

#endif
