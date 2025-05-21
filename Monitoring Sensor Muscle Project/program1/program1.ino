

long sampleTime = 0;
int samplePeriod = 20; 

// The setup routine runs once when you press reset:
void setup() {

  Serial.begin(9600); //Initialize the serial communication at 9600 bits per second



}

void loop() {

   
 /* if(Serial.available() >0){  
     int sensorValue = analogRead(A0); 
  }*/
  
  if (millis() > sampleTime) // reading accelerometer and writing on serial port
  { 
    int startTime = millis();
    sampleTime += samplePeriod;
    // Read the input data of Myoware sensor on analog Pin A0.
   
    int sensorValue = analogRead(A0); 
    // Convert the analog reading (Which goes from 0-1023) to a voltage (0V-5V)
    float voltage = sensorValue * (5.0 / 1023.0);
     // Print out the Voltage value coming from the Myoware sensor:
   
    Serial.println(voltage);
    Serial.println(sampleTime);
    
  }
   
}
  
 



 

 

  