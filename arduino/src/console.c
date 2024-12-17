#include "console.h"

void _releaseAllButtons();
void _waitMicroseconds(uint64_t duration);
void _waitMilliseconds(uint64_t duration);

void 
pressButtonCombination(uint16_t num, uint64_t duration) {
    uint16_t mask = 1;
    for (size_t i = 0; i < 12; i++, mask <<= 1) {
        if (num & mask) {
            digitalWrite(pins[i], HIGH);
        }
    }
    _waitMicroseconds(MS_UL(duration));
    _releaseAllButtons();
}   

void
pressButton(uint8_t pin) {
  digitalWrite(pin, HIGH);
  _waitMicroseconds(MS_UL(59));
  digitalWrite(pin, LOW);
}

void
holdButton(uint8_t pin, uint64_t duration) {
    digitalWrite(pin, HIGH);
    _waitMicroseconds(MS_UL(duration));
    digitalWrite(pin, LOW);
}

void
softResetGameNDS() {
    int i, j;
    for (i = 0; i < 4; i++) {
        digitalWrite(RESET_COMBO[i], HIGH);
    }

    _waitMilliseconds(500);

    for (j = 0; j < 4; j++) {
        digitalWrite(RESET_COMBO[i], LOW);
    }
}

void
rebootConsole() {
    digitalWrite(POWER_PIN, HIGH);
    _waitMilliseconds(2500);

    digitalWrite(POWER_PIN, LOW);
    _waitMilliseconds(1000);

    digitalWrite(POWER_PIN, HIGH);
    _waitMilliseconds(2500);

    digitalWrite(POWER_PIN, LOW);
    _waitMilliseconds(1000);
}


void
_releaseAllButtons() {
    int i;
    for (i = 2; i <= 12; i++, digitalWrite(i, LOW)) {}
}

void
_waitMicroseconds(uint64_t duration) {
    uint64_t start = micros();
    while ((micros() - start) < duration) {
    }
}

void
_waitMilliseconds(uint64_t duration) {
    uint64_t start = millis();
    while ((millis() - start) < duration) {
    }
}



