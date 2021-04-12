
/*
* This example works for ESP8266 and uses the NeoPixelBus library instead of the one bundle
* Sketch contributed to by Joey Babcock - https://joeybabcock.me/blog/
* Codebase created by ScottLawsonBC - https://github.com/scottlawsonbc
*/

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <NeoPixelBus.h>
#include <ArduinoJson.h>
#include <time.h>

#define DEBUG 0

// Set to the number of LEDs in your LED strip
#define NUM_LEDS 80
// Maximum number of packets to hold in the buffer. Don't changethis.
#define BUFFER_LEN 1024
// Toggles FPS output (1 = print FPS over serial, 0 = disable output)
#define PRINT_FPS 0

// Network information
#define DHCP 1 // 0: DHCP off => set network configuration below, 1: DHCP active (auto ip)
IPAddress ip(192, 168, 178, 46);
IPAddress broadcast(192, 168, 178, 255);
// Set gateway to your router's gateway
IPAddress gateway(192, 168, 178, 1);
IPAddress subnet(255, 255, 255, 0);

DynamicJsonDocument configJson(1024);
char configJsonString[BUFFER_LEN] = "{"
  "\"effect_id\": 1,"
  "\"sigma\": 1,"
  "\"color\": {"
    "\"r\": 255,"
    "\"g\": 0,"
    "\"b\": 0"
  "},"
  "\"dsp\": {"
    "\"n_rolling_history\": 2,"
    "\"n_fft_bins\": 24,"
    "\"frequency\": {"
      "\"min\": 50,"
      "\"max\": 12000"
    "},"
    "\"fps\": 30"
  "}"
"}";

typedef enum {
    CONNECT = 1,
    DISCONNECT = 2,
    KEEPALIVE = 3,
    ALREADY_CONNECTED = 4,
    LED_STRIP_UPDATE = 50
} ServerMessageId;

typedef enum {
    CLIENT_MESSAGE_ID_CONNECT = 1,
    CLIENT_MESSAGE_ID_KEEPALIVE = 3
} ClientMessageId;

//NeoPixelBus settings
const uint8_t PixelPin = 3;  // make sure to set this to the correct pin, ignored for Esp8266(set to 3 by default for DMA)

// Wifi and socket settings
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const uint8_t clientType = 1;  // 1: LED_STRIP_CLIENT, 2: CONTROLLER_CLIENT
unsigned int localPort = 7777;
unsigned int remoteBroadcastPort = 8888;
char packetBuffer[BUFFER_LEN];
char broadcastMessageBuffer[1024];
IPAddress serverIp;
uint16_t serverPort;

// timer and counter

uint32_t CLIENT_KEEP_ALIVE_DELAY_MS = 2000;
uint32_t CLIENT_BROADCAST_DELAY_MS = 5000;
uint32_t SERVER_KEEP_ALIVE_TIMEOUT_MS = 5000;
uint32_t lastClientBroadcastMS;
uint32_t lastClientKeepAliveMS;
uint32_t lastServerMessageMS;
uint32_t nowMS;

uint8_t N = 0;
#if PRINT_FPS
    uint16_t fpsCounter = 0;
    uint32_t fpsTimerMS = 0;
#endif

// LED strip
NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod> ledstrip(NUM_LEDS, PixelPin);
float sigma = 0.9f;
String color = "#ff00";

WiFiUDP messageUdpPort;
WiFiUDP broadcastUdpPort;

bool isConnectedToServer = false;

RgbColor red(10,0,0);
RgbColor green(0,10,0);
RgbColor blue(0,0,10);
RgbColor yellow(10,10,0);

void setup() {
    Serial.begin(115200);

    ledstrip.Begin();
    flashPattern(red, 5, 50);
    clearLedStrip();

    #if DHCP
    WiFi.config(ip, gateway, subnet);
    #else
    WiFi.begin(ssid, password);
    #endif
    Serial.println("");
    // Connect to wifi and print the IP address over serial
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        flashPattern(red, 2, 20);
        Serial.print(".");
    }
    Serial.println("Connected to WIFI");
    printWifiStatus();
    setupConfigJson();
    messageUdpPort.begin(localPort);
    broadcastUdpPort.begin(remoteBroadcastPort);
    flashPattern(blue, 5, 50);
    clearLedStrip();
}

void loop() {
    nowMS = millis();
    if(!isConnectedToServer){
        if(nowMS - lastClientBroadcastMS >= CLIENT_BROADCAST_DELAY_MS){
          int len = measureJson(configJson);
          serializeJson(configJson, broadcastMessageBuffer);
          Serial.printf("Sending configJson with length: %i\n", len);
          broadcastMessage(CLIENT_MESSAGE_ID_CONNECT, broadcastMessageBuffer, len);
          flashPattern(yellow, 2, 20);
          lastClientBroadcastMS = nowMS;
        }
    } else {
      if(nowMS - lastClientKeepAliveMS >= CLIENT_KEEP_ALIVE_DELAY_MS){
        Serial.printf("Sending KEEPALIVE to %s:%i\n", serverIp.toString().c_str(), remoteBroadcastPort);
        messageUdpPort.beginPacket(serverIp, remoteBroadcastPort);
        messageUdpPort.write(CLIENT_MESSAGE_ID_KEEPALIVE);
        messageUdpPort.endPacket();
        lastClientKeepAliveMS = nowMS;
      }
      if(nowMS - lastServerMessageMS >= SERVER_KEEP_ALIVE_TIMEOUT_MS){
        Serial.printf("Killing server connection server TIMEOUT\n");
        isConnectedToServer = false;
      }
    }

    // Read data over socket
    int packetSize = messageUdpPort.parsePacket();
    // If packets have been received, interpret the command
    if (packetSize) {
        #if DEBUG
        Serial.printf("Received %d bytes from %s, port %d\n", packetSize, messageUdpPort.remoteIP().toString().c_str(), messageUdpPort.remotePort());
        #endif
        int len = messageUdpPort.read(packetBuffer, BUFFER_LEN);
        #if DEBUG
        Serial.printf("Received message with len %d\n", len);
        #endif
        // read 4 bytes as messageId integer
        int messageId = packetBuffer[0];
        handleMessage(messageId, len-1, &packetBuffer[1]);
        #if PRINT_FPS
            fpsCounter++;
            Serial.print("/");//Monitors connection(shows jumps/jitters in packets)
        #endif
        // check if actually from server ip
        lastServerMessageMS = nowMS;
    }
    #if PRINT_FPS
    if (nowMS - fpsTimerMS >= 1000U) {
        fpsTimerMS = nowMS;
        Serial.printf("FPS: %d\n", fpsCounter);
        fpsCounter = 0;
    }
    #endif
}

void setupConfigJson(){
    DynamicJsonDocument ledStripParamsJson(1024);
    deserializeJson(ledStripParamsJson, configJsonString);
    ledStripParamsJson["num_pixels"] = NUM_LEDS;
    configJson["typeId"] = clientType;
    configJson["name"] = clientName;
    configJson["led_strip_params"] =  ledStripParamsJson;
    configJson["ip"] = ipAddress2String(WiFi.localIP());
    configJson["port"] = localPort;
}


void broadcastMessage(uint8_t messageId, char* messageBuffer, int len) {
  Serial.printf("broadcastUDP messageId: %i\n", messageId);

  broadcastUdpPort.beginPacketMulticast(broadcast, remoteBroadcastPort, WiFi.localIP());
  broadcastUdpPort.write(messageId);
  broadcastUdpPort.write(messageBuffer, len);
  broadcastUdpPort.endPacket();
}

String ipAddress2String(const IPAddress& ipAddress)
{
  return String(ipAddress[0]) + String(".") +\
  String(ipAddress[1]) + String(".") +\
  String(ipAddress[2]) + String(".") +\
  String(ipAddress[3])  ;
}

void handleMessage(int messageId, int len, char *buffer){
    // TODO check IP and make sure it's actually coming from the server
    #if DEBUG
    Serial.printf("Received message with Id: %d\n", messageId);
    #endif
    switch(messageId){
        case CONNECT:
            onConnectionMessage();
            break;
        case DISCONNECT:
            onDisconnectionMessage();
            break;
        case KEEPALIVE:
            onKeepAliveMessage();
            break;
        case ALREADY_CONNECTED:
            if(isConnectedToServer){
              Serial.printf("Received ALREADY_CONNECTED message, which is ignored.\n");
            } else {
              onConnectionMessage();
            }
            break;
        case LED_STRIP_UPDATE:
            onLedStripUpdateMessage(len, buffer);
            break;
        default:
            Serial.printf("Can't handle message with id: %d\n", messageId);
    }
}

void onConnectionMessage(){
    flashPattern(green, 5, 50);
    clearLedStrip();
    isConnectedToServer = true;
    serverIp = messageUdpPort.remoteIP();
    serverPort = messageUdpPort.remotePort();
    Serial.printf("Registered at server: %s, port %d\n", serverIp.toString().c_str(), serverPort);
}

void onDisconnectionMessage(){
    Serial.printf("Unregistered from server: %s, port %d\n", serverIp.toString().c_str(), serverPort);
    flashPattern(blue, 5, 50);
    clearLedStrip();
    isConnectedToServer = false;
}

void onKeepAliveMessage(){
    Serial.printf("Received KEEPALIVE message\n");
}

void onLedStripUpdateMessage(int len, char *buffer){
    for(int i=0; i<len; i+=4) {
        buffer[len]=0;
        N = buffer[i];
        RgbColor pixel((uint8_t)buffer[i+1], (uint8_t)buffer[i+2], (uint8_t)buffer[i+3]);
        ledstrip.SetPixelColor(N, pixel);
    }
    // TODO always clear the pixels which are not present in the buffer and delete below
    if(len==0){
      clearLedStrip();
    }
    #if DEBUG
    Serial.printf("Received LED Strip update\n");
    #endif
    ledstrip.Show();
}

void printWifiStatus() {

  // print the SSID of the network you're attached to:

  Serial.print("SSID: ");

  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:

  IPAddress ip = WiFi.localIP();

  Serial.print("IP Address: ");

  Serial.println(ip);

  // print the received signal strength:

  long rssi = WiFi.RSSI();

  Serial.print("signal strength (RSSI):");

  Serial.print(rssi);

  Serial.println(" dBm");
}

void clearLedStrip(){
  RgbColor off(0,0,0);
  for(int i=0; i<NUM_LEDS; i++) {
    ledstrip.SetPixelColor(i, off);
  }
  Serial.printf("LED Strip reset\n");
  ledstrip.Show();
}

void flashPattern(RgbColor onColor, int numFlashes, uint32_t delayMS){
  if(delayMS <=0){
    return;
  }
  RgbColor offColor(0,0,0);
  bool isOn = false;
  nowMS = millis();
  uint32_t lastChangeMS = nowMS;
  for (int i=0; i<numFlashes*2; i++){
    for(int i=0; i<NUM_LEDS; i++) {
      ledstrip.SetPixelColor(i, isOn ? offColor : onColor);
    }
    ledstrip.Show();
    while(nowMS - lastChangeMS < delayMS){
      nowMS = millis();
    }
    isOn = !isOn;
    lastChangeMS = nowMS;
  }
}
