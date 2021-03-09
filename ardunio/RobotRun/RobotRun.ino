/*
 * RobotRun -- This code demostrats a basic controller for a water based robot.
 * EPIC Robotz, dlb, Feb 2021
 * 
 * The configuration is assumed to be:  PC -> (wifi) -> Raspberry pi -> Ardunio -> Hardware.
 * The Raspberry Pi (pi) and the Ardunio communicate over a SPI connection.
 * 
 * This code also has a battery monitor -- and will flash a warning LED if the battery
 * voltage drops below approximately 10.5 volts.
 * 
 * In Addition -- this program reports status to the serial port connected to the USB of 
 * the ardunio once every 5 seconds.
 * 
 * Fixed Hardware Setup
 * --------------------
 * Although this code is to be used as a reference, some things probably should be left 
 * alone.  Here is the "fixed" setup:
 * 
 *    A0  -- Analong input battery monitor
 *    D2  -- Output LED for battery monitor
 *    A4  -- SDA to Raspberry pi (via level shifter)
 *    A5  -- SCL to Raspberry pi (via level shifter)
 *    D12 -- LED to show Raspberry comm action
 * 
 * I2C Particulars
 * ---------------
 * This program response to the I2C bus like a typical device with a set of registors that
 * can be read or writen to by a master.  The arduino is the slave.  The set of registors
 * are defined in a table below.  Each address has a name according to its function.
 *
 * Table of I2C Registers  
 * ----------------------
 *      Name      Addr      R/W?  Purpose/Usage
 *      --------  ----      ----  -------------   */
#define REG_SIGV     0   // RO  Device Signature/Version.  Currently: 'e'
#define REG_BAT      1   // RO  Battery Voltage (in units of 10ths of volts)
#define REG_DTME1    2   // RO  Device Time, Milliseconds, Byte 0, MSB
#define REG_DTME2    3   // RO  Device Time, Milliseconds, Byte 1
#define REG_DTME3    4   // RO  Device Time, Milliseconds, Byte 2
#define REG_DTME4    5   // RO  Device Time, Milliseconds, Byte 3, LSB
#define REG_A1       6   // RO  Voltage on pin A1, 0-255.  (Read once every 20ms)
#define REG_A2       7   // R0  Voltage on pin A2, 0-255.  (Read once every 20ms)
#define REG_A3       8   // R0  Voltage on pin A3, 0-255.  (Read once every 20ms)
#define REG_A6       9   // R0  Voltage on pin A6, 0-255.  (Read once every 20ms)
#define REG_A7      10   // R0  Voltage on pin A7, 0-255.  (Read once every 20ms)
#define REG_SI      11   // R0  Sensor Inputs, 8 bits maped as: D12, 0, D8, D7, D6, D5, D4, D3
#define REG_SC      12   // RO  Sensor Chages, 8 bits maped as: D12, 0, D8, D7, D6, D5, D4, D3
#define REG_SCC     13   // RW  Sensor Change Clear: 0=clear, 1=keep for each bit.
#define REG_PWM9    14   // RW  PWM Output on D9: 0-255
#define REG_PWM10   15   // RW  PWM Output on D10: 0-255
#define REG_PWM11   16   // RW  PWM Output on D11: 0-255
#define REG_XXX0    17   // RW  Spare 1
#define REG_XXX1    18   // RW  Spare 2
#define REG_XXX2    19   // RW  Spare 3
#define REG_LAST    19   // ** Last Registor
#define REG_RW0     13   // ** First Registor where writing is allowed.

#include <Wire.h>

int ardunio_ic2_addr = 0x8;  // Sets the address of this arduino for the RPi to access
int bat_input_pin = A0;
int bat_monitor_pin = 2;
int pi_restart_cmd_pin = 12;   // Signal from PI to restart
int pi_intr_pin = 13;         

volatile long timenext;
volatile long timenow;
volatile long timelastcomm;
volatile float batvolts = 12.0;
volatile byte regs[20];
volatile int regaddr = 0;
volatile long sendcnt = 0;
volatile long reccnt = 0;
volatile long badmsgcount = 0;

// --------------------------------------------------------------------
// setup() 
// Called on startup by the "os".
void setup() {
  pinMode(bat_monitor_pin, OUTPUT);
  pinMode(pi_intr_pin, OUTPUT);
  pinMode(3, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
  pinMode(5, INPUT_PULLUP);
  pinMode(6, INPUT_PULLUP);
  pinMode(7, INPUT_PULLUP);
  pinMode(8, INPUT_PULLUP);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(pi_restart_cmd_pin, INPUT_PULLUP);
  analogWrite(9, 0);
  analogWrite(10, 0);
  analogWrite(11, 0);
  digitalWrite(bat_monitor_pin, HIGH);
  digitalWrite(pi_intr_pin, LOW);
  Wire.begin(ardunio_ic2_addr);
  Wire.onReceive(receivePiCmd);
  Wire.onRequest(sendPiData);
  timenext = millis() + 10;
  Serial.begin(115200);
  Serial.println("");
  Serial.println("Starting UP! ");
  Serial.println("");
}

// --------------------------------------------------------------------
// loop() 
// Here is the main loop function that is repeatedly called by the "os".  Here, we use 
// a time-share approach to run each task.  This loop calls each task once every 10msec.
// This means there cannot be any "blocking", and each task must return as fast as possible.
void loop() {
  timenow = millis();
  if (timenow < timenext) return;
  timenext += 10;
  monitor_battery();
  monitor_inputs();
  report_status();
  pi_comm();
  pi_restart();
}

// --------------------------------------------------------------------
// receivePiCmd() 
// This is a callback from the I2C lib when the arduino receives data from the RPi.
void receivePiCmd(int msglen) {
  timelastcomm = millis();
  reccnt++;
  if (msglen == 1) {
    regaddr = Wire.read();
    if (regaddr < 0 || regaddr > REG_LAST) {
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
  if (regaddr < 0 || regaddr > REG_LAST) {
    badmsgcount++;
    return;
  }
  if (regaddr < REG_RW0) {
    // Trying to write into a read only reg.  Ignore this.
    return;
  }
  if (regaddr == REG_SCC) {
    // Special processing for clearing the change registor.
    regs[REG_SC] = regs[REG_SC] & dat;
  }
  if (regaddr == REG_PWM9) {
    analogWrite(9, dat);
  }
  if (regaddr == REG_PWM10) {
    analogWrite(10, dat);
  }
  if (regaddr == REG_PWM11) {
    analogWrite(11, dat);
  }
  regs[regaddr] = dat;
}

// --------------------------------------------------------------------
// pi_restart() 
// Here, we monitor the pi restart signal.  This signal is sent
// on a digital input to inform us that something is very wrong
// with the I2C bus (on our side), and we must fix it by restarting.
long tme_rst_past = 0;
void pi_restart() {
    if (digitalRead(pi_restart_cmd_pin) == LOW) {
      if (timenow - tme_rst_past > 5000) {
        tme_rst_past = timenow;
          Serial.println("*** Restart command detected from RPi,");
          Serial.println("*** (Not implimented here yet.");
      }
    }
}

// --------------------------------------------------------------------
// sendPiData()  
// This is a callback from the I2C lib when the arduino has been commanded
// by the RPi to send data back.  The register number of the data to send was
// previously communicated on a receive command, and is stored in regaddr.
volatile byte timesend[4];
void sendPiData() {
  sendcnt++;
  if (regaddr == REG_SIGV) {Wire.write('e'); return; }
  if (regaddr == REG_BAT) {
    int i = batvolts * 10;
    Wire.write(i); 
    return;
  }
  if (regaddr == REG_DTME1) {
    long ttfix = millis();
    timesend[0] = ((byte *)&ttfix)[0];
    timesend[1] = ((byte *)&ttfix)[1];
    timesend[2] = ((byte *)&ttfix)[2];
    timesend[3] = ((byte *)&ttfix)[3];
  }
  if (regaddr >= REG_DTME1 && regaddr <= REG_DTME4) {
    Wire.write(timesend[regaddr - REG_DTME1]);
    delayMicroseconds(10);  // For some reason, this makes it work reliably.
    return;
  }
  Wire.write(regs[regaddr]);
  delayMicroseconds(10); // For some reason, this makes it work reliably.
}

// --------------------------------------------------------------------
// pi_comm()
// Casues a LED to blink at a human readable rate when communication
// happens between the RPi and the Arduino.
int comcount = 0;
void pi_comm() {
  if (timenow - timelastcomm > 200) {
    digitalWrite(pi_intr_pin, LOW);
    comcount = 0;
    return;
  }
  comcount += 1;
  if (comcount > 20) {
    comcount = 0;
  }
  if (comcount < 10) {
    digitalWrite(pi_intr_pin, HIGH);
  } else {
    digitalWrite(pi_intr_pin, LOW);
  }  
}

// --------------------------------------------------------------------
// monitor_battery()
// Monitors the battery voltage and blinks a LED if the voltage falls
// below a threshold.  Increases the blinking rate as the voltage drops.
int batcount = 0;
int batblink = 0;
int battopcount = 10;
void monitor_battery() {
  batcount += 1;
  if (batcount >= 100) {
    // Read the voltage once every second...
    batcount = 0;
    int bv = analogRead(bat_input_pin);  // Requires about .1 ms to read.
    batvolts = bv * 16.0 / 1024.0;  // Where 15.92 = Full range in volts
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

// --------------------------------------------------------------------
// read_digital_inputs() 
// Reads the input pins, and assembles the IO Byte: [0, 0, D8, D7, D6, D5, D4, D3]
byte read_digital_inputs() {
  byte v = 0;
  for (int ireg = 8; ireg >= 3; ireg--) {
    if (digitalRead(ireg) == HIGH) {
      v = ((v << 1) & 0xFE) | 0x00; 
    } else {
      v = ((v << 1) & 0xFE) | 0x01;
    }
  }
  if (digitalRead(pi_restart_cmd_pin) == HIGH) v = v | 0x80;
  return v;
}

// --------------------------------------------------------------------
// monitor_inputs()
// Reads the ADC inputs onces ever 20mses.  Reads the digital inputs
// once every 10ms.  Updates the change registor for the digital inputs.
int inpcount = 0;
void monitor_inputs() {
  inpcount++;
  if (inpcount > 2) inpcount = 0;
  if (inpcount == 0) {
    regs[REG_A1] = (byte) (analogRead(A1) >> 2);
    regs[REG_A2] = (byte) (analogRead(A2) >> 2);
    regs[REG_A3] = (byte) (analogRead(A3) >> 2);
  }
  if (inpcount == 1) {
    regs[REG_A6] = (byte) (analogRead(A6) >> 2);
    regs[REG_A7] = (byte) (analogRead(A7) >> 2);
  }
  byte lastip = regs[REG_SI];
  byte curip = read_digital_inputs();
  byte changes = curip ^ lastip;
  regs[REG_SI] = curip;
  regs[REG_SC] = regs[REG_SC] | changes; 
}

// --------------------------------------------------------------------
// fmt_io() 
// Format the iobyte into on/off bits. Input string should be at least 17
// characters long.
void fmt_io(char *str, byte iobyte, char con, char coff) {
  for (int i = 0; i < 8; i++) {
    str[i*2] = ' ';
    if ((iobyte & 0x80) != 0) str[i*2 + 1] = con;
    else str[i*2 + 1] = coff;
    iobyte = iobyte << 1;
  }
  str[16] = 0;
}

// --------------------------------------------------------------------
// report_status()
// Reports the status to the monitor terminal, once every 5 secs.
// This is a debugging aid only and can be disabled for possibly 
// better performance.
void report_status() {
  static int statuscount = 0;
  char strbuf[100], buf2[30];
  statuscount += 1;
  if (statuscount > 500) {
    statuscount = 0;
    long t0 = millis();
    Serial.println("");

    sprintf(strbuf, "Time = %ld", timenow);
    Serial.println(strbuf);

    sprintf(strbuf, "Last Time Report = %02x %02x %02x %02x (hex)", timesend[0], timesend[1], timesend[2], timesend[3]);
    Serial.println(strbuf);

    Serial.print("Bat Voltage = "); Serial.println(batvolts);

    sprintf(strbuf, "ADC [1,2,3,6,7] = %3d %3d %3d %3d %3d", 
      regs[REG_A1], regs[REG_A2], regs[REG_A3], regs[REG_A6], regs[REG_A7]);
    Serial.println(strbuf);

    fmt_io(buf2, regs[REG_SI], 'T', 'F');
    sprintf(strbuf, "Digital Inputs = (x%02x) %s", regs[REG_SI], buf2);
    Serial.println(strbuf);
   
    fmt_io(buf2, regs[REG_SC], '^', ' ');
    sprintf(strbuf, "Change Bits    = (x%02x) %s", regs[REG_SC], buf2);
    Serial.println(strbuf);

    sprintf(strbuf, "PWM Outputs = %3d %3d %3d", regs[REG_PWM9], regs[REG_PWM10], regs[REG_PWM11]);
    Serial.println(strbuf);
    
    sprintf(strbuf, "Spare Regs (17-19) = %3d %3d %3d", regs[REG_XXX0], regs[REG_XXX1], regs[REG_XXX2]);
    Serial.println(strbuf);

    sprintf(strbuf, "Receive/Send counts = %ld, %ld", reccnt, sendcnt);
    Serial.println(strbuf);

    sprintf(strbuf, "Bad Message count = %ld", badmsgcount);
    Serial.println(strbuf);

    long tdelta = millis() - t0;
    sprintf(strbuf, "Status Report Time = %l msec", tdelta);
    Serial.println(tdelta);
  }
}
 
