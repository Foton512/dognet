// Подключаем стандартную библиотеку LiquidCrystal
#include <LiquidCrystal.h>
 
// Инициализируем объект-экран, передаём использованные 
// для подключения контакты на Arduino в порядке:
// RS, E, DB4, DB5, DB6, DB7
LiquidCrystal lcd(13, 11, 7, 6, 5, 4);

const int ledPin = 13;
const int redLedPin = 3;
const int greenLedPin = 2;
const int buttonPin = 8;
const int ledBacklightPin = 9;

const int blinksCount = 16;
const int blinkLength = 400;

unsigned long backlightStartTime = 0;

void setup() 
{
  lcd.begin(20, 4);
  lcd.print("Loading...");
  
  Serial.begin( 9600 );
  Serial.flush();
  pinMode(ledPin, OUTPUT);
  pinMode(redLedPin, OUTPUT);
  pinMode(greenLedPin, OUTPUT);
  pinMode(ledBacklightPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  digitalWrite(ledPin, LOW);
}

void lcd_message(char *data)
{
  int line = data[0] - '0';
  if (line < 0 || line > 3)
    line = 0;

  lcd.setCursor(0, line);
  lcd.print(data + 2);
}

unsigned long redBlinkStart = 0;
void red_blink()
{
  redBlinkStart = millis();
}

unsigned long greenBlinkStart = 0;
void green_blink()
{
  greenBlinkStart = millis();
}

void blinkCommon(unsigned long *start, int pin)
{
  if (*start != 0)
  {
    // determine state
    unsigned long diff = millis() - *start;
    int state = diff / blinkLength;

    if (state > blinksCount * 2)
    {
      // stop blinking
      *start = 0;
      digitalWrite(pin, LOW);
      return;
    }
    
    if (state % 2)
      digitalWrite(pin, HIGH); // turn on
    else
      digitalWrite(pin, LOW); // turn off
  }
}

void blinksStuff()
{
  blinkCommon(&redBlinkStart, redLedPin);
  blinkCommon(&greenBlinkStart, greenLedPin);
}

void serialStuff()
{
  char bytes[129];
  int n = 0;
  if (Serial.available())
  {
    // read length
    n = (Serial.read() - '0') * 10;
    n += Serial.read() - '0';

    while(!Serial.available())
      delay(1);

    // read data
    int r = 0;
    while (r < n)
      r += Serial.readBytes(bytes + r, n - r);

    bytes[n] = 0;

    // switch command type
    switch (bytes[0])
    {
      case '1': // display message
        if (n > 4)
          lcd_message(&bytes[2]);
        break;

      case '2': // clear display
        lcd.clear();
        break;

      case '3': // turn on backlight
        digitalWrite(ledBacklightPin, HIGH);
        backlightStartTime = millis();
        break;

      case '4': // blink with led (r or g)
        if (n == 3)
        {
          if (bytes[2] == 'r')
            red_blink();
          else if (bytes[2] == 'g')
            green_blink();
        }
        break;
        
      default:
        break;
    }
  }
}

boolean buttonWasUp = true;
const int backLightTime = 4000;
void backlightStuff()
{
  // read button state
  int buttonIsUp = digitalRead(buttonPin);
  if (buttonWasUp && !buttonIsUp)
  {
    delay(10);
    buttonIsUp = digitalRead(buttonPin);
    if (!buttonIsUp)
    {
      // it's a click, turn on backlight
      digitalWrite(ledBacklightPin, HIGH);
      backlightStartTime = millis();
    }
  }

  buttonWasUp = buttonIsUp;

  // maybe we should turn off the backlight
  if (backlightStartTime != 0)
  {
    if (millis() - backlightStartTime > backLightTime)
    {
      backlightStartTime = 0;
      digitalWrite(ledBacklightPin, LOW);
    }
  }
}
 
void loop() 
{
  // read data from serial / execute command
  serialStuff();

  // turn on / off backlight
  backlightStuff();

  // blink with leds
  blinksStuff();

  delay(20);
}
