/* QDSpy simple digital interface
 * Notes:
 * - To make sure that the connection to the PC is as fast as possible,
 *   the BAUD rate is set to `230400`. Lower it, if the communication is
 *   not reliable
 * - If you want to test this using the Arduino IDE's serial monitor,
 *   make sure that the monitor does not add anything to your command 
 *   (non LF and/or CR)
 * - Check that the Arduino board you are using supports interrupts at  
 *   `pin_INT`; for the Nano, this is only pins 2,3
 *    
 * Function:   
 * - To signal a trigger/marker event, QDSpy sends a `1` via the serial 
 *   port; this signal can be picked up at pin `pin_LED` (usually 13)
*/

#define  pin_TRIG    13       // Trigger out pin
#define  pin_LED     12       // LED that signals interrupt detected
#define  pin_INT     2        // Interrupt pin
#define  INT_EVENT   RISING   // Event that triggers the interrupt
#define  DEBOUNCE_MS 10

String   sParam = "";
bool     LEDon = false;
unsigned long t_lastEvent_ms = 0;

void setup() 
{
  Serial.begin(230400);
  pinMode(pin_TRIG, OUTPUT);    
  pinMode(pin_LED, OUTPUT);    
  pinMode(pin_INT, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(pin_INT), triggerEvent, INT_EVENT);
  /*
  Serial.setTimeout(5000);
  Serial.println("Waiting for configuration ...");
  sParam = Serial.readStringUntil('#');
  if(sParam.length() == 0) {
    // Default 
    pinMode(pin_TRIG, OUTPUT);    
    pinMode(pin_LED, OUTPUT);    
    pinMode(pin_INT, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(pin_INT), triggerEvent, INT_EVENT);
    Serial.println("Using default pins");
  }
  else {
    //...
    Serial.println("Using user pins");
  }
  Serial.setTimeout();
  */
}

 
void loop() 
{
  delayMicroseconds(1000);
  if(LEDon and (millis() -t_lastEvent_ms > 1000)) {
    digitalWrite(pin_LED, false);
    LEDon = false;
  }
}

void triggerEvent()
{
  unsigned long t_ms = millis();
  if (t_ms -t_lastEvent_ms > DEBOUNCE_MS) {
    Serial.print('1');
    digitalWrite(pin_LED, true);
    LEDon = true;
  }
  t_lastEvent_ms = t_ms;
}

void serialEvent()
{
  char ch;
  
  while (Serial.available()) {
    ch = (char)Serial.read();
    if(ch == '1')
      digitalWrite(pin_TRIG, true);
    else  
      digitalWrite(pin_TRIG, false);
  }
}
