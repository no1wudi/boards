/****************************************************************************
 * boards/esp32s3/src/esp32s3_bringup.c
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

#include <debug.h>
#include <syslog.h>

#include <nuttx/fs/fs.h>
#include <arch/board/board.h>

#include "espressif/esp_gpio.h"

#ifdef CONFIG_LCD_DEV
#  include <nuttx/lcd/lcd_dev.h>
#endif

#include "esp32s3.h"

/****************************************************************************
 * Public Functions
 ****************************************************************************/

/****************************************************************************
 * Name: esp32s3_bringup
 *
 * Description:
 *   Perform architecture-specific initialization
 *
 *   CONFIG_BOARD_LATE_INITIALIZE=y :
 *     Called from board_late_initialize().
 *
 ****************************************************************************/

int esp32s3_bringup(void) {
  int ret = OK;

#ifdef CONFIG_BOARD_ESP32S3_BUZZER
  /* Keep the buzzer silent */

  esp_configgpio(CONFIG_BOARD_ESP32S3_BUZZER_PIN, OUTPUT | PULLDOWN);
  esp_gpiowrite(CONFIG_BOARD_ESP32S3_BUZZER_PIN, false);
#endif

  /* Release the touch panel controller from reset */

  esp_configgpio(CONFIG_BOARD_ESP32S3_TP_RST_PIN, OUTPUT | PULLUP);
  esp_gpiowrite(CONFIG_BOARD_ESP32S3_TP_RST_PIN, true);

#ifdef CONFIG_FS_PROCFS
  /* Mount the procfs file system */

  ret = nx_mount(NULL, "/proc", "procfs", 0, NULL);
  if (ret < 0) {
    syslog(LOG_ERR, "ERROR: Failed to mount procfs at /proc: %d\n", ret);
  }
#endif

#ifdef CONFIG_FS_TMPFS
  /* Mount the tmpfs file system */

  ret = nx_mount(NULL, CONFIG_LIBC_TMPDIR, "tmpfs", 0, NULL);
  if (ret < 0) {
    syslog(LOG_ERR, "ERROR: Failed to mount tmpfs at %s: %d\n",
           CONFIG_LIBC_TMPDIR, ret);
  }
#endif

#ifdef CONFIG_LCD
  /* Initialize the ST7789 LCD attached to SPI2 */

  ret = board_lcd_initialize();
  if (ret < 0) {
    syslog(LOG_ERR, "ERROR: Failed to initialize LCD: %d\n", ret);
  }
#endif

#ifdef CONFIG_LCD_DEV
  /* Register the LCD character driver (/dev/lcd0) */

  ret = lcddev_register(0);
  if (ret < 0) {
    syslog(LOG_ERR, "ERROR: lcddev_register() failed: %d\n", ret);
  }
#endif

  UNUSED(ret);
  return OK;
}
