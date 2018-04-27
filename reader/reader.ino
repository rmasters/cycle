int inputPin = 2;

void setup() {
    Serial.begin(9600);
    pinMode(inputPin, INPUT);
}

int sensorValue;
float voltage;

const float thresholdVoltage = 2.5; // 5V/2

int state = LOW;

void loop() {
    // Analog reading (0-1023)
    sensorValue = analogRead(inputPin);
    // Convert to voltage (0-5V)
    voltage = sensorValue * (5.0 / 1023.0);

    // When a rising edge is detected, report 1 RPM and set state
    if (state == LOW && voltage >= thresholdVoltage) {
        reportRevolution();
        state = HIGH;
        return;
    }

    // When a falling edge is detected, reset the state machine
    if (state == HIGH && voltage < thresholdVoltage) {
        state = LOW;
    }
}

void reportRevolution() {
    Serial.println(millis());
}

/**
 * Make multiple reads to a channel and average them to remove random noise
 * Use a multiple of two for samples, as the compiler can optimise this to a bit-shift
 */
int sampleAnalog(int channel) {
    unsigned int samples = 64;
    unsigned long accumulator = 0;
    for (unsigned int i = 0; i < samples; i++) {
        accumulator += analogRead(channel);
    }
    return accumulator / samples;
}

