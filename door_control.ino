// Pin definitions
const int relayPin = 6;
const int statusLed = 13;

// Variables for non-blocking timing
unsigned long relayActiveTime = 0;
const unsigned long relayActiveDuration = 5000; // 5 seconds
bool relayActive = false;
bool lastRelayState = false;

// Debouncing variables
unsigned long lastCommandTime = 0;
const unsigned long debounceDelay = 5000; // 5 seconds between valid commands

void setup() {
  // Initialize pins
  pinMode(relayPin, OUTPUT);
  pinMode(statusLed, OUTPUT);
  
  // Start with relay OFF (HIGH for active low relay)
  digitalWrite(relayPin, HIGH);
  digitalWrite(statusLed, LOW);
  
  // Initialize serial communication
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for serial port to connect (for Leonardo/Micro)
  }
  
  // Blink LED to indicate startup
  for (int i = 0; i < 3; i++) {
    digitalWrite(statusLed, HIGH);
    delay(200);
    digitalWrite(statusLed, LOW);
    delay(200);
  }
  
  Serial.println("System initialized. Waiting for commands...");
}

void loop() {
  // Check for incoming serial data
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // Process command only if it's 'D' and we're not in a debounce period
    if (command == 'D' && (millis() - lastCommandTime >= debounceDelay)) {
      // Activate relay (LOW for active low relay)
      digitalWrite(relayPin, LOW);
      digitalWrite(statusLed, HIGH);
      relayActive = true;
      relayActiveTime = millis();
      lastCommandTime = millis();
      
      Serial.println("Door unlocked for 5 seconds");
    }
    // Optional: Ignore other characters or handle them as needed
    else if (command != 'D') {
      Serial.print("Received unknown command: ");
      Serial.println(command);
    }
  }
  
  // Check if relay activation period has expired
  if (relayActive && (millis() - relayActiveTime >= relayActiveDuration)) {
    // Deactivate relay (HIGH for active low relay)
    digitalWrite(relayPin, HIGH);
    digitalWrite(statusLed, LOW);
    relayActive = false;
    
    Serial.println("Door locked");
  }
  
  // Optional: Add status reporting (only when state changes)
  if (relayActive != lastRelayState) {
    Serial.print("Relay state: ");
    Serial.println(relayActive ? "ACTIVE" : "INACTIVE");
    lastRelayState = relayActive;
  }
  
  // Add a small delay to prevent overwhelming the serial buffer
  delay(10);
}
