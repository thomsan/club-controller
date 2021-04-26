#include <time.h>
#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#define DEBUG 0

// Maximum number of packets to hold in the buffer. Don't changethis.
#define BUFFER_LEN 1024

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
    GPIO_UPDATE = 200
} ServerMessageId;

typedef enum {
    CLIENT_MESSAGE_ID_CONNECT = 0,
    CLIENT_MESSAGE_ID_KEEPALIVE = 1
} ClientMessageId;

// Wifi and socket settings
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const uint8_t clientType = 2;  // 0: LED_STRIP, 1: CONTROLLER, 2: GPIO
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

WiFiUDP messageUdpPort;
WiFiUDP broadcastUdpPort;

bool isConnectedToServer = false;
int pinModes[128];

void setup() {
    Serial.begin(115200);

    #if not DHCP
    WiFi.config(ip, gateway, subnet);
    #endif
    WiFi.begin(ssid, password);
    Serial.println("");
    // Connect to wifi and print the IP address over serial
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected to WIFI");
    printWifiStatus();
    setupClientParameterJson();
    messageUdpPort.begin(localPort);
    broadcastUdpPort.begin(remoteBroadcastPort);
}

void loop() {
    nowMS = millis();
    if(!isConnectedToServer){
        if(nowMS - lastClientBroadcastMS >= CLIENT_BROADCAST_DELAY_MS){
          int len = measureJson(clientParameterJson);
          serializeJson(clientParameterJson, broadcastMessageBuffer);
          Serial.printf("Sending clientParameterJson with length: %i\n", len);
          broadcastMessage(CLIENT_MESSAGE_ID_CONNECT, broadcastMessageBuffer, len);
          lastClientBroadcastMS = nowMS;
        }
    } else {
      if(nowMS - lastClientKeepAliveMS >= CLIENT_KEEP_ALIVE_DELAY_MS){
        #if DEBUG
        Serial.printf("Sending KEEPALIVE to %s:%i\n", serverIp.toString().c_str(), remoteBroadcastPort);
        #endif
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
        // check if actually from server ip
        lastServerMessageMS = nowMS;
    }
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
        case GPIO_UPDATE:
            onGpioUpdateMessage(len, buffer);
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
      return;
    }
    Serial.println(receivedServerConfigJson.as<String>());
    // setup the gpio modes with the received config
    for (JsonPair kv : receivedServerConfigJson.as<JsonObject>()) {
      if(kv.key() == "gpio_modes"){
        Serial.println("Got modes");
        int i = 0;
        for (JsonVariant v : kv.value().as<JsonArray>()) {
          int mode = v.as<int>();
          Serial.printf("%i,", mode);
          pinModes[i] = mode;
          if(mode == 2){
            pinMode(i, OUTPUT);
          }
          i++;
        }
      }
    }

    serverIp = messageUdpPort.remoteIP();
    serverPort = messageUdpPort.remotePort();
    Serial.printf("\nRegistered at server: %s, port %d\n", serverIp.toString().c_str(), serverPort);
    isConnectedToServer = true;
    // TODO request current values
}

void onDisconnectionMessage(){
    Serial.printf("Unregistered from server: %s, port %d\n", serverIp.toString().c_str(), serverPort);
    isConnectedToServer = false;
}

void onKeepAliveMessage(){
    #if DEBUG
    Serial.printf("Received KEEPALIVE message\n");
    #endif
}

void onGpioUpdateMessage(int len, char *buffer){
    #if DEBUG
    Serial.printf("Received GPIO update\n");
    #endif
    buffer[len]=0;
    for(int i=0; i<len; i++) {
        if(pinModes[i] == 2){ // output pin mode
          digitalWrite(i, (bool)buffer[i] ? 1 : 0);
        }
        #if DEBUG
        Serial.printf((bool)buffer[i] ? "1," : "0,");
        #endif
    }
    #if DEBUG
    Serial.println();
    #endif
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
