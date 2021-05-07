#include <Arduino.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include <time.h>
#include "wifi_settings.h"

#define DEBUG 0

// Maximum number of packets to hold in the buffer. Don't changethis.
#define BUFFER_LEN 1024

// Network information
#define DHCP 1 // 0: DHCP off => set network configuration below, 1: DHCP active (auto ip)
IPAddress broadcastIp;
#if not DHCP
IPAddress ip(192, 168, 178, 46);
// Set gateway to your router's gateway
IPAddress gateway(192, 168, 178, 1);
IPAddress subnet(255, 255, 255, 0);
#endif

DynamicJsonDocument receivedServerConfigJson(2048);
DynamicJsonDocument clientParameterJson(1024);
typedef enum {
    CONNECT = 0,
    DISCONNECT = 1,
    KEEPALIVE = 2,
    ALREADY_CONNECTED = 3,
    LED_STRIP_UPDATE = 100,
    LED_STRIP_NEC_UPDATE = 101
} ServerMessageId;

typedef enum {
    CLIENT_MESSAGE_ID_CONNECT = 0,
    CLIENT_MESSAGE_ID_KEEPALIVE = 1
} ClientMessageId;

// Data output (IRsend) settings
const uint16_t PixelPin = 4;  // ESP8266 GPIO pin to use. Recommended: 4 (D2).
IRsend irsend(PixelPin, true, false);  // Set the GPIO to be used to sending the message.

// Wifi and socket settings
const int MAX_WIFI_CONNECTION_ATTEMPTS = 10;
const uint8_t clientType = 4;  // 0: LED_STRIP, 1: CONTROLLER, 2: GPIO, 4: NEC_LED_STRIP
unsigned int localPort = 7777;
unsigned int remoteBroadcastPort = 60123;
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
uint32_t nec_message;

WiFiUDP messageUdpPort;
WiFiUDP broadcastUdpPort;

bool isConnectedToServer = false;

uint32_t NEC_ON_OFF_TOGGLE = 0xFF02FD;
uint32_t NEC_RED = 0xFF1AE5;
uint32_t NEC_GREEN = 0xFF9A65;
uint32_t NEC_BLUE = 0xFFA25D;
uint32_t NEC_YELLOW = 0xFF18E7;

void wifiConnectionLoop(){
  #if not DHCP
  WiFi.config(ip, gateway, subnet);
  #endif
  // loop through available wifi credentials
  int numWifiCredentials = sizeof(ssids)/sizeof(ssids[0]);
  int i=-1;
  int iAttempt = MAX_WIFI_CONNECTION_ATTEMPTS;
  const char* ssid;
  const char* password;
  // Connect to wifi and print the IP address over serial
  while (WiFi.status() != WL_CONNECTED) {
      if(iAttempt >= MAX_WIFI_CONNECTION_ATTEMPTS){
        i = (i+1) % numWifiCredentials;
        ssid  = ssids[i];
        password  = passwords[i];
        WiFi.begin(ssid, password);
        Serial.println("\nConnecting to ssid ");
        Serial.print(ssid);
        iAttempt=0;
      }
      delay(500);
      flashPattern(NEC_RED, 2, 20);
      Serial.print(".");
      iAttempt++;
  }
  Serial.println("Connected to WIFI");
  printWifiStatus();
  broadcastIp = WiFi.localIP();
  broadcastIp[3] = 255;
}

void setup() {
  irsend.begin();
#if ESP8266
  Serial.begin(115200, SERIAL_8N1, SERIAL_TX_ONLY);
#else  // ESP8266
  Serial.begin(115200, SERIAL_8N1);
#endif  // ESP8266
  flashPattern(NEC_RED, 5, 50);
  wifiConnectionLoop();
  setupClientParameterJson();
  messageUdpPort.begin(localPort);
  broadcastUdpPort.begin(remoteBroadcastPort);
  flashPattern(NEC_BLUE, 5, 50);
}

void loop() {
  nowMS = millis();
    if(!isConnectedToServer){
        if(nowMS - lastClientBroadcastMS >= CLIENT_BROADCAST_DELAY_MS){
          int len = measureJson(clientParameterJson);
          serializeJson(clientParameterJson, broadcastMessageBuffer);
          Serial.printf("Sending clientParameterJson with length: %i\n", len);
          broadcastMessage(CLIENT_MESSAGE_ID_CONNECT, broadcastMessageBuffer, len);
          flashPattern(NEC_YELLOW, 2, 20);
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
        // read 1 byte as messageId integer
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
  Serial.printf("broadcastUDP messageId: %i to server port %i\n", messageId, remoteBroadcastPort);
  broadcastUdpPort.beginPacketMulticast(broadcastIp, remoteBroadcastPort, WiFi.localIP());
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
        case LED_STRIP_NEC_UPDATE:
            onLedStripNecUpdate(len, buffer);
            break;
        default:
            Serial.printf("Ignoring message with id: %d\n", messageId);
    }
}

void onConnectionMessage(int len, char *buffer){
    Serial.println("onConnectionMessage");
    DeserializationError error = deserializeJson(receivedServerConfigJson, buffer);
    Serial.println("Deserialized");
    if (error){
      Serial.println("jsonReceiveBuffer.parseObject(buffer) failed");
      Serial.println(buffer);
      flashPattern(NEC_RED, 10, 50);
      return;
    }
    flashPattern(NEC_GREEN, 5, 50);
    serverIp = messageUdpPort.remoteIP();
    serverPort = messageUdpPort.remotePort();
    Serial.printf("Registered at server: %s, port %d\n", serverIp.toString().c_str(), serverPort);
    isConnectedToServer = true;
}

void onDisconnectionMessage(){
    Serial.printf("Unregistered from server: %s, port %d\n", serverIp.toString().c_str(), serverPort);
    flashPattern(NEC_BLUE, 5, 50);
    isConnectedToServer = false;
}

void onKeepAliveMessage(){
    Serial.printf("Received KEEPALIVE message\n");
}

void onLedStripNecUpdate(int len, char *buffer){
    // NEC message is 4 bytes (uint32)
    nec_message = (uint32_t) buffer[0] << 24;
    nec_message |=  (uint32_t) buffer[1] << 16;
    nec_message |= (uint32_t) buffer[2] << 8;
    nec_message |= (uint32_t) buffer[3];
    #if DEBUG
    Serial.printf("Received LED Strip NEC mesage: %i\n", nec_message);
    #endif
    irsend.sendNEC(nec_message);
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

void flashPattern(uint32_t colorNecCode, int numFlashes, uint32_t delayMS){
  irsend.sendNEC(NEC_ON_OFF_TOGGLE);
  irsend.sendNEC(colorNecCode);
  delay(delayMS);
  for (int i=0; i<(numFlashes-1)*2; i++){
    irsend.sendNEC(NEC_ON_OFF_TOGGLE);
    delay(delayMS);
  }
  irsend.sendNEC(NEC_ON_OFF_TOGGLE);
}
