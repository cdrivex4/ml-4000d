/** \file
 * Entry points into the firmware image.
 *
 * These are the functions that we can call from our tasks
 * in the Canon 1.1.0 firmware for the 1300d / Rebel T6.
 *
 */
/*
 * Copyright (C) 2017 Magic Lantern Team
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the
 * Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor,
 * Boston, MA  02110-1301, USA.
 */

#include <stub.h>

.text

// ROMBASE = 0xFE0C0000
// RESTARTSTART = 0x82000
// ROM->RAM START = 0xF80110CC -> 0x100000

// for task information

/** Startup **/
NSTUB( ROMBASEADDR, firmware_entry )                        // 0xFE0C0000
NSTUB(0xFE0C39A0,  cstart)                                  //
NSTUB(   0x27CE0,  bzero32)                                 // called by cstart() rom
NSTUB(    0x51E0,  create_init_task)                        // must be called from ram
NSTUB(0xFE11F1CC,  init_task)                               // passed as arg to create_init_task, look for dmSetup
NSTUB(   0x67430,  additional_version)

/** File I/O **/
NSTUB(0xFE27C670,  FIO_CloseFile)                           //
NSTUB(0xFE27D2CC,  FIO_FindClose)                           // called with ret_FIO_FindFirstEx after finishing the dir scanning loop
NSTUB(0xFE27D1EC,  FIO_FindNextEx)                          //
NSTUB(0xFE27C420, _FIO_ReadFile)                            //
NSTUB(0xFE27C4D0,  FIO_SeekSkipFile)                        // same as SeekFile
NSTUB(0xFE27C5C0, _FIO_WriteFile)                           //
NSTUB(0xFE27CE48, _FIO_CreateDirectory)                     //
NSTUB(0xFE27C2CC, _FIO_CreateFile)                          //
NSTUB(0xFE27D0F8, _FIO_FindFirstEx)                         //
NSTUB(0xFE27C708, _FIO_GetFileSize)                         //
NSTUB(0xFE27C210, _FIO_OpenFile)                            //
NSTUB(0xFE27C378, _FIO_RemoveFile)                          //
NSTUB(0xFE27CC80, _FIO_RenameFile)

/** GUI **/
NSTUB(   0x2F738,  gui_main_struct)                         // in gui_main_task
NSTUB(   0x2F76C,  gui_task_list)
NSTUB(0xFE0CC434,  GUI_ChangeMode)
NSTUB(0xFE0CC278,  GUI_Control)
NSTUB(0xFE14415C,  SetGUIRequestMode)
NSTUB(0xFE0CC8E8,  gui_init_end)                            // EndGuiInit
NSTUB(0xFE0CBEA8,  gui_main_task)                           // message at 0x30, counter at 0x0c
NSTUB(0xFE145F08,  gui_massive_event_loop)                  // GUI_Control_Post
NSTUB(0xFE0CD660,  TurnOnDisplay)                           // GUILock_TurnOnDisplay
NSTUB(0xFE0CD6D0,  TurnOffDisplay)                          // GUILock_TurnOffDisplay
NSTUB(0xFE10C340,  SetBitmapVramAddress)
NSTUB(0xFE2EB7F8,  GUI_SetLvMode)                           /* present on 500D.111, 50D.109, 5D2.212 */
// NSTUB(    ???,  GUI_SetMovieSize_a)                      /* present on 50D.109 */
// NSTUB(    ???,  GUI_SetMovieSize_b)                      /* present on 50D.109 */
// NSTUB(0xFE2EBA2C,  Gui_SetSoundRecord)                   /* present on 6D.113, 5D2.212 */

/** ASIF **/
// TODO:
 // NSTUB(0XFE108E44,  PowerAudioOutput)                       /* not found */
// NSTUB(0xFE11B938,  SetAudioVolumeOut)
NSTUB(0xFE106A98,  SetNextASIFADCBuffer)
NSTUB(0xFE106C80,  SetNextASIFDACBuffer)
NSTUB(0xFE11C690,  SetSamplingRate)
NSTUB(0xFE105F7C,  StartASIFDMAADC)
NSTUB(0xFE106350,  StartASIFDMADAC)
NSTUB(0xFE1065D0,  StopASIFDMADAC)
NSTUB(0xFE11CD04,  PowerMicAmp)                             /* present on 650D.104, EOSM.202, 700D.113 */
// NSTUB(    ???,  SetASIFMode)                             /* present on 700D.113 */
NSTUB(0xFE108E10,  SetAudioVolumeIn)                        /* present on 6D.113 */
NSTUB(0xFE108A70,  SoundDevActiveIn)                        /* present on 7D.203, 6D.113, 650D.104, EOSM.202, 700D.113 */
NSTUB(0xFE108CC8,  SoundDevShutDownIn)                      /* present on 7D.203, 6D.113, 650D.104, EOSM.202, 700D.113 */
NSTUB(0xFE106228,  StopASIFDMAADC)                          /* present on 7D.203, 6D.113, EOSM.202 */

/** Audio **/
NSTUB(    0x31604,  sounddev)                               // in sounddev_task
// TODO: Not found direct write it looks like its some kind of serial connection now
 NSTUB(0xFE284014, _audio_ic_read)
 NSTUB(0xFE2B36D4, _audio_ic_write) // posible sub_FE2B3A18
NSTUB(0xFE8C32CC,  audio_thresholds)                        // find "ALV_Initialize", then pointer to "AudioLevel", thresholds are following array of 41 values
NSTUB(0xFE108A70,  sounddev_active_in)                      // "SoundDevActiveIn"
NSTUB(0xFE108660,  sounddev_task)                           // "[SND] _SoundDeviceTask"
// NSTUB(    ???, _audio_ic_write_bulk)                     /* present on 6D.116 */

/** Bitmap **/
NSTUB(   0x51B60,  LCD_Palette)                             // in InitializeBitmapDisplayDevice, right after 0xc0f14800
NSTUB(   0x53360,  bmp_vram_info)                           // 4000D PB_BITMAP_INFO (SetBitmapVramAddress at 0xFE10C188)

/** CFN **/
NSTUB(0xFE6971B8,  GetCFnData)
NSTUB(0xFE6973E4,  SetCFnData)
// NSTUB(    ???,  GUI_GetCFnForTab4)                       /* present on 7D.203 */
// NSTUB(0xFE4716F0,  GUI_SetCFnForTab4)                    /* present on 7D.203 */

/** Camera interface? **/
// TODO:
 NSTUB(0xC0220000,  camera_engine)

/** MPU communication **/
NSTUB(0xFE2993B4, _mpu_send);                               /* dwSize < TXBD_DATA_SIZE */
NSTUB(0xFE10FA70, _mpu_recv);                               /* registered in InitializeIntercom as CBR */

/** DMA **/
NSTUB(0xFE1244E0,  dma_memcpy)

/** Debug messages **/
NSTUB(   0x300D8,  dm_names)                                // in DebugMsg, before the 1st loop target
NSTUB(0xFE1171B4,  DryosDebugMsg)                           /* 4000D verified */
NSTUB(0xFE11F6FC,  dm_set_store_level)                      // called by "dmstore"

/** Dialog API **/
NSTUB(0xFE3F0A44,  dialog_redraw)
NSTUB(0xFE2F8BF8,  dialog_set_property_str)

/** Dialog handlers **/
NSTUB(0xFE5ACCEC,  ErrCardForLVApp_handler)                 // LiveViewErrorApp, as in 60D
NSTUB(0xFE3F9A7C,  ErrForCamera_handler)                    // ERR70, ERR80 etc (DlgErrForCamera.c, AJ_DIALOG.HANDLER_DlgErrForCamera.c)
NSTUB(0xFE488590,  HideUnaviFeedBack_maybe)                 // look for StartUnaviFeedBackTimer
NSTUB(0xFE48D148,  LiveViewApp_handler)
NSTUB(0xFE48D7B4,  LiveViewApp_handler_BL_JudgeBottomInfoDispTimerState)
NSTUB(0xFE48EDF0,  LiveViewApp_handler_end)                 // start of next function
NSTUB(0xFE4A8C24,  PlayMain_handler)
NSTUB(0xFE5DDE7C,  PlayMovieGuideApp_handler)
NSTUB(0xFE49C300,  ShootOlcApp_handler)
// NSTUB(    ???,  LiveViewLevelApp_handler)                /* present on 5D3.113 */
// NSTUB(    ???,  LiveViewShutterApp_handler)              /* present on 6D.113, 650D.104, EOSM.202, 700D.113 */
NSTUB(0xFE49AA14,  LiveViewWbApp_handler)                /* present on 7D.203, 5D3.113, 5D2.212 */
// NSTUB(    ???,  LiveViewWifiApp_handler)                 /* present on 6D.113 */
// NSTUB(    ???,  StartPlayProtectGuideApp)                /* present on 7D.203, 5D2.212 */
// NSTUB(    ???,  StopPlayProtectGuideApp)                 /* present on 7D.203, 5D2.212 */

/** Display **/
NSTUB(0xFE40E9E4,  MirrorDisplay)
NSTUB(0xFE40EA44,  NormalDisplay)
NSTUB(0xFE40EA14,  ReverseDisplay)

/** EDMAC **/
NSTUB(0xFE277178,  AbortEDmac)
NSTUB(0xFE276FDC,  ConnectReadEDmac)
NSTUB(0xFE277340,  ConnectWriteEDmac)
NSTUB(0xFE2772FC,  RegisterEDmacAbortCBR)
NSTUB(0xFE2771D0,  RegisterEDmacCompleteCBR)
NSTUB(0xFE2771F8,  RegisterEDmacPopCBR)
NSTUB(0xFE276E40,  SetEDmac)
NSTUB(0xFE277130,  StartEDmac)
NSTUB(0xFE277310,  UnregisterEDmacAbortCBR)
NSTUB(0xFE2771E4,  UnregisterEDmacCompleteCBR)
NSTUB(0xFE277238,  UnregisterEDmacPopCBR)

/** Electronic Level **/
NSTUB(0xFE2EB038,  GUI_SetRollingPitchingLevelStatus)

/** Engio **/
NSTUB(0xFE2780C4, _EngDrvOut)
NSTUB(0xFE278470, _engio_write)
NSTUB(0xFE277FB4,  shamem_read)                             // AJ_0x8FB0_engio_struct_n_R0_manipulation_to_get_ptr
// NSTUB(    ???,  EngDrvOut)                               /* present on 7D_MASTER.203 */

/** Eventprocs (call by name) **/
NSTUB(0xFE117D9C,  call)

/** Events **/
NSTUB(0xFE2C2308,  TryPostEvent)                            /* present on 6D.113, 650D.104, EOSM.202, 700D.113 */
NSTUB(0xFE2C2364,  TryPostEvent_end)                        /* present on 6D.113, 650D.104, EOSM.202, 700D.113 */
NSTUB(0xFE2BE730,  TryPostStageEvent)                       /* present on 6D.113, 650D.104, EOSM.202, 700D.113 */
NSTUB(0xFE2BE78C,  TryPostStageEvent_end)                   /* present on 6D.113, 650D.104, EOSM.202, 700D.113 */

/** ExMem **/
NSTUB(0xFE122C84,  AddMemoryChunk)
NSTUB(0xFE11B038,  AllocateContinuousMemoryResource)        // m_pfContAllocMemoryCBR
NSTUB(0xFE11AFEC,  AllocateMemoryResource)                  // m_pfAllocMemoryCBR
NSTUB(0xFE119370,  CreateMemoryChunk)
NSTUB(0xFE11997C,  CreateMemorySuite)                       // FFCCEF34
NSTUB(0xFE122818,  DeleteMemorySuite)                       // FFCCED2C
NSTUB(0xFE11B150,  FreeMemoryResource)                      // m_pfFreeMemoryCBR
NSTUB(0xFE122D54,  GetFirstChunkFromSuite)                  // AJ_PackMemory_PackMem_p3
NSTUB(0xFE1227A4,  GetMemoryAddressOfMemoryChunk)           // AJ_PackMemory_PackMem.c_IsChunkSignature
NSTUB(0xFE1234E0,  GetNextMemoryChunk)
NSTUB(0xFE0D5554,  SRM_AllocateMemoryResourceFor1stJob)
NSTUB(0xFE0D7E54,  SRM_FreeMemoryResourceFor1stJob)

/** GUI for old cameras **/
NSTUB(   0x35034,  gui_timer_struct)                        // in GUI_Control_Post
NSTUB(0xFE147DA8,  gui_change_mode)                         // GUI_ChangeMode_Post
NSTUB(0xFE148588,  gui_local_post)
NSTUB(0xFE148BB0,  gui_other_post)
// NSTUB(    ???,  gui_change_lcd_state_post)               /* present on 7D.203, 500D.111, 50D.109, 5D2.212 */

NSTUB(0xFE148F98,  gui_change_shoot_type_post)              /* present on 7D.203, 500D.111, 50D.109, 5D2.212 */
NSTUB(0xFE149824,  gui_init_event)                          /* present on 7D.203, 500D.111, 50D.109, 5D2.212 */
NSTUB(0xFE14899C,  gui_post_10000085)                       /* present on 500D.111, 50D.109, 5D2.212 */
// NSTUB(    ???,  gui_timer_something)                     /* present on 7D.203, 500D.111, 50D.109, 5D2.212 */

/** GUI timers **/
NSTUB(0xFE482FE0,  CancelDateTimer)                         /* present on 7D.203, 6D.113, 5D3.113 */
NSTUB(0xFE11EB7C,  CancelTimer)
NSTUB(0xFE118638,  SetHPTimerAfterNow)
NSTUB(0xFE120DDC,  SetHPTimerNextTick)
NSTUB(0xFE11EAAC,  SetTimerAfter)

/** H264 Encoder **/
NSTUB(   0x38AC8,  mvr_config)
NSTUB(0xFE281D2C,  mvrFixQScale)
NSTUB(0xFE2817F0,  mvrSetDefQScale)
NSTUB(0xFE281838,  mvrSetFullHDOptSize)
NSTUB(0xFE281A1C,  mvrSetGopOptSizeFULLHD)

/** Interrupts **/
// NSTUB(    ???,  isr_table_handler)                       /* present on 7D_MASTER.203 */
// NSTUB(    ???,  isr_table_param)                         /* present on 7D_MASTER.203 */
NSTUB(   0x2F470,  post_isr_hook)                           /* present on 7D.203, 6D.113, 5D3.113, EOSM.202 */
NSTUB(   0x2F46C,  pre_isr_hook)                            /* present on 7D.203, 6D.113, 5D3.113, 7D_MASTER.203, EOSM.202 */

/** LCD Sensor **/
NSTUB(0xFE12BBC8,  DispSensorStart)
// NSTUB(    ???,  LightMeasure_n_Callback_r0)              /* present on 7D.203, 5D2.212 */

/** Making the card bootable **/
NSTUB(   0x499a0,  cf_device)
NSTUB(   0x499C4,  sd_device)                               // in sdReadBlk
NSTUB(0xFE543BD0,  fsuDecodePartitionTable)

/** Memory allocation **/
NSTUB(0xFE11D5B0,  GetMemoryInformation)                    // called from AllocateMemory
NSTUB(0xFE11D55C,  GetSizeOfMaxRegion)
NSTUB(0xFE11D810, _AllocateMemory)                          // "[MEM] NG AllocateMemory"
NSTUB(0xFE11DBAC, _FreeMemory)
NSTUB(0xFE28EE1C, _alloc_dma_memory)
NSTUB(0xFE2934F8, _free)
NSTUB(0xFE28EE58, _free_dma_memory)
NSTUB(0xFE2934A0, _malloc)                                  // maybe it's better to use Allocate/Free?
// NSTUB(    ???,  free_dma_memory)                         /* present on 7D_MASTER.203 */

/** Message queues **/
NSTUB(    0x7804,  msg_queue_count)
NSTUB(    0x741C,  msg_queue_create)                        // CreateMessageQueue
NSTUB(    0x77B0,  msg_queue_post)
NSTUB(    0x756C,  msg_queue_receive)

/** PTP **/
// NSTUB(0xFE36ED54,  ptp_register_handler) // 0xFE36ED54 in 4000D is ASCII string
NSTUB(0xFE1FDBE8,  ptpPropSetUILock)                        /* present on 650D.104, 700D.113 */

/** Properties **/
NSTUB(0xFE1053A0, _prop_cleanup)
NSTUB(0xFE104CA4, _prop_request_change)
NSTUB(0xFE1051F4,  prop_deliver)
NSTUB(0xFE10527C,  prop_register_slave)                     // called by"GUI_RegisterPropertySlave"
// NSTUB(    ???,  prop_unregister_slave)                   /* present on 7D.203 */

/** RPC (for 7D) **/
// NSTUB(0xFE2B8E18,  BulkInIPCTransfer)                    /* present on 7D.203 */
// NSTUB(0xFE2B8D54,  BulkOutIPCTransfer)                   /* present on 7D.203 */
// NSTUB(0xFE2B8F8C,  QuickOutIPCTransfer)                  /* present on 7D.203 */
// NSTUB(0xFE2B950C,  RegisterRPCHandler)                   /* present on 7D.203, 7D_MASTER.203 */
// NSTUB(0xFE2B95BC,  RequestRPC)                           /* present on 7D.203, 7D_MASTER.203 */

/** Recursive locks **/
NSTUB(    0xB9B8,  AcquireRecursiveLock)
NSTUB(    0xB8F8,  CreateRecursiveLock) 
NSTUB(    0xBB28,  ReleaseRecursiveLock)

/** ResLock **/
NSTUB(0xFE27AA84,  CreateResLockEntry)
NSTUB(0xFE27AD7C,  LockEngineResources)
NSTUB(0xFE27AEB4,  UnLockEngineResources)

/** Semaphores **/
NSTUB(    0x3054,  create_named_semaphore)
NSTUB(    0x32E4,  give_semaphore)
NSTUB(    0x31FC,  take_semaphore)

/** Task info **/
NSTUB(   0x33CAC,  task_max)
NSTUB(    0x24C4, _get_task_info_by_id)
NSTUB(   0x33C50,  DRYOS_ASSERT_HANDLER)
NSTUB(0xFE2C2ED0,  is_taskid_valid)                         // AJ_task_trampoline_related_p10
NSTUB(   0x2F53C,  current_task)                            /* 4000D verified */
NSTUB(     0x640,  current_interrupt)                       // in interrupt handler (0x18), where MEM(C0201004) is stored

/** Task sleep **/
NSTUB(    0x370C,  msleep)                                  // called from EV_GETDONE_CACHE param 0x64

/** Tasks **/
NSTUB(   0x33CEC,  task_dispatch_hook)  // 4000D verified at 0xFE96DC64
NSTUB(    0x3888,  task_create)                             /* 4000D verified */
NSTUB(    0x4168,  task_trampoline)
// NSTUB(    ???,  current_task_ctx)                        /* present on 7D.203 */
// NSTUB(    ???,  next_task_ctx)                           /* present on 7D.203 */

/** Misc **/
NSTUB(   0x6D418,  lv_path_struct)                          // first arg of SelectPathDriveMode
NSTUB(0xFE112F70,  LoadCalendarFromRTC)
NSTUB(0xFE292FEC,  vsprintf_canon)                          // really vsprintf(buf, fmt, ap) - NO size arg!
//NSTUB(0xFE0180A8,  _print_serial)
//NSTUB( 0xff37aee4, ChangeHDMIOutputSizeToFULLHD)
//NSTUB( 0xff37b174, ChangeHDMIOutputSizeToVGA)
NSTUB(0xFE114B20,  EnableImagePhysicalScreenParameter)      /* present on 7D.203, 50D.109, 5D2.212 */
// NSTUB(    ???,  FSUunMountDevice)                        /* present on 5D3.113 */
// NSTUB(    ???,  PtpDps_remote_release_SW1_SW2_worker)    /* present on 7D.203, 5D2.212 */
// NSTUB(    ???,  memcpy)                                  /* present on 7D_MASTER.203 */

/** Unused stubs or porting notes **/
// NSTUB( 0xFF34B724, AJ_guess_LED_OFF )
// NSTUB( 0xFF34B6F4, AJ_guess_LED_ON )   // led for SD/CF read and write ops
// NSTUB(0xFF29E25C,  AfCtrl_SetLensParameterRemote)
// NSTUB(0xFF37FAF4,  CancelBottomInfoDispTimer)
// NSTUB(0xFF234FCC,  ChangeColorPalette)
// NSTUB(0xFF31DA7C,  CreateDialogBox)
// NSTUB(0xFF31D214,  DeleteDialogBox)
// NSTUB(0xFF1E65E4,  FIO_SeekFile)
// NSTUB(0xFF23081C,  GUI_GetFirmVersion)
// NSTUB(0xFF1115DC,  GetJpegBufForLV)
// NSTUB(0xFF1115E8,  GetJpegSizeForLV)
// NSTUB(0xFF073910, GetNumberOfChunks)
// NSTUB(0xFF073580, GetRemainOfMemoryChunk)
// NSTUB(0xFF0735B0, GetSizeOfMemoryChunk)
// NSTUB(0xFF0738AC, GetSizeOfMemorySuite)
// NSTUB(0xFF378968,  HideBottomInfoDisp_maybe)                // look for StartBottomInfoDispTimer
// NSTUB(   0x3787C,  LV_EX_X)
// NSTUB(   0x37880,  LV_EX_Y)
// NSTUB(0xFF1E963C,  MuteOff_0)
// NSTUB(0xFF1E95F4,  MuteOn_0)
// NSTUB(0xFF039D4C,  PD_GetBatteryPower)
// NSTUB(0xFF0396E4,  PD_RemoteRelease)
// NSTUB(0xFF05CB28,  PROPAD_GetPropertyData)
// NSTUB(0xFF05BF04,  PROP_GetMulticastProperty)
// NSTUB(0xFF1E09F8,  PopEDmac)
// NSTUB( 0xFF1A16D0, ReadyLiveViewDevice )
// NSTUB( 0xff33a734, RedrawDisplay )
// NSTUB(0xFF14B9E4,  RemoteRelease)
NSTUB(0xFE10C188,  SetBitmapVramAddress)                    // 4000D SetBitmapVramAddress
// NSTUB(0xFF06FB60, SetHPTimerAfterTimeout)
// NSTUB( 0xFF1A1CA4, SleepLiveViewDevice )               // not found
// NSTUB(0xFF072280, _AllocateMemory_do)                       // no err70, malloc structure at 0x3070
// NSTUB(0xFF05BF04, _prop_get_value)
// NSTUB(0xFF06DFCC,  bootdisk_disable)
// NSTUB(0xFF06DFC0,  bootdisk_enable)
// NSTUB( 0xFF4F2648, cfReadBlk )
// NSTUB(0xFF010500,  cli_save)
// NSTUB(0xFF31C444,  ctrlman_dispatch_event)
// NSTUB(0xFF070F38,  delete_semaphore)
// NSTUB(0xFF1E8FE0,  dispcheck)
// NSTUB(0xFF06E690,  dm_set_print_level)
// NSTUB(0xFF06E318,  dmstart)
// NSTUB(0xFF06E358,  dmstop)
// NSTUB(0xFF06ED38,  dumpf)
// NSTUB(0xFF14B8F4,  gui_lock)                                // PtpPropSetUILock
// NSTUB(0xFF56DCCC,  gui_main_task_functbl)                   // 7 functions
// NSTUB(0xFF31C594,  gui_task_create)
// NSTUB(0xFF31C6B4,  gui_task_destroy)
// NSTUB(    0x1A7C,  hotplug_struct)
// NSTUB(0xFF01B5D8,  hotplug_task)
// NSTUB(    0x1AC8,  hotplug_usb_buf)                         // after "USB Disconnect"
// NSTUB(0xFF04E9E4,  mvrSetBitRate)
// NSTUB(0xFF1C94E0,  mvrSetDeblockingFilter)
// NSTUB(0xFF1C97FC,  mvrSetGopOptSizeHD)
// NSTUB(0xFF1C9874,  mvrSetGopOptSizeVGA)
// NSTUB(0xFF1C96E8,  mvrSetHDOptSize)
// NSTUB(0xFF1C9A94,  mvrSetPrintMovieLog)
// NSTUB(0xFF1C9730,  mvrSetVGAOptSize)
// NSTUB(0xFF06FCE4,  oneshot_timer)
// NSTUB(0xFF230E48,  prop_request_icu_auto_poweroff)          // "PROP_Request PROP_ICU_AUTO_POWEROFF(%d)"
// NSTUB(0xFF14BAC8,  ptpPropButtonSW1)
// NSTUB(0xFF14BC30,  ptpPropButtonSW2)
// NSTUB(0xFF1FAEEC,  register_func)
// NSTUB(0xFF4F838C,  sdReadBlk)
// NSTUB(0xFF010514,  sei_restore)
// NSTUB(0xFF2E1124,  vram_get_number)                         // after "[ImgPlyer]   Rate"
// NSTUB(0xFF1E7C04,  vram_get_pos_and_size)
// NSTUB(   0x75DDC,  vram_info)

/** Boot & Card I/O stubs (verified by a1ex in DMP4000D rescue log) **/
NSTUB(  0x106744,  card_bootflags)
NSTUB(  0x106F38,  boot_read_sector)
NSTUB(  0x107030,  boot_write_sector)
NSTUB(  0x101DE4,  sd_card_init)
