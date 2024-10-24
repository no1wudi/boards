/****************************************************************************
 * boards/risc-v/esp32c3/esp32c3-generic/src/esp32c3_ssd1681.c
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
#include <nuttx/lcd/ssd1680.h>
#include <stdbool.h>

#include "espressif/esp_gpio.h"
#include "espressif/esp_spi.h"

/****************************************************************************
 * Private Fucntion Decalarations
 ****************************************************************************/

static bool set_vcc(bool on);
static bool set_rst(bool on);
static bool check_busy(void);

/****************************************************************************
 * Private Data
 ****************************************************************************/

/****************************************************************************
 * Name: g_lcd_priv
 *
 * Description:
 *   Private structure for the SSD1680 LCD driver.
 *
 * Fields:
 *   set_vcc    - Function pointer to set the VCC state.
 *   set_rst    - Function pointer to set the reset pin state.
 *   check_busy - Function pointer to check the busy state of the LCD.
 ****************************************************************************/

const struct ssd1680_priv_s g_lcd_priv = {
    .set_vcc    = set_vcc,
    .set_rst    = set_rst,
    .check_busy = check_busy,
};

/****************************************************************************
 * Private Functions
 ****************************************************************************/

/****************************************************************************
 * Name: set_vcc
 *
 * Description:
 *   Set the VCC state.
 *
 * Parameters:
 *   on - Boolean indicating whether to turn VCC on or off.
 *
 * Returned Value:
 *   Always returns true.
 ****************************************************************************/

static bool set_vcc(bool on)
{
  return true;
}

/****************************************************************************
 * Name: set_rst
 *
 * Description:
 *   Set the reset pin state.
 *
 * Parameters:
 *   on - Boolean indicating whether to assert the reset pin.
 *
 * Returned Value:
 *   Always returns true.
 ****************************************************************************/

static bool set_rst(bool on)
{
  esp_gpiowrite(CONFIG_BOARD_SSD1681_RESET_IO, on);
  return true;
}

/****************************************************************************
 * Name: check_busy
 *
 * Description:
 *   Check the busy state of the LCD.
 *
 * Returned Value:
 *   Boolean indicating whether the LCD is busy.
 ****************************************************************************/

static bool check_busy(void)
{
  return esp_gpioread(CONFIG_BOARD_SSD1681_BUSY_IO);
}

/****************************************************************************
 * Public Functions
 ****************************************************************************/

/****************************************************************************
 * Name: board_lcd_getdev
 *
 * Description:
 *   Get the LCD device structure.
 *
 * Returned Value:
 *   Pointer to the LCD device structure.
 *
 ****************************************************************************/

struct lcd_dev_s *board_lcd_getdev(void)
{
  /* Configure the reset pin as an output */

  esp_configgpio(CONFIG_BOARD_SSD1681_RESET_IO, OUTPUT);

  /* Configure the busy pin as an input */

  esp_configgpio(CONFIG_BOARD_SSD1681_BUSY_IO, INPUT);

  /* Initialize the reset pin */

  esp_gpiowrite(CONFIG_BOARD_SSD1681_RESET_IO, false);
  up_mdelay(100);
  esp_gpiowrite(CONFIG_BOARD_SSD1681_RESET_IO, true);

  struct spi_dev_s *spi = esp_spibus_initialize(2);
  if (!spi)
  {
    return NULL;
  }

  return ssd1680_initialize(spi, &g_lcd_priv);
}

/****************************************************************************
 * Name: board_lcd_initialize
 *
 * Description:
 *   Initialize the LCD.
 *
 * Returned Value:
 *   Returns OK if the initialization is successful.
 ****************************************************************************/

int board_lcd_initialize(void)
{
  return OK;
}

/****************************************************************************
 * Name: board_lcd_uninitialize
 *
 * Description:
 *   Uninitialize the LCD.
 *
 * Returned Value:
 *   None.
 ****************************************************************************/

void board_lcd_uninitialize(void)
{
}
