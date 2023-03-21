/****************************************************************************
 * boards/xtensa/esp32/esp32-devkitc/src/esp32_bringup.c
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

#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <syslog.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <syslog.h>
#include <debug.h>
#include <stdio.h>

#include <arch/board/board.h>

#include <errno.h>
#if defined(CONFIG_ESP32_EFUSE)
#include <nuttx/efuse/efuse.h>
#endif
#include <nuttx/fs/fs.h>
#include <nuttx/himem/himem.h>
#include <nuttx/video/fb.h>

#if defined(CONFIG_ESP32_EFUSE)
#include "esp32_efuse.h"
#endif
#include "esp32_partition.h"

#ifdef CONFIG_USERLED
#  include <nuttx/leds/userled.h>
#endif

#ifdef CONFIG_CAN_MCP2515
#  include "esp32_mcp2515.h"
#endif

#ifdef CONFIG_TIMER
#include <esp32_tim_lowerhalf.h>
#endif

#ifdef CONFIG_ONESHOT
#  include "esp32_board_oneshot.h"
#endif

#ifdef CONFIG_WATCHDOG
#  include "esp32_board_wdt.h"
#endif

#ifdef CONFIG_ESP32_SPIFLASH
#  include "esp32_board_spiflash.h"
#endif

#ifdef CONFIG_ESP32_BLE
#  include "esp32_ble.h"
#endif

#ifdef CONFIG_ESP32_WIFI
#  include "esp32_board_wlan.h"
#endif

#ifdef CONFIG_ESP32_WIFI_BT_COEXIST
#  include "esp32_wifi_adapter.h"
#endif

#ifdef CONFIG_ESP32_I2C
#  include "esp32_board_i2c.h"
#endif

#ifdef CONFIG_ESP32_I2S
#  include "esp32_i2s.h"
#endif

#ifdef CONFIG_ESP32_PCNT_AS_QE
#  include "board_qencoder.h"
#endif

#ifdef CONFIG_I2CMULTIPLEXER_TCA9548A
#  include "esp32_tca9548a.h"
#endif

#ifdef CONFIG_SENSORS_BMP180
#  include "esp32_bmp180.h"
#endif

#ifdef CONFIG_SENSORS_BMP280
#  include "esp32_bmp280.h"
#endif

#ifdef CONFIG_SENSORS_SHT3X
#  include "esp32_sht3x.h"
#endif

#ifdef CONFIG_SENSORS_MS5611
#  include "esp32_ms5611.h"
#endif

#ifdef CONFIG_LCD_HT16K33
#  include "esp32_ht16k33.h"
#endif

#ifdef CONFIG_ESP32_AES_ACCELERATOR
#  include "esp32_aes.h"
#endif

#ifdef CONFIG_ESP32_RT_TIMER
#  include "esp32_rt_timer.h"
#endif

#ifdef CONFIG_INPUT_BUTTONS
#  include <nuttx/input/buttons.h>
#endif

#ifdef CONFIG_RTC_DRIVER
#  include "esp32_rtc_lowerhalf.h"
#endif

#ifdef CONFIG_SPI_DRIVER
#  include "esp32_spi.h"
#endif

#ifdef CONFIG_LCD_BACKPACK
#  include "esp32_lcd_backpack.h"
#endif

#ifdef CONFIG_SENSORS_MAX6675
#  include "esp32_max6675.h"
#endif

#include "esp32_gpio.h"

/****************************************************************************
 * Public Functions
 ****************************************************************************/

/****************************************************************************
 * Name: esp32_bringup
 *
 * Description:
 *   Perform architecture-specific initialization
 *
 *   CONFIG_BOARD_LATE_INITIALIZE=y :
 *     Called from board_late_initialize().
 *
 *   CONFIG_BOARD_LATE_INITIALIZE=n && CONFIG_BOARDCTL=y :
 *     Called from the NSH library
 *
 ****************************************************************************/

int esp32_bringup(void)
{
  int ret;

#ifdef CONFIG_ESP32_AES_ACCELERATOR
  ret = esp32_aes_init();
  if (ret < 0)
    {
      syslog(LOG_ERR,
             "ERROR: Failed to initialize AES: %d\n", ret);
    }
#endif

#ifdef CONFIG_FS_PROCFS
  /* Mount the procfs file system */

  ret = nx_mount(NULL, "/proc", "procfs", 0, NULL);
  if (ret < 0)
    {
      syslog(LOG_ERR, "ERROR: Failed to mount procfs at /proc: %d\n", ret);
    }
#endif


#ifdef CONFIG_FS_TMPFS
  /* Mount the tmpfs file system */

  ret = nx_mount(NULL, CONFIG_LIBC_TMPDIR, "tmpfs", 0, NULL);
  if (ret < 0)
    {
      syslog(LOG_ERR, "ERROR: Failed to mount tmpfs at %s: %d\n",
             CONFIG_LIBC_TMPDIR, ret);
    }
#endif

#ifdef CONFIG_MMCSD
  ret = esp32_mmcsd_initialize(0);
  if (ret < 0)
    {
      syslog(LOG_ERR, "Failed to initialize SD slot: %d\n", ret);
    }
#endif

#ifdef CONFIG_ESP32_RT_TIMER
  ret = esp32_rt_timer_init();
  if (ret < 0)
    {
      syslog(LOG_ERR, "Failed to initialize RT timer: %d\n", ret);
    }
#endif

#ifdef CONFIG_RTC_DRIVER
  /* Instantiate the ESP32 RTC driver */

  ret = esp32_rtc_driverinit();
  if (ret < 0)
    {
      syslog(LOG_ERR,
             "ERROR: Failed to Instantiate the RTC driver: %d\n", ret);
    }
#endif

  /* If we got here then perhaps not all initialization was successful, but
   * at least enough succeeded to bring-up NSH with perhaps reduced
   * capabilities.
   */

  fb_register(0, 0);


  esp32_gpiowrite(DISPLAY_BCKL, false);

  UNUSED(ret);
  return OK;
}
