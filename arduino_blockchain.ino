#include <ArduinoJson.h>
#include "sha1.h"

SHA1 sha;
unsigned long nonce = 0;
int current_difficulty = 1;
String prev_hash = "";

void setup() {
  Serial.begin(115200);
  while (!Serial); // Ожидание подключения к Serial
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    DynamicJsonDocument doc(256);
    deserializeJson(doc, input);

    if (doc["cmd"] == "job") {
      prev_hash = doc["prev_hash"].as<String>();
      current_difficulty = doc["difficulty"];
      nonce = 0;
      mine_block();
    }
  }
}

void mine_block() {
  // Создаем строку с нулями вручную
  String target = "";
  for (int i = 0; i < current_difficulty; i++) {
    target += "0";
  }

  while (true) {
    String input = prev_hash + String(nonce);
    sha.update(input);
    String hash = sha.final();

    if (hash.startsWith(target)) {
      send_solution(nonce, hash);
      return;
    }

    nonce++;

    // Проверка новых заданий каждые 1000 попыток
    if (nonce % 1000 == 0) {
      if (check_for_new_job()) return;
    }
  }
}

bool check_for_new_job() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    DynamicJsonDocument doc(256);
    deserializeJson(doc, input);
    return doc["cmd"] == "job";
  }
  return false;
}

void send_solution(unsigned long nonce, String hash) {
  DynamicJsonDocument doc(256);
  doc["cmd"] = "solution";
  doc["nonce"] = nonce;
  doc["hash"] = hash;

  serializeJson(doc, Serial);
  Serial.println();
}