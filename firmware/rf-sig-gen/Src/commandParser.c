#include "main.h"
#include "commandParser.h"
#include "usbd_cdc_if.h"
#include "dwt_stm32_delay.h"
#include <stdio.h>
#include <string.h>
#include "max2871.h"
#include "txChain.h"
#include "STP08CP05.h"

char txStr[128] = "";

void commandParser(struct MAX2871Struct *max2871Status, struct txStruct *txStatus)
{
	#define BUF_SIZE 128
	#define CMD_SIZE 32
	#define NUM_ARGS 6

	char usrMsg[BUF_SIZE];
	char command[CMD_SIZE] = "";
	char args[NUM_ARGS][16];
	uint8_t argNum = 0;
	// Get whatever the user has sent
	scanUSB((uint8_t *) usrMsg, BUF_SIZE);

	// Split on delim
	for (uint8_t i = 0; i < FIFO_SIZE; i++)
	{
		if ((usrMsg[i] == '(') || (usrMsg[i] == ')') || (usrMsg[i] == ','))
			usrMsg[i] = '\0';
	}

	// Determine the command word
	uint8_t i = 0;
	while (usrMsg[i] != '\0')
	{
		command[i] = usrMsg[i];
		i++;
	}

	// Find arguments
	while (i < FIFO_SIZE)
	{
		// If null term, (was delim) skip
		if (usrMsg[i] == '\0')
			i++;
		else
		{
			// Otherwise, copy arguments into their own strings
			uint8_t j = 0;
			while (usrMsg[i] != '\0')
			{
				args[argNum][j] = '\0';
				args[argNum][j++] = usrMsg[i];
				i++;
			}
			args[argNum][j] = '\0';
			argNum++;
		}

	}

	// Find command based on command word, and call function

	// Signal generator mode
	if (strncmp("sigGen", command, 6) == 0)
	{
		// If set to min power, max attenuation and MAX2871 output power
		if (strncmp("MIN", args[1], 3) == 0)
		{
			sigGen(atof(args[0]), 0, max2871Status, txStatus);
			setAttenuation(MAX_ATTENUATION, txStatus);
			max2871SetPower(-4, max2871Status);
		}
		else
		{
			sigGen(atof(args[0]), atof(args[1]), max2871Status, txStatus);
		}
		
		sprintf((char *)txStr, "> Signal Generator: Frequency = %0.3f MHz, Power = %0.2f dBm\n", max2871Status->frequency, txStatus->measOutputPower);
		printUSB(txStr);
	}

	// Sweep frequencies
	else if (strncmp("sweep", command, 5) == 0)
	{
		sprintf((char *)txStr, "> Sweep: Start = %0.2f MHz, fFinish = %0.2f dBm Power = %0.2f dBm\n", atof(args[0]), atof(args[1]), atof(args[2]));
		printUSB(txStr);

		while (RX_FIFO.dataReady == 0)
		{
			sweep(atof(args[0]), atof(args[1]), atof(args[2]), atof(args[3]), atof(args[4]), max2871Status, txStatus);
		}
	}

	else if (strncmp("enableRF", command, 8) == 0)
	{
		max2871RFEnable(max2871Status);
		enablePA(txStatus);
		printUSB("> RF Enabled \r\n");

		readAD8319(txStatus);
		sprintf((char *)txStr, "? %0.3f %0.2f \n", max2871Status->frequency, txStatus->measOutputPower);
		printUSB(txStr);
	}

	else if (strncmp("disableRF", command, 9) == 0)
	{
		max2871RFDisable(max2871Status);
		disablePA(txStatus);
		printUSB("> RF Disabled \r\n");

		readAD8319(txStatus);
		sprintf((char *)txStr, "? %0.3f %0.2f \n", max2871Status->frequency, -99.99);
		printUSB(txStr);
	}

	else if (strncmp("status", command, 6) == 0)
	{
		if (strncmp("v", args[0], 1) == 0)
		{
			args[0][0] = (int32_t) "";
			max2871PrintStatus(VERBOSE,max2871Status);
			txChainPrintStatus(VERBOSE,txStatus);
		}
		else
		{
			max2871PrintStatus(nVERBOSE,max2871Status);
			txChainPrintStatus(nVERBOSE,txStatus);
		}
	}
	
	else if (strncmp("WHOAMI", command, 5) == 0)
	{
		printUSB("> Josh's Signal Generator!\r\n");
	}

	else if (strncmp("led", command, 3) == 0)
	{
		stpSpiTx((uint8_t) atoi(args[0]));
	}

	else if (strncmp("rainbow", command, 7) == 0)
	{
		rainbow();
	}

	else if (strncmp("kitt", command, 4) == 0)
	{
		kitt();
	}

	else if (strncmp("binary", command, 6) == 0)
	{
		binary();
	}
	
	// USE BELOW AT YOUR OWN RISK
	else if (strncmp("setMaxPower", command, 11) == 0)
	{
		max2871SetPower(atoi(args[0]), max2871Status);
		int8_t powerArray[4] = {-4, -1, 2, 5};
		sprintf((char *)txStr, "> Power set to: %d dBm\n", powerArray[max2871Status->rfPower]);
		printUSB(txStr);
	}

	else if (strncmp("setAttenuation", command, 14) == 0)
	{
		setAttenuation(atof(args[0]), txStatus);
		sprintf((char *)txStr, "> Attenuation set to: %0.2f dB\n", txStatus->attenuation);
		printUSB(txStr);
	}

	else if (strncmp("enableLO", command, 8) == 0)
	{
		max2871RFEnable(max2871Status);
		printUSB("> LO Enabled \r\n");
	}

	else if (strncmp("disableLO", command, 8) == 0)
	{
		max2871RFDisable(max2871Status);
		printUSB("> LO Disabled \r\n");
	}

	else if (strncmp("enablePA", command, 8) == 0)
	{
		enablePA(txStatus);
		printUSB("> PA Enabled \r\n");
	}

	else if (strncmp("disablePA", command, 8) == 0)
	{
		disablePA(txStatus);
		printUSB("> PA Disabled \r\n");
	}

	else if (strncmp("adc", command, 3) == 0)
	{
		readAD8319(txStatus);

		sprintf((char *)txStr, "> Measured Voltage= %0.2f V\n", readAD8319(txStatus));
		printUSB(txStr);

		sprintf((char *)txStr, "> Output Power at SMA = %0.2f dBm\n", txStatus->measOutputPower);
		printUSB(txStr);
	}

	else if (strncmp("help", command, 4) == 0)
	{
		printUSB((char *)"> --  Available Commands  --\r\n");
		printUSB((char *)"> sigGen(frequency, power)\r\n");
		printUSB((char *)"> sweep(startFreq, stopFreq, numSteps, power, time)\r\n");
		printUSB((char *)"> enableRF\r\n");
		printUSB((char *)"> disableRF\r\n");
		printUSB((char *)"> status(verbose)\r\n");
		printUSB((char *)"> WHOAMI\r\n");
		printUSB((char *)"> --- Use the below at your own risk ---\r\n");
		printUSB((char *)"> setMaxPower(power(dBm))\r\n");
		printUSB((char *)"> setAttenuation(atten(dB))\r\n");
		printUSB((char *)"> enableLO\r\n");
		printUSB((char *)"> disableLO\r\n");
		printUSB((char *)"> enablePA\r\n");
		printUSB((char *)"> disablePA\r\n");
	}

	else if (strncmp("\r\n", command, 2) == 0)
	{
		printUSB("> Break\r\n");
	}
	else
	{
		printUSB("> Not found, try again\r\n");
		sprintf((char *)txStr, "> %s\n", command);
		printUSB(txStr);

	}

}
