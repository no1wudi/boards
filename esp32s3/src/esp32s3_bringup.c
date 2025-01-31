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

#include <errno.h>
#include <nuttx/fs/fs.h>
#include <nuttx/video/fb.h>

#include "esp32s3_gpio.h"

#ifdef CONFIG_ESP32S3_TIMER
#include "esp32s3_board_tim.h"
#endif

#ifdef CONFIG_ESP32S3_RT_TIMER
#include "esp32s3_rt_timer.h"
#endif

#ifdef CONFIG_WATCHDOG
#include "esp32s3_board_wdt.h"
#endif

#ifdef CONFIG_INPUT_BUTTONS
#include <nuttx/input/buttons.h>
#endif

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
 *   CONFIG_BOARD_LATE_INITIALIZE=n && CONFIG_BOARDCTL=y :
 *     Called from the NSH library
 *
 ****************************************************************************/

int esp32s3_bringup(void)
{
  int ret;

#ifdef CONFIG_BOARD_ESP32S3_BUZZER
  esp32s3_configgpio(CONFIG_BOARD_ESP32S3_BUZZER_PIN, OUTPUT | PULLDOWN);
  esp32s3_gpiowrite(CONFIG_BOARD_ESP32S3_BUZZER_PIN, false);
#endif

  esp32s3_configgpio(CONFIG_BOARD_ESP32S3_TP_RST_PIN, OUTPUT | PULLUP);
  esp32s3_gpiowrite(CONFIG_BOARD_ESP32S3_TP_RST_PIN, true);

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

#ifdef CONFIG_ESP32S3_TIMER
  /* Configure general purpose timers */

  ret = board_tim_init();
  if (ret < 0)
  {
    syslog(LOG_ERR, "Failed to initialize timers: %d\n", ret);
  }
#endif

#ifdef CONFIG_ESP32S3_RT_TIMER
  ret = esp32s3_rt_timer_init();
  if (ret < 0)
  {
    syslog(LOG_ERR, "Failed to initialize RT timer: %d\n", ret);
  }
#endif

#ifdef CONFIG_WATCHDOG
  /* Configure watchdog timer */

  ret = board_wdt_init();
  if (ret < 0)
  {
    syslog(LOG_ERR, "Failed to initialize watchdog timer: %d\n", ret);
  }
#endif

#ifdef CONFIG_INPUT_BUTTONS
  /* Register the BUTTON driver */

  ret = btn_lower_initialize("/dev/buttons");
  if (ret < 0)
  {
    syslog(LOG_ERR, "Failed to initialize button driver: %d\n", ret);
  }
#endif

#ifdef CONFIG_ESP32S3_SPIFLASH
  ret = board_spiflash_init();
  if (ret)
  {
    syslog(LOG_ERR, "ERROR: Failed to initialize SPI Flash\n");
  }
#endif

#if defined(CONFIG_VIDEO_FB)
  fb_register(0, 0);
#endif

  UNUSED(ret);
  return OK;
}
