/*
 * RobotRun -- This code demostrats a basic controller for a water based robot.
 * 
 * The configuration is assumed to be:  PC -> (wifi) -> Raspberry pi -> Ardunio -> Hardware.
 * The Raspberry Pi (pi) and the Ardunio communicate over a SPI connection.
 * 
 * This code also has a battery monitor -- and will flash a warning LED if the battery
 * voltage drops below 9.5 volts.
 * 
 * In Addition -- this program reports status to the serial port connected to the USB of 
 * the ardunio once every 5 seconds.
 * 
 * I2C Particulars
 * ---------------
 * This program response to the I2C bus like a typical device with a set of registors that
 * can be read or writen to by a master.  The ardunio is the slave.  The set of registors
 * are defined below, and are kept in the variable 'regs'.
 * 
 *   Registor Address   W/R?     Usage
 *                  0   RO  Device Signature: 'e'
 *                  1   RO  Battery Voltage (in units of 10ths of volts) 
 *                  2   RO  Device Time, Milliseconds, Byte 0, MSB
 *                  3   RO  Device Time, Milliseconds, Byte 1
 *                  4   RO  Device Time, Milliseconds, Byte 2
 *                  5   RO  Device Time, Milliseconds, Byte 3, LSB
 * 
 * ++++ Hardware setup:
 * A0 -- Analong input battery monitor
 * D2 -- Output LED for battery monitor
 * A4 -- SDA to Raspberry pi (via level shifter)
 * A5 -- SCL to Raspberry pi (via level shifter)
 * D11 -- Led to show Raspberry comm action
 * 
 */

#include <Wire.h>

int ardunio_ic2_addr = 0x8;
int bat_input_pin = A0;
int bat_monitor_pin = 2;
int pi_intr_pin = 11;

volatile long timenext;
volatile long timenow;
volatile float batvolts = 12.0;
volatile char picmd = '.';
volatile byte regs[10];
volatile int regaddr = 0;
volatile long sendcnt = 0;
volatile long reccnt = 0;
int badmsgcount = 0;

void setup() {
  pinMode(bat_monitor_pin, OUTPUT);
  pinMode(pi_intr_pin, OUTPUT);
  digitalWrite(bat_monitor_pin, HIGH);
  digitalWrite(pi_intr_pin, LOW);
  Wire.begin(ardunio_ic2_addr);
  Wire.onReceive(receivePiCmd);
  Wire.onRequest(sendPiData);
  Serial.begin(9600);
  timenext = millis() + 10;
}

// Here is the main loop function that is called by the "os".  In this implementation
// do not provide any type of delay -- the loop should take no longer than 10msec to run.
void loop() {
  timenow = millis();
  if (timenow < timenext) return;
  timenext += 10;
  monitor_battery();
  report_status();
  pi_comm();
}

void receivePiCmd(int msglen) {
  reccnt++;
  if (msglen == 1) {
    regaddr = Wire.read();
    if (regaddr < 0 || regaddr > 9) {
      badmsgcount++;
      regaddr = 0;
    }
    return;
  }
  if (msglen != 2) {
    badmsgcount++;
    return;
  }
  regaddr = Wire.read();
  int dat = Wire.read();
  if (regaddr < 0 || regaddr > 9) {
    badmsgcount++;
    return;
  }
  regs[regaddr] = dat;
}

volatile byte timesend[4];
void sendPiData() {
  sendcnt++;
  if (regaddr == 0) {Wire.write('e'); return; }
  if (regaddr == 1) {
    int i = batvolts * 10;
    Wire.write(i); 
    return;
  }
  if (regaddr == 2) {
    long ttfix = millis();
    timesend[0] = ((byte *)&ttfix)[0];
    timesend[1] = ((byte *)&ttfix)[1];
    timesend[2] = ((byte *)&ttfix)[2];
    timesend[3] = ((byte *)&ttfix)[3];
  }
  if (regaddr >= 2 && regaddr <= 5) {
    Wire.write(timesend[regaddr - 2]);
    delayMicroseconds(3);  // For some reason, this makes it work reliably.
    return;
  }
  Wire.write(regs[regaddr]);
  delayMicroseconds(3); // For some reason, this makes it work reliably.
}

int comcount = 0;
void pi_comm() {
  comcount += 1;
  if (comcount > 40) {
    comcount = 0;
  }
  if (picmd == 'r') {
    if (comcount < 20) {
      digitalWrite(pi_intr_pin, HIGH);
    } else {
      digitalWrite(pi_intr_pin, LOW);
    }  
  } else {
    digitalWrite(pi_intr_pin, LOW);
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
  if (statuscount > 500) {
    Serial.println("");
    Serial.print("Time = "); Serial.println(timenow); 
    Serial.print("Last Time Report = (");
    Serial.print(timesend[0], HEX); Serial.print(" "); Serial.print(timesend[1], HEX);
    Serial.print(" ");
    Serial.print(timesend[2], HEX); Serial.print(" "); Serial.print(timesend[3], HEX);
    Serial.println(") ");
    Serial.print("Bat Voltage = "); Serial.println(batvolts);
    Serial.print("Bad Msg Count = "); Serial.println(badmsgcount);
    Serial.print("Regs = ");
    int i;
    for (i = 0; i < 10; i++) {Serial.print(regs[i]); Serial.print(" "); }
    Serial.println("");
    statuscount = 0; 
    Serial.print("Rec, Send Counts = "); Serial.print(reccnt); 
    Serial.print(" "); Serial.println(sendcnt);
  }
}
 
