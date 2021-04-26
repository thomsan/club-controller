
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

// Maximum number of packets to hold in the buffer. Don't changethis.
#define BUFFER_LEN 1024
// Toggles FPS output (1 = print FPS over serial, 0 = disable output)
#define PRINT_FPS 0

// Network information
#define DHCP 1 // 0: DHCP off => set network configuration below, 1: DHCP active (auto ip)
IPAddress broadcast(192, 168, 178, 255);
#if not DHCP
IPAddress ip(192, 168, 178, 46);
// Set gateway to your router's gateway
IPAddress gateway(192, 168, 178, 1);
IPAddress subnet(255, 255, 255, 0);
#endif

DynamicJsonDocument receivedServerConfigJson(1024);
DynamicJsonDocument clientParameterJson(1024);
typedef enum {
    CONNECT = 0,
    DISCONNECT = 1,
    KEEPALIVE = 2,
    ALREADY_CONNECTED = 3,
    LED_STRIP_UPDATE = 100
} ServerMessageId;

typedef enum {
    CLIENT_MESSAGE_ID_CONNECT = 0,
    CLIENT_MESSAGE_ID_KEEPALIVE = 1
} ClientMessageId;

//NeoPixelBus settings
const uint8_t PixelPin = 3;  // make sure to set this to the correct pin, ignored for Esp8266(set to 3 by default for DMA)

// Wifi and socket settings
const uint8_t clientType = 0;  // 0: LED_STRIP_CLIENT, 1: CONTROLLER_CLIENT
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

// Initialize the LED strip with a default pixel count of 50
// This will be overwritten, as soon as the config is received from the server
uint16_t numPixels = 50;
NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod>* strip = NULL;

WiFiUDP messageUdpPort;
WiFiUDP broadcastUdpPort;

bool isConnectedToServer = false;

RgbColor red(10,0,0);
RgbColor green(0,10,0);
RgbColor blue(0,0,10);
RgbColor yellow(10,10,0);

void initStrip(){
  if (strip != NULL) {
    delete strip;
  }
  Serial.println("deleted strip");
  strip = new NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod>(numPixels, PixelPin);
  if (strip == NULL) {
      Serial.println("Couldn't create strip. OUT OF MEMORY");
      return;
  }
  Serial.println("created strip");
  strip->Begin();
  Serial.println("started strip");
}

void setup() {
    Serial.begin(115200);

    initStrip();
    flashPattern(red, 5, 50);

    #if not DHCP
    WiFi.config(ip, gateway, subnet);
    #endif
    WiFi.begin(ssid, password);
    Serial.println("");
    // Connect to wifi and print the IP address over serial
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        flashPattern(red, 2, 20);
        Serial.print(".");
    }
    Serial.println("Connected to WIFI");
    printWifiStatus();
    setupClientParameterJson();
    messageUdpPort.begin(localPort);
    broadcastUdpPort.begin(remoteBroadcastPort);
    flashPattern(blue, 5, 50);
}

void loop() {
    nowMS = millis();
    if(!isConnectedToServer){
        if(nowMS - lastClientBroadcastMS >= CLIENT_BROADCAST_DELAY_MS){
          int len = measureJson(clientParameterJson);
          serializeJson(clientParameterJson, broadcastMessageBuffer);
          Serial.printf("Sending clientParameterJson with length: %i\n", len);
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

void setupClientParameterJson(){
    clientParameterJson["type_id"] = clientType;
    clientParameterJson["mac"] = WiFi.macAddress();
    clientParameterJson["ip"] = ipAddress2String(WiFi.localIP());
    clientParameterJson["port"] = localPort;
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
            onConnectionMessage(len, buffer);
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
              onConnectionMessage(len, buffer);
            }
            break;
        case LED_STRIP_UPDATE:
            onLedStripUpdateMessage(len, buffer);
            break;
        default:
            Serial.printf("Ignoring message with id: %d\n", messageId);
    }
}

void onConnectionMessage(int len, char *buffer){
    Serial.println("onConnectionMessage");
    DeserializationError error = deserializeJson(receivedServerConfigJson, buffer);
    Serial.println("deserialized");
    if (error){
      Serial.println("jsonReceiveBuffer.parseObject(buffer) failed");
      Serial.println(buffer);
      flashPattern(red, 10, 50);
      return;
    }
    // setup the ledstrip with the received config
    numPixels = receivedServerConfigJson["num_pixels"];
    initStrip();
    flashPattern(green, 5, 50);
    serverIp = messageUdpPort.remoteIP();
    serverPort = messageUdpPort.remotePort();
    Serial.printf("Registered at server: %s, port %d\n", serverIp.toString().c_str(), serverPort);
    isConnectedToServer = true;
}

void onDisconnectionMessage(){
    Serial.printf("Unregistered from server: %s, port %d\n", serverIp.toString().c_str(), serverPort);
    flashPattern(blue, 5, 50);
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
        strip->SetPixelColor(N, pixel);
    }
    #if DEBUG
    Serial.printf("Received LED Strip update\n");
    #endif
    strip->Show();
}

void printWifiStatus() {

  // print the SSID of the network you're attached to:

  Serial.print("SSID: ");

  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:

  IPAddress ip = WiFi.localIP();

  Serial.print("IP Address: ");

  Serial.println(ip);

  Serial.print("MAC Address: ");

  Serial.println(WiFi.macAddress());


  // print the received signal strength:

  long rssi = WiFi.RSSI();

  Serial.print("signal strength (RSSI):");

  Serial.print(rssi);

  Serial.println(" dBm");
}

void clearLedStrip(){
  RgbColor off(0,0,0);
  for(int i=0; i<numPixels; i++) {
    strip->SetPixelColor(i, off);
  }
  Serial.printf("LED Strip cleared\n");
  strip->Show();
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
    for(int i=0; i<numPixels; i++) {
      strip->SetPixelColor(i, isOn ? offColor : onColor);
    }
    strip->Show();
    while(nowMS - lastChangeMS < delayMS){
      nowMS = millis();
    }
    isOn = !isOn;
    lastChangeMS = nowMS;
  }
}
