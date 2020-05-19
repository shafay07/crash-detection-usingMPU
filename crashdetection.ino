#include <Wire.h>
#include "TinyGPS++.h"
#include "SoftwareSerial.h"


SoftwareSerial gpsSerial(1, 8);
SoftwareSerial SIM900A(2, 3);
TinyGPSPlus gps;

float accelX, accelY, accelZ;                      //Accelerometer raw data
unsigned long int milli_time;                     //variable to hold the time
float g_accelX, g_accelY, g_accelZ ;                   //GForce value
float roll, pitch, yaw;
String sms = "";
bool crashStatus;

void initializeMPU6050();

void setup() {
  Serial.begin(9600);
  Serial.begin(9600);//This opens up communications to the GPS
  Wire.begin();
  initializeMPU6050();
}

void loop() {

  Wire.beginTransmission(0b1101000);   //I2C address of the MPU                   //Accelerometer and Temperature reading (check 3.register map)
  Wire.write(0x3B);                    //Starting register for Accel Readings
  Wire.endTransmission();
  Wire.requestFrom(0b1101000, 8);      //Request Accel Registers (3B - 42)
  if (Wire.available() < 8) {
    crashStatus = detectCrash();
    if (crashStatus){
      //exit(0); //equilant for haulting
      while(1); //hault the program into a forever loop
    }
  }
}

// checks the crash status and returns a boolean true/false
bool detectCrash(){
    accelX = Wire.read() << 8 | Wire.read(); //Store first two bytes into accelX
    accelY = Wire.read() << 8 | Wire.read(); //Store middle two bytes into accelY
    accelZ = Wire.read() << 8 | Wire.read(); //Store last two bytes into accelZ

    g_accelX = (accelX / 16384);   // this is for 2g.. for 8g we divide by 4096.
    g_accelY = (accelY / 16384);
    g_accelZ = (accelZ / 16384);

    pitch = 180 * atan (g_accelX / sqrt(g_accelY * g_accelY + g_accelZ * g_accelZ)) / 3.14;
    roll = 180 * atan (g_accelY / sqrt(g_accelX * g_accelX + g_accelZ * g_accelZ)) / 3.14;
    yaw = 180 * atan (g_accelZ / sqrt(g_accelX * g_accelX + g_accelZ * g_accelZ)) / 3.14;

    milli_time = millis();                                                        //Serial printing the data in CSV format
    //Serial.print(milli_time);
    Serial.print(g_accelX);
    Serial.print(",");
    Serial.print(g_accelY);
    Serial.print(",");
    Serial.print(g_accelZ);
    Serial.print('\n');

    if ((abs(g_accelX) == 2) || (abs(g_accelY) == 2) || (abs(g_accelZ) == 2)) {
      sms = "Accident Detect";
      if ( pitch < -20 || pitch > 20 || roll > 20 || roll < -20 ) {
        sms = "Accident detected with Rollover";
      }
      SendMessage();
      return true;

    }
    return false;
}


void initializeMPU6050() {
  Wire.beginTransmission(0b1101000);    //This is the I2C address of the MPU (b1101000/b1101001 for AC0 low/high datasheet sec. 9.2)
  Wire.write(0x6B);                     //Accessing the register 6B - Power Management (Sec. 4.28)
  Wire.write(0b00000000);               //Setting SLEEP register to 0. (Required; see Note on p. 9)
  Wire.endTransmission();
  Wire.beginTransmission(0b1101000);    //I2C address of the MPU
  Wire.write(0x1B);                     //Accessing the register 1B - Gyroscope Configuration (Sec. 4.4)
  Wire.write(0b00001000);               //Setting the gyro to full scale +/- 500deg./s
  Wire.endTransmission();
  Wire.beginTransmission(0b1101000);    //I2C address of the MPU
  Wire.write(0x1C);                     //Accessing the register 1C - Acccelerometer Configuration (Sec. 4.5)
  Wire.write(0b00000000);               //Setting the accel to +/- 2g
  Wire.endTransmission();
}

void SendMessage()
{
  Serial.println ("Sending Message");
  SIM900A.println("AT+CMGF=1");    //Sets the GSM Module in Text Mode
  delay(1000);
  Serial.println ("Set SMS Number");
  SIM900A.println("AT+CMGS=\"+60182755080\"\r"); //Mobile phone number to send message
  delay(1000);
  Serial.println ("Set SMS Content");
  SIM900A.println("Accident Happened At Location:\n");
  delay(100);
  SIM900A.println("Latitude:");
  SIM900A.println(gps.location.lat(), 6);
  delay(100);
  SIM900A.println("Longitude:");
  SIM900A.println(gps.location.lng(), 6);
  delay(100);
  SIM900A.println("http://www.google.com/maps/place/gps.location.lat(),gps.location.lng()");
  delay(100);
  Serial.println ("Finish");
  SIM900A.println((char)26);// ASCII code of CTRL+Z
  delay(1000);
  Serial.println ("Message has been sent");
}
