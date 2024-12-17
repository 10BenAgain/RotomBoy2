#define MAX_STEPS          3
#define MAX_STEP_LENGTH    8
#define BAUD_RATE          9600
#define SPACE_STEP         '+'
#define END_STEP           '?'

#include <stdint.h>
#include <string.h>

extern "C" {
  #include "src/console.h"
}

static uint64_t instructions[MAX_STEPS];
static uint16_t stepCount = 0;

static char stepBlock[MAX_STEP_LENGTH];
static uint16_t position = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  for (int i = 2; i <= 14; i++) {
    pinMode(i, OUTPUT);
  }
}

void proccessStep() {
  uint64_t stepValue = atol(stepBlock);
  if (stepCount < MAX_STEPS) {
    instructions[stepCount] = stepValue;

    Serial.print(stepCount + 1);
    Serial.print(F(", "));
    Serial.print(F("Step value: "));
    Serial.println(atol(stepBlock));
    stepCount++;
  }
  else {
    Serial.println(F("Error: Maximum step count exceeded."));
  }
  memset(stepBlock, 0, sizeof(stepBlock));
  position = 0;
}

void processInstruction(uint64_t instructions[3]) {
  switch (instructions[0]) {
    case 0:
      pressButton((uint8_t)instructions[1]);
      break;
    case 1:
      holdButton(
        (uint8_t)instructions[1],
        instructions[2]
      );
      break;
    case 2:
      pressButtonCombination(
        (uint16_t)instructions[1],
        instructions[2]
      );
      break;
    case 3:
      softResetGameNDS();
      break;
    case 4:
      rebootConsole();
      break;
    default:
      break;
  }
}

void loop() {
  if (Serial.available() > 0) {
    char inByte = Serial.read();
   
    if (inByte == END_STEP) {
      processInstruction(instructions);
      memset(instructions, 0, sizeof(instructions));
      stepCount = 0;
      Serial.println(F("Done."));
      Serial.flush();

    } else if (inByte == SPACE_STEP) {
      proccessStep();

    } else if (isDigit(inByte)) {
        if (position < MAX_STEP_LENGTH - 1) {
          stepBlock[position++] = inByte;
        } else {
          Serial.println(F("Error: Step length exceeded."));
        }
    }
    else {
       Serial.println(F("Warning: Invalid character received."));
    }
  }
}
