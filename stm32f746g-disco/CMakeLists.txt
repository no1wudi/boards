# ##############################################################################
# boards/stm32f746g-disco/CMakeLists.txt
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed to the Apache Software Foundation (ASF) under one or more contributor
# license agreements.  See the NOTICE file distributed with this work for
# additional information regarding copyright ownership.  The ASF licenses this
# file to you under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.
#
# ##############################################################################

# Delegate to in-tree board
set(BOARD_SRC_DIR ${NUTTX_DIR}/boards/arm/stm32f7/stm32f746g-disco)
set(BOARD_SCRIPT_DIR ${BOARD_SRC_DIR}/scripts)
set(BOARD_INCLUDE_DIR ${BOARD_SRC_DIR}/include)

# Create board.h symlink if not already present
if(NOT EXISTS ${CMAKE_BINARY_DIR}/include/arch/board)
  nuttx_create_symlink(${BOARD_INCLUDE_DIR} ${CMAKE_BINARY_DIR}/include/arch/board)
endif()

# Source files from in-tree board
set(SRCS
    ${BOARD_SRC_DIR}/src/stm32_boot.c
    ${BOARD_SRC_DIR}/src/stm32_spi.c
    ${BOARD_SRC_DIR}/src/stm32_bringup.c)

if(CONFIG_ARCH_LEDS)
  list(APPEND SRCS ${BOARD_SRC_DIR}/src/stm32_autoleds.c)
else()
  list(APPEND SRCS ${BOARD_SRC_DIR}/src/stm32_userleds.c)
endif()

if(CONFIG_ARCH_BUTTONS)
  list(APPEND SRCS ${BOARD_SRC_DIR}/src/stm32_buttons.c)
endif()

if(CONFIG_BOARDCTL)
  list(APPEND SRCS ${BOARD_SRC_DIR}/src/stm32_appinitialize.c)
endif()

if(CONFIG_ADC)
  list(APPEND SRCS ${BOARD_SRC_DIR}/src/stm32_adc.c)
endif()

if(CONFIG_SPORADIC_INSTRUMENTATION)
  list(APPEND SRCS ${BOARD_SRC_DIR}/src/stm32_sporadic.c)
endif()

if(CONFIG_STM32F7_LTDC)
  list(APPEND SRCS ${BOARD_SRC_DIR}/src/stm32_lcd.c)
endif()

if(CONFIG_STM32F7_FMC)
  list(APPEND SRCS ${BOARD_SRC_DIR}/src/stm32_extmem.c)
endif()

if(CONFIG_INPUT_FT5X06)
  list(APPEND SRCS ${BOARD_SRC_DIR}/src/stm32_touchscreen.c)
endif()

if(CONFIG_MTD_N25QXXX)
  list(APPEND SRCS ${BOARD_SRC_DIR}/src/stm32_n25q.c)
endif()

if(CONFIG_STM32F7_OTGFS OR CONFIG_STM32F7_OTGFSHS)
  list(APPEND SRCS ${BOARD_SRC_DIR}/src/stm32_usb.c)
endif()

if(CONFIG_STM32F7_SDMMC)
  list(APPEND SRCS ${BOARD_SRC_DIR}/src/stm32_sdmmc.c)
endif()

if(CONFIG_AUDIO_WM8994)
  list(APPEND SRCS ${BOARD_SRC_DIR}/src/stm32_wm8994.c)
endif()

target_sources(board PRIVATE ${SRCS})

# Linker script from in-tree board
set_property(GLOBAL PROPERTY LD_SCRIPT "${BOARD_SCRIPT_DIR}/flash.ld")
