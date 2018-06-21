int pin_LED  = 13;

void setup() 
{
  Serial.begin(115200);
  pinMode(pin_LED, OUTPUT);    
}
  
void loop() 
{
  delayMicroseconds(500);
}

void serialEvent()
{
  char ch;
  
  while (Serial.available()) {
    ch = (char)Serial.read();
    if(ch == '1')
      digitalWrite(pin_LED, true);
    else  
      digitalWrite(pin_LED, false);
  }
}
