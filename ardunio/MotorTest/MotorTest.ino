#define MOTOR_IN1 10
#define MOTOR_IN2 11
#define STEPTIME 15

void setup() { 
  Serial.begin(9600);
  Serial.println("Motor Test.");
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
}

void loop() {
  Serial.println("Forward -- Speeding Up.");
  // put your main code here, to run repeatedly:
    // ramp up forward
  digitalWrite(MOTOR_IN1, LOW);
  for (int i=0; i<255; i++) {
    analogWrite(MOTOR_IN2, i);
    delay(STEPTIME);
  }
 
  // forward full speed for one second
  delay(1000);

  Serial.println("Forward -- Slowing Done.");
  // ramp down forward
  for (int i=255; i>=0; i--) {
    analogWrite(MOTOR_IN2, i);
    delay(STEPTIME);
  }
 
  // ramp up backward
  Serial.println("Reverse -- Speeding Up.");
  digitalWrite(MOTOR_IN2, LOW);
  for (int i=0; i<255; i++) {
    analogWrite(MOTOR_IN1, i);
    delay(STEPTIME);
  }
 
  // backward full speed for one second
  delay(1000);
 
  // ramp down backward
  Serial.println("Reverse -- Slowing Down.");
  for (int i=255; i>=0; i--) {
    analogWrite(MOTOR_IN1, i);
    delay(STEPTIME);
  }

  delay(1000);
}
