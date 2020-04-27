/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2020 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f1xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */
#define  FIFO_SIZE 128  // must be 2^N
typedef struct FIFO
{
	uint32_t head;
	uint32_t tail;
	uint8_t data[FIFO_SIZE];
	uint8_t dataReady;
	uint8_t charArray[FIFO_SIZE];
} FIFO;

extern FIFO RX_FIFO;
/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */
#define FRAC_N 		0
#define INT_N		1

#define nVERBOSE 	0
#define VERBOSE 	1
/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */
#define  FIFO_INCR(x) (((x)+1)&((FIFO_SIZE)-1))
/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define MAX_LE_Pin GPIO_PIN_1
#define MAX_LE_GPIO_Port GPIOA
#define MAX_RFOUT_EN_Pin GPIO_PIN_2
#define MAX_RFOUT_EN_GPIO_Port GPIOA
#define MAX_LD_Pin GPIO_PIN_3
#define MAX_LD_GPIO_Port GPIOA
#define nLED_OE_Pin GPIO_PIN_5
#define nLED_OE_GPIO_Port GPIOA
#define ATTEN_LE_Pin GPIO_PIN_6
#define ATTEN_LE_GPIO_Port GPIOA
#define ATTEN_SDO_Pin GPIO_PIN_7
#define ATTEN_SDO_GPIO_Port GPIOA
#define ATTEN_CLK_Pin GPIO_PIN_0
#define ATTEN_CLK_GPIO_Port GPIOB
#define LED_SDI_Pin GPIO_PIN_10
#define LED_SDI_GPIO_Port GPIOB
#define LED_CLK_Pin GPIO_PIN_11
#define LED_CLK_GPIO_Port GPIOB
#define LED_LE_Pin GPIO_PIN_12
#define LED_LE_GPIO_Port GPIOB
#define nLED_RED_Pin GPIO_PIN_13
#define nLED_RED_GPIO_Port GPIOB
#define nLED_GRN_Pin GPIO_PIN_14
#define nLED_GRN_GPIO_Port GPIOB
#define nLED_BLU_Pin GPIO_PIN_15
#define nLED_BLU_GPIO_Port GPIOB
#define nLED_USR_Pin GPIO_PIN_8
#define nLED_USR_GPIO_Port GPIOA
#define SWDIO_Pin GPIO_PIN_13
#define SWDIO_GPIO_Port GPIOA
#define SWDCLK_Pin GPIO_PIN_14
#define SWDCLK_GPIO_Port GPIOA
#define USB_PU_Pin GPIO_PIN_15
#define USB_PU_GPIO_Port GPIOA
#define MAX_CE_Pin GPIO_PIN_3
#define MAX_CE_GPIO_Port GPIOB
#define MAX_DAT_Pin GPIO_PIN_4
#define MAX_DAT_GPIO_Port GPIOB
#define MAX_CLK_Pin GPIO_PIN_5
#define MAX_CLK_GPIO_Port GPIOB
#define LED_Pin GPIO_PIN_6
#define LED_GPIO_Port GPIOB
#define MAX_MUX_Pin GPIO_PIN_7
#define MAX_MUX_GPIO_Port GPIOB
#define ATTEN_SDI_Pin GPIO_PIN_8
#define ATTEN_SDI_GPIO_Port GPIOB
#define PA_PWDN_Pin GPIO_PIN_9
#define PA_PWDN_GPIO_Port GPIOB
/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
