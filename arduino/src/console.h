#ifndef Console_h
#define Console_h

#define A_PRESS       2
#define B_PRESS       3
#define X_PRESS       4
#define Y_PRESS       5
#define LEFT_PRESS    6
#define RIGHT_PRESS   7
#define UP_PRESS      8
#define DOWN_PRESS    9
#define L_PRESS       10
#define R_PRESS       11
#define SELECT_PRESS  12

/* 
* Pin 13 seems to be tied to serial communication 
* Whenever the device is reading serial input, 
* it acts as if pin 13 is set to HIGH. This might be able to be
* avoided by turning it off while reading but skipping a pin
* is just easier. 
*/

#define START_PRESS   14
#define POWER_PIN     15

#define MAX_BUTTON    10

#define MS_UL(ms) ((ms) * 1000UL) 

#include <stdint.h>
#include <stdlib.h>
#include <Arduino.h>

static uint8_t RESET_COMBO[4] = {
  A_PRESS, 
  B_PRESS, 
  SELECT_PRESS, 
  START_PRESS
};

const uint8_t pins[] = {
  A_PRESS, 
  B_PRESS, 
  X_PRESS, 
  Y_PRESS, 
  LEFT_PRESS, 
  RIGHT_PRESS,
  UP_PRESS,
  DOWN_PRESS, 
  L_PRESS, 
  R_PRESS, 
  SELECT_PRESS, 
  START_PRESS
};

void softResetGameNDS();
void rebootConsole();

/* Presses button for 59 MS*/
void pressButton(uint8_t pin);
void holdButton(uint8_t pin, uint64_t duration);
void pressButtonCombination(uint16_t num, uint64_t duration);

#endif

