#include "STP08CP05.h"

// Map frequency to how many leds are enabled
uint8_t freqToLed (float frequency)
{
    uint8_t leds;

    if (frequency < 23.50)
        leds = 0;
    else if (frequency < 36.875)
        leds = 0b00000001;
    else if (frequency < 73.75)
        leds = 0b00000011;
    else if (frequency < 187.5)
        leds = 0b00000111;
    else if (frequency < 375)
        leds = 0b00001111;
    else if (frequency < 750)
        leds = 0b00011111;
    else if (frequency < 1500)
        leds = 0b00111111;
    else if (frequency < 3000)
        leds = 0b01111111;
    else if (frequency <= 6000)
        leds = 0b11111111;

    return leds;
}

void rainbow()
{
    uint8_t display = 0;
    while ((RX_FIFO.dataReady == 0))
    {
        for (uint8_t i = 0; i < 8; i++)
        {
            stpSpiTx(display |= (1 << i));
            HAL_Delay(100);
            if (RX_FIFO.dataReady == 1) break;
        }

        for (uint8_t i = 0; i < 8; i++)
        {
            stpSpiTx(display &= ~(1 << i));
            HAL_Delay(100);
            if (RX_FIFO.dataReady == 1) break;
        }
    }
}

void kitt()
{
    uint8_t display = 0;
    while ((RX_FIFO.dataReady == 0))
    {
        for (uint8_t i = 0; i < 8; i++)
        {
            stpSpiTx(display = (1 << i));
            HAL_Delay(100);
            if (RX_FIFO.dataReady == 1) break;
        }
        for (uint8_t i = 6; i > 0; i--)
        {
            stpSpiTx(display = (1 << i));
            HAL_Delay(100);
            if (RX_FIFO.dataReady == 1) break;
        }
    }
}

void binary()
{
    while ((RX_FIFO.dataReady == 0))
    {
        for (uint8_t i = 0; i <= 255; i++)
        {
            stpSpiTx(i);
            HAL_Delay(50);
            if (RX_FIFO.dataReady == 1) break;
        }
    }
}

// Shift in LED values to driver
void stpSpiTx(uint8_t leds)
{
	// Transfer the bits
	for (uint8_t i = 0; i < 8; i++)
	{
		HAL_GPIO_WritePin(LED_SDI_GPIO_Port, LED_SDI_Pin, leds & (1 << i));
		HAL_GPIO_WritePin(LED_CLK_GPIO_Port, LED_CLK_Pin, 1);
		HAL_GPIO_WritePin(LED_CLK_GPIO_Port, LED_CLK_Pin, 0);
	}

    // Latch Enable
    HAL_GPIO_WritePin(LED_LE_GPIO_Port, LED_LE_Pin, 1);
    HAL_GPIO_WritePin(LED_LE_GPIO_Port, LED_LE_Pin, 0);

    // Clock Again
    HAL_GPIO_WritePin(LED_CLK_GPIO_Port, LED_CLK_Pin, 1);
    HAL_GPIO_WritePin(LED_CLK_GPIO_Port, LED_CLK_Pin, 0);
	
}