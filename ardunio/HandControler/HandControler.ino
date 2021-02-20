/*
 *  HandControler -- code for the hand controller that uses a Nano and a PCA9685 to
 *  control PWM devices (servos, ESC, etc).
 *  
 *  Input to the nano is:
 *  A0 -- Battery voltage (for battery monitor)
 *  A1 -- Control Pot -- voltage divider
 *  A2 -- Control Pot -- voltage divider
 */

#include <Wire.h>  // For I2C comm with the PCA9685
#include <Adafruit_PWMServoDriver.h>

#define PCA9685_ADR           0x42 
#define MIN_PULSE_WIDTH       850
#define MAX_PULSE_WIDTH       2200
#define FREQUENCY             50        

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(PCA9685_ADR);

int bat_input_pin = A0;
int pot_0_pin = A1;
int pot_1_pin = A2;
int bat_monitor_pin = 2;
float usec_per_tick = 1000000.0 / (4096.0 * FREQUENCY);

volatile long timenext;
volatile long timenow;
volatile float batvolts = 12.0;
volatile float a0_in = 0.0;
volatile float a1_in = 0.0;

void setup() {
  pinMode(bat_monitor_pin, OUTPUT);
  digitalWrite(bat_monitor_pin, HIGH);
  pwm.begin();
  pwm.setOutputMode(true);  // Use Totempole output, not open drain
  pwm.setPWMFreq(FREQUENCY);
  Serial.begin(9600);
  timenext = millis() + 10;
}

void loop() {
  timenow = millis();
  if (timenow < timenext) return;
  timenext += 10;
  monitor_input();
  monitor_battery();
  report_status();
  set_outputs();
}

void set_outputs() {
  float pw0 = a0_in * (MAX_PULSE_WIDTH - MIN_PULSE_WIDTH) + MIN_PULSE_WIDTH;
  float pw1 = a1_in * (MAX_PULSE_WIDTH - MIN_PULSE_WIDTH) + MIN_PULSE_WIDTH;
  int ticks0 = int(pw0 / usec_per_tick);
  int ticks1 = int(pw1 / usec_per_tick);
  pwm.setPWM(0, 0, ticks0);
  pwm.setPWM(1, 0, ticks1); 
}


int incount = 0;
void monitor_input() {
  incount += 1;
  if (incount > 3) {
    incount = 0;
    int ix = analogRead(pot_0_pin);
    int iy = analogRead(pot_1_pin);
    a0_in = float(ix) / 1024.0;
    a1_in = float(iy) / 1024.0;
  }
}

int batcount = 0;
int batblink = 0;
int battopcount = 10;
void monitor_battery() {
  batcount += 1;
  if (batcount >= 100) {
    batcount = 0;
    int bv = analogRead(bat_input_pin);  // Requires about .1 ms to read.
    batvolts = bv * 14.75 / 1024.0;  // Where 15.92 = Full range in volts
  }
  if (batvolts > 10.5) {
    digitalWrite(bat_monitor_pin, HIGH);
    batblink = 0;
  } else {
    if (batblink >= battopcount) batblink = 0;
    if (batblink == 0) {
      // Calculate blink rate...
      float v = batvolts - 9.0;
      if (v < 0.0) v = 0.0;
      if (v > 1.5) v = 1.5;
      battopcount = (v * 200.0) + 16;
    }
    batblink += 1;
    if (batvolts < 9.5) {
      if (batblink < 8) {
        digitalWrite(bat_monitor_pin, HIGH);
      } else {
        digitalWrite(bat_monitor_pin, LOW);
      }
    } else {
      if (batblink < 10) {
        digitalWrite(bat_monitor_pin, LOW);
      } else {
        digitalWrite(bat_monitor_pin, HIGH);
      }      
    }
  }
}

void report_status() {
  static int statuscount = 0;
  statuscount += 1;
  if (statuscount > 200) {
    Serial.println("");
    Serial.print("Time = "); Serial.println(timenow); 
    Serial.print("Bat Voltage = "); Serial.println(batvolts);
    Serial.print("Pot 0 = "); Serial.println(a0_in);
    Serial.print("Pot 1 = "); Serial.println(a1_in);
    statuscount = 0; 
  }
}
