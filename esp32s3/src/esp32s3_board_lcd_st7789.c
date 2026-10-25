/****************************************************************************
 * boards/esp32s3/src/esp32s3_board_lcd_st7789.c
 *
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance with the
 * License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
 * License for the specific language governing permissions and limitations
 * under the License.
 *
 ****************************************************************************/

/****************************************************************************
 * Included Files
 ****************************************************************************/

#include <nuttx/config.h>

#include <errno.h>
#include <stdbool.h>

#include <nuttx/arch.h>
#include <nuttx/board.h>
#include <nuttx/debug.h>
#include <nuttx/spi/spi.h>
#include <nuttx/lcd/lcd.h>
#include <nuttx/lcd/st7789.h>

#include <arch/board/board.h>

#include "espressif/esp_gpio.h"
#include "esp32s3_spi.h"

#include "esp32s3.h"

/****************************************************************************
 * Private Data
 ****************************************************************************/

static struct spi_dev_s *g_spidev;
static struct lcd_dev_s *g_lcd;

/****************************************************************************
 * Public Functions
 ****************************************************************************/

/****************************************************************************
 * Name: board_lcd_initialize
 *
 * Description:
 *   Initialize the ST7789 LCD attached to SPI2. The DC/RST/backlight pins
 *   are plain GPIOs, configured via the BOARD_ESP32S3_LCD_ST7789_* options.
 *
 * Returned Value:
 *   Zero (OK) on success; a negated errno value on failure.
 *
 ****************************************************************************/

int board_lcd_initialize(void) {
  /* Initialize the non-SPI control GPIOs */

  esp_configgpio(CONFIG_BOARD_ESP32S3_LCD_ST7789_DC_PIN, OUTPUT);
  esp_configgpio(CONFIG_BOARD_ESP32S3_LCD_ST7789_RST_PIN, OUTPUT);
  esp_configgpio(CONFIG_BOARD_ESP32S3_LCD_ST7789_BL_PIN, OUTPUT);

  /* Reset the panel */

  esp_gpiowrite(CONFIG_BOARD_ESP32S3_LCD_ST7789_RST_PIN, false);
  nxsched_usleep(10 * 1000);
  esp_gpiowrite(CONFIG_BOARD_ESP32S3_LCD_ST7789_RST_PIN, true);
  nxsched_usleep(120 * 1000);

  /* Turn on the backlight */

  esp_gpiowrite(CONFIG_BOARD_ESP32S3_LCD_ST7789_BL_PIN, true);

  /* Bind the ST7789 to SPI2 */

  g_spidev = esp32s3_spibus_initialize(DISPLAY_SPI);
  if (!g_spidev) {
    lcderr("ERROR: Failed to initialize SPI port %d\n", DISPLAY_SPI);
    return -ENODEV;
  }

  g_lcd = st7789_lcdinitialize(g_spidev);
  if (!g_lcd) {
    lcderr("ERROR: st7789_lcdinitialize() failed\n");
    return -ENODEV;
  }

  return OK;
}

/****************************************************************************
 * Name: board_lcd_getdev
 *
 * Description:
 *   Return a reference to the LCD object for the specified LCD.
 *
 * Input Parameters:
 *   devno - LCD device number
 *
 * Returned Value:
 *   LCD device pointer if success or NULL if failed.
 *
 ****************************************************************************/

struct lcd_dev_s *board_lcd_getdev(int devno) {
  if (!g_lcd) {
    lcderr("ERROR: Failed to bind SPI port %d to LCD %d\n", DISPLAY_SPI,
           devno);
    return NULL;
  }

  lcdinfo("SPI port %d bound to LCD %d\n", DISPLAY_SPI, devno);
  return g_lcd;
}

/****************************************************************************
 * Name: board_lcd_uninitialize
 *
 * Description:
 *   Uninitialize the LCD support.
 *
 ****************************************************************************/

void board_lcd_uninitialize(void) {
  if (g_lcd) {
    g_lcd->setpower(g_lcd, 0);
  }
}
