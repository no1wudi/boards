/****************************************************************************
 * boards/xtensa/esp32s3/esp32s3-eye/src/esp32s3_bringup.c
 *
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.  The
 * ASF licenses this file to you under the Apache License, Version 2.0 (the
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

#include <nuttx/spi/spi.h>
#include <nuttx/lcd/st7789.h>

#include "esp32s3_gpio.h"
#include "esp32s3_spi.h"

/****************************************************************************
 * Public Functions
 ****************************************************************************/

struct lcd_dev_s *board_graphics_setup(unsigned int devno)
{
  struct spi_dev_s *spi;

  /* Configure the DC/CS/RST/BL pins as GPIOs */

  esp32s3_configgpio(CONFIG_BOARD_ESP32S3_LCD_ST7789_DC_PIN, OUTPUT);
  esp32s3_configgpio(CONFIG_BOARD_ESP32S3_LCD_ST7789_RST_PIN, OUTPUT);
  esp32s3_configgpio(CONFIG_BOARD_ESP32S3_LCD_ST7789_BL_PIN, OUTPUT);

  /* Set the initial state of the DC/CS/RST/BL pins */

  esp32s3_gpiowrite(CONFIG_BOARD_ESP32S3_LCD_ST7789_DC_PIN, 1);
  esp32s3_gpiowrite(CONFIG_BOARD_ESP32S3_LCD_ST7789_RST_PIN, 1);
  esp32s3_gpiowrite(CONFIG_BOARD_ESP32S3_LCD_ST7789_BL_PIN, 1);

  /* Configure the SPI bus used by the ST7789 */

  spi = esp32s3_spibus_initialize(2);
  if (!spi)
    {
      return NULL;
    }

  return st7789_lcdinitialize(spi);
}

uint8_t esp32s3_spi2_status(struct spi_dev_s *dev, uint32_t devid)
{
  return 0;
}

int esp32s3_spi2_cmddata(struct spi_dev_s *dev, uint32_t devid, bool cmd)
{
  if (devid == SPIDEV_DISPLAY(0))
    {
      esp32s3_gpiowrite(CONFIG_BOARD_ESP32S3_LCD_ST7789_DC_PIN, !cmd);
      return OK;
    }

  return -ENODEV;
}
