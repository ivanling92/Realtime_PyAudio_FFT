void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
}
int in1, in2, in3;
void loop() {
  if (Serial.available() > 0) {
    in1 = Serial.read();
    in2 = Serial.read();
    in3 = Serial.read();
  }

  if(in1 == '1')
  {
    digitalWrite(2, HIGH);
  }
  else
  {
    digitalWrite(2, LOW);
  }
  if(in2 == '1')
  {
    digitalWrite(3, HIGH);
  }
  else
  {
    digitalWrite(3, LOW);
  }

  if(in3 == '1')
  {
    digitalWrite(4, HIGH);
  }
  else
  {
    digitalWrite(4, LOW);
  }
  delay(10);

  



}
